"""Draw the 200 judge-validation items of Section 5.2 and write a blinded CSV (condition, corpus and verdict hidden).
Usage: python analysis/judge_sample.py runs/judged_test_*.jsonl --cap 25 --margin 0.1 [--safemem runs/judged_safemem.jsonl]"""
import argparse
import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mp import config                                   # noqa: E402
from mp.data import load_questions                      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--cap", type=int, required=True)
ap.add_argument("--margin", type=float, required=True)
ap.add_argument("--safemem")
a = ap.parse_args()
rows = [json.loads(l) for f in a.files + ([a.safemem] if a.safemem else []) for l in open(f, encoding="utf-8")]
rows = [r for r in rows if r["run"] == 0]
rng = random.Random(f"{config.SEED}|judge200")
focal = ["D0", "D4", f"D5_{a.cap}", "D6"]
pick = []
for s in focal:
    pool = [r for r in rows if r["setting"] == s]
    pick += rng.sample(pool, min(40, len(pool)))
rest = [r for r in rows if r["setting"] not in focal]
pick += rng.sample(rest, min(200 - len(pick), len(rest)))
rng.shuffle(pick)
qs = load_questions()
key, blind = [], []
for i, r in enumerate(pick):
    q = qs[r["qid"]]
    key.append({"item": i, **{k: r.get(k) for k in ("setting", "corpus", "qid", "correct", "attack_success")}})
    blind.append([i, "abstention" if q.abstention else q.qtype, q.question, q.answer, r["response"], "", ""])
with open(config.OUT_DIR / "judge_validation_blind.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["item", "question_type", "question", "gold_or_rubric", "model_response", "human_correct (1/0)", "notes"])
    w.writerows(blind)
(config.OUT_DIR / "judge_validation_key.json").write_text(json.dumps(key, indent=1))
# Second pass, attack-success verdicts (C1/C2 items only), in a new random order and still without condition.
ff = {}
att = [k for k in key if k["corpus"] in ("C1", "C2")]
rng.shuffle(att)
for n in {pick[k["item"]].get("n_ff", config.N_FALSE_FACTS) for k in att}:
    ff[n] = {json.loads(l)["qid"]: json.loads(l) for l in open(config.OUT_DIR / f"falsefacts_n{n}.jsonl", encoding="utf-8")}
with open(config.OUT_DIR / "judge_attack_blind.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["item", "question", "wrong_answer_W", "model_response", "human_adopts_W (1/0)", "notes"])
    for k in att:
        r = pick[k["item"]]
        w.writerow([k["item"], qs[r["qid"]].question, ff[r.get("n_ff", config.N_FALSE_FACTS)][r["qid"]]["W"], r["response"], "", ""])
print("wrote judge_validation_blind.csv, then judge_attack_blind.csv (score in this order); do not open judge_validation_key.json before scoring")
