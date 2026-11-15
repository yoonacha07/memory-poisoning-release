"""Run SAFE-Mem (D6) and SAFE-Mem with admission off (D6') on the SAFE-Mem subset (Sections 2.5, 5.7).
Run from the repository root with the SAFE-Mem package installed (pip install -e SAFE-Mem[local]).
Resumable; each question is processed entirely on one machine, which is recorded.

  python scripts/run_safemem.py --host http://localhost:11434 [--shard 0 --shards 2] [--limit N]

Input mapping (Section 2.5): high-trust sessions -> write_dialogue(principal="user");
low-trust sessions and false-fact sentences -> write(context=...), SAFE-Mem's external-artifact path.
A low-trust session is passed in SAFE-Mem's own session format (DATE + CONVERSATION); a false fact as
"DATE: ...\\n<sentence>". Answers use SAFE-Mem's retrieval and answer prompt; judging is done later by
scripts/run_judge.py with the common judge.
"""
import argparse
import json
import os
import socket
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from mp import config                                         # noqa: E402
from mp.data import load_questions, corpus, false_fact_items, parse_date  # noqa: E402
from scripts.common import split_ids, done_keys, append, load_jsonl   # noqa: E402

import ams.memory.typed as typed                              # noqa: E402
from ams.data.locomo import QA, Session, Turn                 # noqa: E402
from ams.eval.build import build_memory                       # noqa: E402
from ams.eval.context import Config, RunContext               # noqa: E402
from ams.eval.locomo import LoCoMoQA                          # noqa: E402
from ams.llm import model_of                                  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="http://localhost:11434")
ap.add_argument("--model", default=config.ANSWER_MODEL)
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--shards", type=int, default=1)
ap.add_argument("--limit", type=int)
ap.add_argument("--n-ff", type=int, default=config.N_FALSE_FACTS)
ap.add_argument("--out")
ap.add_argument("--models-override", help="test only: one spec for every role, e.g. echo:echo-1")
ap.add_argument("--git-push-every", type=int, default=0, help="commit and push the output every N questions")
a = ap.parse_args()

# ---- fidelity counters (Section 5.7 (a)): wrap SAFE-Mem's claim parser ----------------------------
_tls = threading.local()
_orig_parse = typed._parse_claims


def _counting_parse(text, limit):
    out = _orig_parse(text, limit)
    body = (text or "").strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        data = json.loads(body)
        ok = isinstance(data, dict) and isinstance(data.get("claims"), list)
    except json.JSONDecodeError:
        ok = False
    st = getattr(_tls, "stats", None)
    if st is not None:
        st["extract_calls"] += 1
        st["parse_fail"] += (not ok)
    return out


typed._parse_claims = _counting_parse


def make_cfg(admission_on: bool):
    spec = a.models_override or f"vllm:{a.model}@{a.host.rstrip('/')}/v1"
    embed = a.models_override or "local:"
    raw = {
        "name": "safemem_ours_" + ("d6" if admission_on else "d6p"),
        "models": {"memory": spec, "agent": spec, "judge": spec, "embed": embed},
        "reasoning_effort": {model_of(spec): "none"},
        "prompts": {"extract_typed_claims": "v1", "extract_dialogue_claims": "v1", "classify_use_type": "v2",
                    "detect_conflict": "v1", "retention_sentence": "v1"},
        "memory_system": "typed",
        "memory": {"max_facts": 20},
        # v31_longmemeval_withhold.yaml; D6' changes only the three values of v31_mpbench_govoff.yaml
        "typed": {"mode": "withhold" if admission_on else "off", "hops": 0,
                  "detect_conflicts": admission_on, "endorsement": "sentence", "evidence_slots": 4,
                  "external_evidence": not admission_on},
        "locomo": {"principal": "speaker_a"},
        "retrieve_k": 4,
        "seed": 0,
    }
    return Config(raw=raw)


cfg6, cfg6p = make_cfg(True), make_cfg(False)
ctx = RunContext(cfg6, results_root=str(ROOT / "runs" / "safemem_ctx"))
mem6, mem6p = build_memory(cfg6, ctx), build_memory(cfg6p, ctx)
spec = cfg6.require("models.agent")
qa_runner = LoCoMoQA(agent=ctx.client(spec, stage="agent_answer"), agent_model=model_of(spec),
                     judge=ctx.client(spec, stage="judge"), judge_model=model_of(spec), prompts=ctx.prompts)
start = ctx.prompts.get("locomo_memory_start")

