"""Confirmatory contrasts of Section 5.1 with Holm correction and verdicts.
Usage: python analysis/test_report.py runs/judged_test_*.jsonl --cap 25 --margin 0.1 [--safemem runs/judged_safemem.jsonl]"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analysis.stats import compare, holm      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--cap", type=int, required=True)
ap.add_argument("--margin", type=float, required=True)
ap.add_argument("--safemem")
ap.add_argument("--exclude-abstention", action="store_true", help="exploratory recomputation (Section 5.6)")
a = ap.parse_args()

t = defaultdict(lambda: defaultdict(list))
for f in a.files + ([a.safemem] if a.safemem else []):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        if a.exclude_abstention and r["qid"].endswith("_abs"):
            continue
        t[(r["setting"], r["corpus"])][r["qid"]].append((r["run"], int(r["correct"])))


def scores(setting, corpus, first_run_only=False):
    out = {}
    for q, v in t[(setting, corpus)].items():
        v = sorted(v)
        out[q] = v[0][1] if first_run_only or len(v) == 1 else int(sum(x for _, x in v) * 2 > len(v))  # majority of 3
    return out


D3, D5, D2 = f"D3_{a.cap}", f"D5_{a.cap}", f"D2_{a.margin}"
contrasts = [
    ("1", "H1", "C1", "D4", "D0", ">", False),
    ("2", "H2", "C2", D5, "D4", ">", False),
    ("3", "H3", "C3", D3, D2, ">", False),
    ("4", "H4", "C0", D3, "D0", "<", False),
    ("5", "H5", "C3", "D6", D3, "<", True),     # D3* first run only (Section 5.3)
]
rows = []
for cid, h, corp, x, y, direction, first in contrasts:
    sx, sy = scores(x, corp, first), scores(y, corp, first)
    if not sx or not sy:
        rows.append({"contrast": cid, "hypothesis": h, "missing": True})
        continue
    r = compare(sx, sy)
    r.update({"contrast": cid, "hypothesis": h, "corpus": corp, "x": x, "y": y, "predicted": direction})
    rows.append(r)
ok = [r for r in rows if not r.get("missing")]
for r, s in zip(ok, holm([r["p"] for r in ok])):
    r["holm_significant"] = s
    observed = ">" if r["diff"] > 0 else "<" if r["diff"] < 0 else "="
    r["verdict"] = ("supported" if s and observed == r["predicted"] else
                    "refuted" if s and observed != r["predicted"] else "inconclusive")
print(json.dumps(rows, indent=1, default=float))
