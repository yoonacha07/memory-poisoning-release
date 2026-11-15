"""Generate false facts for every question with the judge model (Section 2.3). Run on the cloud GPU.
Usage: python scripts/gen_falsefacts.py --n 3 [--host http://localhost:11434] [--data path]"""
import argparse
from common import config, split_ids, done_keys, append
from mp.data import load_questions
from mp.falsefacts import generate
from mp.llm import Ollama

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=config.N_FALSE_FACTS)
ap.add_argument("--host", default="http://localhost:11434")
ap.add_argument("--data", default=str(config.DATA_PATH))
ap.add_argument("--retry-failed", action="store_true", help="regenerate only questions whose earlier generation failed")
a = ap.parse_args()

out = config.OUT_DIR / f"falsefacts_n{a.n}.jsonl"
qs = load_questions(a.data)
llm = Ollama(config.JUDGE_MODEL, a.host, cache_dir=config.OUT_DIR / "cache_judge")
if a.retry_failed and out.exists():
    import json
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    keep = [r for r in rows if r["ok"]]
    (config.OUT_DIR / f"falsefacts_n{a.n}_failed_before_retry.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows if not r["ok"]), encoding="utf-8")
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep), encoding="utf-8")
    print(f"retrying {len(rows) - len(keep)} failed questions")
done = done_keys(out, lambda r: r["qid"])
ids = [q for q in split_ids("all") if q not in done]
for i, qid in enumerate(ids, 1):
    append(out, generate(qs[qid], llm, n=a.n))
    if i % 25 == 0:
        print(f"{i}/{len(ids)}", flush=True)
print("done:", out)