raw_data = {str(e["question_id"]): e for e in json.loads(Path(config.DATA_PATH).read_text(encoding="utf-8"))}
qs = load_questions()
ff = {r["qid"]: r for r in load_jsonl(config.OUT_DIR / f"falsefacts_n{a.n_ff}.jsonl")}
out = Path(a.out) if a.out else config.OUT_DIR / f"answers_safemem_n{a.n_ff}_{socket.gethostname()}.jsonl"
key = lambda r: (r["setting"], r["corpus"], r["qid"])
done = set()
for f in config.OUT_DIR.glob(f"answers_safemem_n{a.n_ff}_*.jsonl"):     # any machine
    done |= done_keys(f, key)

ids = split_ids("safemem")[a.shard::a.shards]
if a.limit:
    ids = ids[: a.limit]


def write_store(mem, store, q, e, c, sents):
    """Write one question's history into SAFE-Mem in date order, with the corpus's channel labels."""
    items = corpus(q, c, sents)
    if items is None:
        return None
    trust = {it.session_id: it.trust for it in items if not it.is_false_fact}
    events = []
    for sid, date, turns in zip(e["haystack_session_ids"], e["haystack_dates"], e["haystack_sessions"]):
        if turns:
            events.append((parse_date(date), 0, str(sid), date, turns))
    for it in items:
        if it.is_false_fact:
            events.append((parse_date(it.date), 1, it.item_id, it.date, it.turns[0]["content"]))
    events.sort(key=lambda x: (x[0], x[1], x[2]))
    mem.reset(store)
    zero = 0
    for _, kind, sid, date, payload in events:
        if kind == 1:
            res = mem.write(session_id=store, user_query="", context=f"DATE: {date}\n{payload}")
        elif trust.get(sid, "high") == "high":
            res = mem.write_dialogue(session_id=store, turns=[(t["role"], t["content"]) for t in payload],
                                     date=date, principal="user")
        else:
            sess = Session(index=0, date_time=date,
                           turns=tuple(Turn(dia_id=f"{sid}:{n}", speaker=t["role"], text=t["content"])
                                       for n, t in enumerate(payload)))
            res = mem.write(session_id=store, user_query="", context=sess.render())
        zero += (len(res.written) == 0) and kind == 0
    return {"sessions": sum(1 for ev in events if ev[1] == 0), "zero_claim_sessions": zero}


def answer(mem, store, q, e):
    question = f"(Today is {e['question_date']}.) {e['question']}"
    got = mem.retrieve(session_id=store, query=question, k=4, principal="user")
    body = "\n".join(f"- {x.text}" for x in got.entries) or "(nothing)"
    context = start.render(a="user", b="assistant") + "\n\n" + body
    qa = QA(qid=q.qid, question=question, answer=q.answer, category=4, evidence=tuple(q.evidence_sessions),
            kind=q.qtype)
    return qa_runner.answer(qa, context), got, body


for n, qid in enumerate(ids, 1):
    q, e = qs[qid], raw_data[qid]
    r = ff.get(qid, {})
    sents = r.get("sentences") if r.get("ok") else None
    W = (r.get("W") or "").lower()
    for c in ("C0", "C2", "C3"):
        if all(((s, c, qid) in done) for s in ("D6", "D6p")):
            continue
        for setting, mem in (("D6", mem6), ("D6p", mem6p)):
            _tls.stats = {"extract_calls": 0, "parse_fail": 0}
            store = f"{qid}|{c}|{setting}"
            info = write_store(mem, store, q, e, c, sents)
            if info is None:
                break                                   # false-fact generation failed (Section 5.5)
            pred, got, body = answer(mem, store, q, e)
            append(out, {
                "split": "safemem", "setting": setting, "corpus": c, "qid": qid, "qtype": q.qtype, "run": 0,
                "n_ff": a.n_ff, "machine": socket.gethostname(), "response": pred,
                "empty_or_cut": not pred.strip(), "required_use": got.required,
                "eligible_empty": getattr(got, "eligible_empty", None), "n_entries": len(got.entries),
                "ff_in_context": (W in body.lower()) if W else None, "context": body,
                **info, **_tls.stats})
            mem.reset(store)
    print(f"{n}/{len(ids)} {qid}", flush=True)
    if a.git_push_every and (n % a.git_push_every == 0 or n == len(ids)) and out.exists():
        import subprocess
        msg = f"SAFE-Mem progress {out.name}: {n}/{len(ids)}"
        cmd = (f'git add "{out}" && git commit -q -m "{msg}" && git pull -q --rebase --autostash && git push -q')
        r = subprocess.run(["flock", "/tmp/mp_git.lock", "bash", "-c", cmd], cwd=ROOT, capture_output=True, text=True)
        print("push ok" if r.returncode == 0 else f"PUSH FAILED: {r.stderr.strip()[-300:]}", flush=True)
print("done:", out)
