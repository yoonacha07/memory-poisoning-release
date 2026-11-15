"""Judge answers on the cloud GPU (Sections 2.6, 4). Adds correctness and, for C1/C2, attack success. Resumable.
Usage: python scripts/run_judge.py runs/answers_dev_n3_run0.jsonl"""
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
out = src.with_name(src.name.replace("answers_", "judged_"))
qs = load_questions(a.data)
llm = Ollama(config.JUDGE_MODEL, a.host, cache_dir=config.OUT_DIR / "cache_judge")
ffs = {}
key = lambda r: (r["setting"], r["corpus"], r["qid"], r["run"])
done = done_keys(out, key)
rows = [r for r in load_jsonl(src) if key(r) not in done]
for i, r in enumerate(rows, 1):
    q = qs[r["qid"]]
    resp = "" if r.get("empty_or_cut") else r["response"]       # still empty/cut after regeneration -> incorrect
    c = verdict(llm, correctness_prompt(q, resp)) if resp else {"label": False, "missing": False, "retried": False, "raw": ""}
    rec = {**r, "correct": c["label"], "judge_missing": c["missing"], "judge_raw": c["raw"]}
    if r["corpus"] in ("C1", "C2"):
        n = r.get("n_ff", config.N_FALSE_FACTS)
        if n not in ffs:
            ffs[n] = {x["qid"]: x for x in load_jsonl(config.OUT_DIR / f"falsefacts_n{n}.jsonl")}
        W = ffs[n][r["qid"]]["W"]
        s = verdict(llm, attack_prompt(q, W, resp)) if resp else {"label": False, "missing": False, "raw": ""}
        rec.update({"attack_success": s["label"], "attack_missing": s["missing"], "attack_raw": s["raw"]})
    append(out, rec)
    if i % 200 == 0:
        print(f"{i}/{len(rows)}", flush=True)
print("done:", out)
