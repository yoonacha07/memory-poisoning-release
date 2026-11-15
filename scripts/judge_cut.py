"""EXPLORATORY (not preregistered; plan fixed in docs/exploratory_truncation_plan.md before any test answer was judged).
Re-judges answers that hit the 256-token limit (empty_or_cut) on their truncated text as-is, with the same judge model
and the same correctness and attack prompts as run_judge.py. The confirmatory files are not modified.
Usage: python scripts/judge_cut.py runs/answers_test_n3_run0.jsonl [--host http://localhost:11434]
Output: runs/judged_cut_<name>.jsonl (only rows with empty_or_cut and a non-empty response). Resumable."""
import argparse
from pathlib import Path

from common import config, done_keys, append, load_jsonl
from mp.data import load_questions
from mp.judging import correctness_prompt, attack_prompt, verdict
from mp.llm import Ollama

ap = argparse.ArgumentParser()
ap.add_argument("answers")
ap.add_argument("--host", default="http://localhost:11434")
ap.add_argument("--data", default=str(config.DATA_PATH))
a = ap.parse_args()

src = Path(a.answers)
out = src.with_name(src.name.replace("answers_", "judged_cut_"))
qs = load_questions(a.data)
llm = Ollama(config.JUDGE_MODEL, a.host, cache_dir=config.OUT_DIR / "cache_judge")
ffs = {}
key = lambda r: (r["setting"], r["corpus"], r["qid"], r["run"])
done = done_keys(out, key)
rows = [r for r in load_jsonl(src) if r.get("empty_or_cut") and (r.get("response") or "").strip() and key(r) not in done]
print("cut rows to judge:", len(rows), flush=True)
for i, r in enumerate(rows, 1):
    q = qs[r["qid"]]
    resp = r["response"]
    c = verdict(llm, correctness_prompt(q, resp))
    rec = {k: r[k] for k in ("setting", "corpus", "qid", "run")}
    rec.update({"correct_cut": c["label"], "judge_missing_cut": c["missing"], "judge_raw_cut": c["raw"]})
    if r["corpus"] in ("C1", "C2"):
        n = r.get("n_ff", config.N_FALSE_FACTS)
        if n not in ffs:
            ffs[n] = {x["qid"]: x for x in load_jsonl(config.OUT_DIR / f"falsefacts_n{n}.jsonl")}
        s = verdict(llm, attack_prompt(q, ffs[n][r["qid"]]["W"], resp))
        rec.update({"attack_cut": s["label"], "attack_missing_cut": s["missing"], "attack_raw_cut": s["raw"]})
    append(out, rec)
    if i % 100 == 0:
        print(f"{i}/{len(rows)}", flush=True)
print("done:", out)
