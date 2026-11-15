"""Run-to-run check of Section 5.3. Usage: python analysis/variance.py runs/judged_dev_n3_run0.jsonl runs/judged_dev_var_run1.jsonl runs/judged_dev_var_run2.jsonl --cap 25"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--cap", type=int, required=True)
a = ap.parse_args()
keep = set(Path("runs/var50.txt").read_text().split())
settings = {"D0", f"D5_{a.cap}"}
res = defaultdict(set)
for f in a.files:
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        if r["qid"] in keep and r["setting"] in settings and r["corpus"] == "C2":
            res[(r["qid"], r["setting"])].add(int(r["correct"]))
pairs = len(res)
changed = sum(1 for v in res.values() if len(v) > 1)
rate = changed / pairs if pairs else float("nan")
print(json.dumps({"pairs": pairs, "changed": changed, "rate": rate, "triple_runs_needed": rate > 0.05}, indent=1))
