"""patch v1.5 (analysis tools only; no change to answering, judging or decisions):
- analysis/judge_sample.py: add a question_type column to judge_validation_blind.csv so the human scorer can apply
  the official per-type criteria (docs/judge_validation_rubric.md). Question type is not condition information,
  so blinding is unchanged. Sampling, order and the key file are unchanged.
- requirements-exp.txt: add matplotlib (used by analysis/make_figures.py).
Run once from the repository root: python tools/apply_patch_v1_5.py"""
from pathlib import Path

p = Path("analysis/judge_sample.py")
h = p.read_text(encoding="utf-8")
old_row = 'blind.append([i, q.question, q.answer, r["response"], "", ""])'
new_row = 'blind.append([i, "abstention" if q.abstention else q.qtype, q.question, q.answer, r["response"], "", ""])'
old_head = 'w.writerow(["item", "question", "gold_or_rubric", "model_response", "human_correct (1/0)", "notes"])'
new_head = 'w.writerow(["item", "question_type", "question", "gold_or_rubric", "model_response", "human_correct (1/0)", "notes"])'
if new_row in h and new_head in h:
    print("judge_sample.py: already patched")
else:
    assert h.count(old_row) == 1 and h.count(old_head) == 1, "judge_sample.py differs from expected; not patched"
    p.write_text(h.replace(old_row, new_row).replace(old_head, new_head), encoding="utf-8")
    print("judge_sample.py: question_type column added")

r = Path("requirements-exp.txt")
req = r.read_text(encoding="utf-8")
if "matplotlib" not in req:
    r.write_text(req.rstrip("\n") + "\nmatplotlib\n", encoding="utf-8")
    print("requirements-exp.txt: matplotlib added")
else:
    print("requirements-exp.txt: matplotlib already listed")
