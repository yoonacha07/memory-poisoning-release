"""Paper tables and the trade-off figure from judged test files (descriptive; the confirmatory contrasts come from
test_report.py). Uses the same per-question scoring rule as test_report.py: first run if one run, majority of 3 if three.

Usage:
  python analysis/test_report.py runs/judged_test_n3_run0.jsonl --cap 25 --margin 0.1 --safemem runs/judged_safemem.jsonl > runs/test_report.json
  python analysis/make_figures.py runs/judged_test_n3_run0.jsonl --cap 25 --margin 0.1 \
      --safemem runs/judged_safemem.jsonl --adaptive runs/judged_test_adaptive_run0.jsonl --report runs/test_report.json
Outputs (results/): accuracy_table.tex, asr_table.tex, contrasts_table.tex, tradeoff.pdf, summary.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analysis.stats import wilson  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--cap", type=int, required=True)
ap.add_argument("--margin", type=float, required=True)
ap.add_argument("--safemem")
ap.add_argument("--adaptive")
ap.add_argument("--report", help="JSON printed by test_report.py")
ap.add_argument("--out", default="results")
a = ap.parse_args()
out = Path(a.out)
out.mkdir(exist_ok=True)

CORPORA = ["C0", "C1", "C2", "C3"]
ORDER = [("D0", "D0"), ("D1", "D1"), (f"D2_{a.margin}", "D2*"), (f"D3_{a.cap}", "D3*"), ("D3_0", "D3-0"),
         ("D4", "D4"), (f"D5_{a.cap}", "D5*"), ("D6", "D6"), ("D6p", "D6$'$")]
SUBSET = {"D6", "D6p"}          # SAFE-Mem runs on the 120-question subset
# label positions (points) for the crowded cluster near (55-62, 21-26); tuned on the test results, labels only
LABEL_OFFSET = {"D0": (10, -3), "D1": (4, -16), "D2*": (8, 9), "D3*": (-8, -17), "D4": (-6, 12), "D5*": (-18, 8)}


def load(paths):
    t = defaultdict(lambda: defaultdict(list))
    for p in paths:
        for line in open(p, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                t[(r["setting"], r["corpus"])][r["qid"]].append(
                    (r["run"], int(r["correct"]), int(r["attack_success"]) if r.get("attack_success") is not None else None))
    return t


def per_question(cell, idx):
    res = {}
    for q, v in cell.items():
        v = sorted(v)
        vals = [x[idx] for x in v if x[idx] is not None]
        if not vals:
            continue
        res[q] = vals[0] if len(vals) == 1 else int(sum(vals) * 2 > len(vals))
    return res


def rate(cell, idx):
    s = per_question(cell, idx)
    n, k = len(s), sum(s.values())
    if n == 0:
        return None
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "p": k / n, "lo": lo, "hi": hi}


def fmt(x):
    if x is None:
        return "--"
    return f"{100 * x['p']:.1f} \\scriptsize{{[{100 * x['lo']:.0f}, {100 * x['hi']:.0f}]}}"


t = load(a.files + ([a.safemem] if a.safemem else []))
summary = {}

# 1) accuracy table
lines = [r"\begin{tabular}{@{}l" + "c" * len(CORPORA) + "@{}}", r"\toprule",
         "Condition & " + " & ".join(CORPORA) + r" \\", r"\midrule"]
for key, label in ORDER:
    cells = {c: rate(t[(key, c)], 1) for c in CORPORA}
    if all(v is None for v in cells.values()):
        continue
    summary[label] = {c: v for c, v in cells.items() if v}
    mark = r"$^\dagger$" if key in SUBSET else ""
    lines.append(f"{label}{mark} & " + " & ".join(fmt(cells[c]) for c in CORPORA) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}"]
(out / "accuracy_table.tex").write_text("\n".join(lines) + "\n")

# 2) attack success table (C1, C2, and adaptive C2 if given)
ad = load([a.adaptive]) if a.adaptive else {}
cols = ["C1", "C2"] + (["C2 adaptive"] if a.adaptive else [])
lines = [r"\begin{tabular}{@{}l" + "c" * len(cols) + "@{}}", r"\toprule",
         "Condition & " + " & ".join(cols) + r" \\", r"\midrule"]
for key, label in ORDER:
    cells = [rate(t[(key, "C1")], 2), rate(t[(key, "C2")], 2)]
    if a.adaptive:
        cells.append(rate(ad[(key, "C2")], 2) if (key, "C2") in ad else None)
    if all(v is None for v in cells):
        continue
    summary.setdefault(label, {})["ASR"] = dict(zip(cols, cells))
    mark = r"$^\dagger$" if key in SUBSET else ""
    lines.append(f"{label}{mark} & " + " & ".join(fmt(v) for v in cells) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}"]
(out / "asr_table.tex").write_text("\n".join(lines) + "\n")

# 3) contrasts table from test_report.py
if a.report:
    rep = json.load(open(a.report, encoding="utf-8"))
    names = dict(ORDER)
    lines = [r"\begin{tabular}{@{}lllrrcl@{}}", r"\toprule",
             r"H & Corpus & Comparison & $b$ & $c$ & Diff.\ [95\% CI] & Verdict \\", r"\midrule"]
    for r in rep:
        if r.get("missing"):
            lines.append(f"{r['hypothesis']} & \\multicolumn{{6}}{{l}}{{missing}} \\\\")
            continue
        lo, hi = r["diff_ci"]
        star = "*" if r.get("holm_significant") else ""
        lines.append(f"{r['hypothesis']} & {r['corpus']} & {names.get(r['x'], r['x'])} vs.\\ {names.get(r['y'], r['y'])} & "
                     f"{r['b']} & {r['c']} & {100 * r['diff']:+.1f} [{100 * lo:+.1f}, {100 * hi:+.1f}]{star} & {r['verdict']} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (out / "contrasts_table.tex").write_text("\n".join(lines) + "\n")

# 4) trade-off figure: x = C3 accuracy (evidence retention), y = C2 accuracy (poisoning resistance)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({"font.family": "serif", "font.size": 8})
fig, ax = plt.subplots(figsize=(3.4, 2.6))
for key, label in ORDER:
    x, y = rate(t[(key, "C3")], 1), rate(t[(key, "C2")], 1)
    if not x or not y:
        continue
    sub = key in SUBSET
    ax.errorbar(100 * x["p"], 100 * y["p"],
                xerr=[[100 * (x["p"] - x["lo"])], [100 * (x["hi"] - x["p"])]],
                yerr=[[100 * (y["p"] - y["lo"])], [100 * (y["hi"] - y["p"])]],
                fmt="s" if sub else "o", mfc="white" if sub else "black", mec="black", ecolor="0.6",
                ms=4, elinewidth=0.6, capsize=1.5)
    name = label.replace("$'$", "'")
    off = LABEL_OFFSET.get(name)
    ax.annotate(name, (100 * x["p"], 100 * y["p"]), xytext=off or (3, 3), textcoords="offset points", fontsize=7,
                arrowprops=dict(arrowstyle="-", lw=0.4, color="0.4", shrinkA=0, shrinkB=2) if off else None)
ax.set_xlabel("Accuracy on C3 (all evidence low trust), %")
ax.set_ylabel("Accuracy on C2 (poisoned), %")
ax.grid(alpha=0.3, lw=0.4)
fig.tight_layout()
fig.savefig(out / "tradeoff.pdf")
(out / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
print("wrote", ", ".join(p.name for p in sorted(out.iterdir())))
