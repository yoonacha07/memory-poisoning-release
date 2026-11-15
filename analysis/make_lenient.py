"""EXPLORATORY (docs/exploratory_truncation_plan.md). Builds a 'lenient' copy of a judged file in which every
cut answer takes its as-is verdict from judged_cut_*.jsonl instead of the registered 'cut = incorrect' rule.
Usage: python analysis/make_lenient.py runs/judged_test_n3_run0.jsonl runs/judged_cut_test_n3_run0.jsonl
Output: runs/judged_lenient_<name>.jsonl, then run analysis/test_report.py on it (label all results exploratory)."""
import json
import sys
from collections import Counter
from pathlib import Path

judged, cut = Path(sys.argv[1]), Path(sys.argv[2])
key = lambda r: (r["setting"], r["corpus"], r["qid"], r["run"])
cuts = {key(r): r for r in (json.loads(l) for l in cut.read_text(encoding="utf-8").splitlines() if l.strip())}
out = judged.with_name(judged.name.replace("judged_", "judged_lenient_"))
n = Counter()
with open(out, "w", encoding="utf-8") as f:
    for l in judged.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        r["lenient"] = True
        if r.get("empty_or_cut"):
            n["cut"] += 1
            c = cuts.get(key(r))
            if c is None:
                n["cut_missing_verdict"] += 1          # left as registered (incorrect)
            else:
                n["flipped_correct"] += int(c["correct_cut"] and not r["correct"])
                r["correct"] = c["correct_cut"]
                if "attack_cut" in c:
                    n["flipped_attack"] += int(c["attack_cut"] and not r.get("attack_success"))
                    r["attack_success"] = c["attack_cut"]
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"out": str(out), **n}, indent=1))
