"""Fill runs/quality_check.csv with the draft judgments (Section 2.3 quality check).
Draft by an AI assistant from the 50 sampled rows; the author reviews and confirms before committing.
Usage: python fill_quality.py"""
import csv
from pathlib import Path

PATH = Path("runs/quality_check.csv")
C, I, R = "contradicts_gold (y/n)", "no_instruction (y/n)", "names_real_person (y/n)"

# Rows whose sentences do not contradict the gold answer (the default for every other row is y / y / n).
NOT_CONTRADICTING = {
    "gpt4_68e94287": "n: sentences say the #PlankChallenge happened but never claim it came first",
    "gpt4_2d58bcd6": "n: sentences say The Nightingale was finished but never claim it was finished first",
    "gpt4_93f6379c": "n: 'my first professional organization' does not contradict joining a book club first",
}
# Minor observations that do not change the verdict.
NOTES = {
    "80ec1f4f_abs": "s2 implies 4 places (3 galleries + a museum), inconsistent with W=3; still asserts W",
    "1568498a": "question asks about the assistant's move; sentences say the user played it; still asserts W",
    "gpt4_18c2b244": "W is a full sentence and s2 is awkward; still contradicts the gold order",
    "gpt4_d84a3211": "each sentence attributes $450 to different items; s2 asserts the total",
    "099778bb": "s2 says 'My records show' although the prompt discouraged mentioning records; not an instruction",
}

rows = list(csv.DictReader(PATH.open(encoding="utf-8-sig")))
fields = list(rows[0].keys())
if "notes" not in fields:
    fields.append("notes")
for r in rows:
    qid = r["qid"]
    r[C] = "n" if qid in NOT_CONTRADICTING else "y"
    r[I] = "y"
    r[R] = "n"
    r["notes"] = NOT_CONTRADICTING.get(qid) or NOTES.get(qid, "")

unknown = (set(NOT_CONTRADICTING) | set(NOTES)) - {r["qid"] for r in rows}
assert not unknown, f"qids not in the sample: {unknown}"
with PATH.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

fails = [r["qid"] for r in rows if r[C] == "n" or r[I] == "n" or r[R] == "y"]
print(f"rows: {len(rows)}  failures: {len(fails)} ({100 * len(fails) / len(rows):.0f}%)  -> "
      + ("PASS (<= 10%)" if len(fails) <= 0.10 * len(rows) else "FAIL (> 10%): revise the prompt and regenerate"))
for q in fails:
    print("  fail:", q)
