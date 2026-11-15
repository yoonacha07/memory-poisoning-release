"""Generate answers for D0-D5 / D3-0 on the laptop (Sections 2.3-2.4, 2.6). Resumable.
Usage:
  python scripts/run_answers.py --split dev --settings dev
  python scripts/run_answers.py --split test --settings D0 D1 D2_0.1 D3_25 D3_0 D4 D5_25
  python scripts/run_answers.py --split dev --settings D0 D5_25 --corpora C2 --qids-file runs/var50.txt --run 1
  python scripts/run_answers.py --split test --settings D0 D3_25 D4 D5_25 --corpora C2 --adaptive runs/adaptive.jsonl
"""
import argparse
import hashlib
from pathlib import Path

from common import config, split_ids, done_keys, append, load_jsonl
from mp.conditions import Embedder, rank, select, render, matches_pattern
from mp.data import load_questions, corpus
from mp.judging import d1_classifier
from mp.llm import Ollama

ap = argparse.ArgumentParser()
ap.add_argument("--split", required=True)
ap.add_argument("--settings", nargs="+", required=True)
ap.add_argument("--corpora", nargs="+", default=config.CORPORA)
ap.add_argument("--n-ff", type=int, default=config.N_FALSE_FACTS)
ap.add_argument("--qids-file")
ap.add_argument("--run", type=int, default=0)
ap.add_argument("--adaptive", help="JSONL of adaptive rewrites: {qid, sentences}")
ap.add_argument("--host", default="http://localhost:11434")
ap.add_argument("--out")
a = ap.parse_args()

settings = config.dev_settings() if a.settings == ["dev"] else a.settings
ids = split_ids(a.split)
if a.qids_file:
    keep = set(Path(a.qids_file).read_text().split())
    ids = [q for q in ids if q in keep]
tag = "adaptive" if a.adaptive else f"n{a.n_ff}"
out = Path(a.out) if a.out else config.OUT_DIR / f"answers_{a.split}_{tag}_run{a.run}.jsonl"

qs = load_questions()
ff = {r["qid"]: r for r in load_jsonl(config.OUT_DIR / f"falsefacts_n{a.n_ff}.jsonl")}
if a.adaptive:
    for r in load_jsonl(a.adaptive):
        ff[r["qid"]] = {**ff[r["qid"]], "sentences": r["sentences"]}
llm = Ollama(config.ANSWER_MODEL, a.host, cache_dir=config.OUT_DIR / "cache_answer")
is_instr = d1_classifier(llm)
embed = Embedder()
key = lambda r: (r["setting"], r["corpus"], r["qid"])
done = done_keys(out, key)

for n, qid in enumerate(ids, 1):
    q = qs[qid]
    sents = ff.get(qid, {}).get("sentences") if ff.get(qid, {}).get("ok") else None
    for c in a.corpora:
        items = corpus(q, c, sents)
        if items is None:
            continue                                     # false-fact generation failed (Section 5.5)
        ranked = rank(q.question, items, embed)
        for s in settings:
            if (s, c, qid) in done:
                continue
            sel = select(s, ranked, is_instr)
            prompt, cut = render(q, sel, s)
            res = llm(prompt, num_predict=config.MAX_ANSWER_TOKENS, run=a.run)
            regen = False
            if not res["text"].strip() or res.get("done_reason") == "length":   # Section 5.5: one regeneration
                regen = True
                res = llm(prompt, num_predict=config.MAX_ANSWER_TOKENS, run=a.run + 1000)
            ff_ranks = [i for i, (it, _) in enumerate(ranked) if it.is_false_fact]
            append(out, {
                "split": a.split, "setting": s, "corpus": c, "qid": qid, "qtype": q.qtype, "run": a.run,
                "n_ff": a.n_ff, "adaptive": bool(a.adaptive),
                "selected": [it.item_id for it in sel], "n_low": sum(it.trust == "low" for it in sel),
                "ff_in_context": sum(it.is_false_fact for it in sel),
                "ff_rank1": bool(ranked) and ranked[0][0].is_false_fact,
                "ff_best_rank": min(ff_ranks) if ff_ranks else None,
                "evidence_hit": any(it.is_evidence for it in sel),
                "ff_stored": (sum(not (matches_pattern(it.content) or is_instr(it.content)) for it in items if it.is_false_fact)
                              if s == "D1" else sum(it.is_false_fact for it in items)),
                "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                "prompt_tokens": res.get("prompt_tokens"), "output_tokens": res.get("output_tokens"),
                "truncated": cut or (res.get("prompt_tokens") or 0) >= config.NUM_CTX - config.MAX_ANSWER_TOKENS,
                "regenerated": regen, "empty_or_cut": (not res["text"].strip()) or res.get("done_reason") == "length",
                "response": res["text"]})
    print(f"{n}/{len(ids)} {qid}", flush=True)
print("done:", out)
