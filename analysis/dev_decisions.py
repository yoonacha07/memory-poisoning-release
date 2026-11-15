"""Dev decisions of Section 5.4: attack check, selection of the cap and the margin, replication direction,
and the 50 questions for the run-to-run check. Usage: python analysis/dev_decisions.py runs/judged_dev_n3_run0.jsonl"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mp import config                           # noqa: E402
from analysis.stats import compare              # noqa: E402


def acc_table(rows):
    t = defaultdict(dict)
    for r in rows:
        if r["run"] == 0:
            t[(r["setting"], r["corpus"])][r["qid"]] = int(r["correct"])
    return t


def mean(d):
    return sum(d.values()) / len(d) if d else float("nan")


def decide(rows):
    t = acc_table(rows)
    out = {}
    c0, c2 = mean(t[("D0", "C0")]), mean(t[("D0", "C2")])
    out["attack_check"] = {"D0_C0": c0, "D0_C2": c2, "drop_points": 100 * (c0 - c2), "passed": c0 - c2 >= 0.10}

    def score(s):
        return (mean(t[(s, "C2")]) + mean(t[(s, "C3")])) / 2
    caps = {c: score(f"D3_{c}") for c in config.D3_CAPS}
    best_cap = max(caps.values())
    out["cap"] = max(c for c in config.D3_CAPS if caps[c] == best_cap)            # tie -> larger cap
    margins = {m: score(f"D2_{m}") for m in config.D2_MARGINS}
    best_m = max(margins.values())
    out["margin"] = min(m for m in config.D2_MARGINS if margins[m] == best_m)    # tie -> smaller margin
    out["cap_scores"], out["margin_scores"] = caps, margins
    out["replication"] = {
        "shipped_vs_D0_on_C2": compare(t[(f"D2_{config.D2_SHIPPED}", "C2")], t[("D0", "C2")]),
        "corrected_vs_D0_on_C3": compare(t[(f"D2_{config.D2_CORRECTED}", "C3")], t[("D0", "C3")])}
    return out


if __name__ == "__main__":
    rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    dec = decide(rows)
    ids = sorted({r["qid"] for r in rows})
    var50 = random.Random(f"{config.SEED}|var50").sample(ids, min(50, len(ids)))
    (config.OUT_DIR / "var50.txt").write_text("\n".join(var50))
    dec["var50_file"] = "runs/var50.txt"
    (config.OUT_DIR / "dev_decisions.json").write_text(json.dumps(dec, indent=1, default=str))
    print(json.dumps(dec, indent=1, default=str))
