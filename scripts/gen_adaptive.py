"""Minimal adaptive attack (Section 2.7): rewrite each test false-fact sentence and keep the most question-similar
passing candidate. Run on the cloud GPU after the dev decisions are committed. Output: runs/adaptive.jsonl"""
import argparse
from common import config, split_ids, done_keys, append, load_jsonl
from mp.conditions import Embedder
from mp.data import load_questions
from mp.falsefacts import rewrite
from mp.llm import Ollama

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=config.N_FALSE_FACTS)
ap.add_argument("--host", default="http://localhost:11434")
ap.add_argument("--data", default=str(config.DATA_PATH))
a = ap.parse_args()
qs = load_questions(a.data)
ff = {r["qid"]: r for r in load_jsonl(config.OUT_DIR / f"falsefacts_n{a.n}.jsonl")}
llm = Ollama(config.JUDGE_MODEL, a.host, cache_dir=config.OUT_DIR / "cache_judge")
embed = Embedder()
out = config.OUT_DIR / "adaptive.jsonl"
done = done_keys(out, lambda r: r["qid"])
for qid in split_ids("test"):
    r = ff.get(qid)
    if qid in done or not r or not r["ok"]:
        continue
    new, logs = [], []
    for s in r["sentences"]:
        best, log = rewrite(qs[qid], r["W"], s, llm, embed)
        new.append(best); logs.append(log)
    append(out, {"qid": qid, "W": r["W"], "sentences": new, "log": logs})
print("done:", out)
