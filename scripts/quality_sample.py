"""Write 50 random dev questions with their false facts to a CSV for the author's manual check (Section 2.3).
Dev only, so that no test answer key is shown before test."""
import csv
import random
from common import config, split_ids, load_jsonl
from mp.data import load_questions

ff = {r["qid"]: r for r in load_jsonl(config.OUT_DIR / f"falsefacts_n{config.N_FALSE_FACTS}.jsonl")}
qs = load_questions()
ids = random.Random(f"{config.SEED}|quality").sample(sorted(split_ids("dev")), min(50, len(split_ids("dev"))))
with open(config.OUT_DIR / "quality_check.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["qid", "question", "gold", "W", "s1", "s2", "s3", "generator_ok",
                "contradicts_gold (y/n)", "no_instruction (y/n)", "names_real_person (y/n)"])
    for qid in ids:
        r, q = ff.get(qid, {}), qs[qid]
        s = (r.get("sentences") or ["", "", ""]) + ["", "", ""]
        w.writerow([qid, q.question, q.answer, r.get("W", ""), s[0], s[1], s[2], r.get("ok"), "", "", ""])
fails = sum(1 for r in ff.values() if not r["ok"])
print(f"wrote quality_check.csv; generation failures overall: {fails}/{len(ff)}")
