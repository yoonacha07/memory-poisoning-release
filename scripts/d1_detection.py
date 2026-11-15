"""D1 detection performance on dev (Section 4, exploratory): A2' sentences, A1 instructions, and genuine items.
Usage: python scripts/d1_detection.py"""
import json
from common import config, split_ids, load_jsonl
from mp.conditions import matches_pattern
from mp.data import load_questions
from mp.falsefacts import a1_instruction
from mp.judging import d1_classifier
from mp.llm import Ollama

qs = load_questions()
ff = {r["qid"]: r for r in load_jsonl(config.OUT_DIR / f"falsefacts_n{config.N_FALSE_FACTS}.jsonl")}
llm = Ollama(config.ANSWER_MODEL, cache_dir=config.OUT_DIR / "cache_answer")
clf = d1_classifier(llm)
flag = lambda t: matches_pattern(t) or clf(t)
a2 = a1 = gen = 0
n_a2 = n_a1 = n_gen = 0
for qid in split_ids("dev"):
    r = ff.get(qid)
    if r and r["ok"]:
        for s in r["sentences"]:
            n_a2 += 1; a2 += flag(s)
        n_a1 += 1; a1 += flag(a1_instruction(r["W"]))
    for it in qs[qid].items[::10]:                       # every 10th genuine item
        n_gen += 1; gen += flag(it.content)
res = {"A2_recall": a2 / max(1, n_a2), "A1_recall": a1 / max(1, n_a1), "genuine_FPR": gen / max(1, n_gen),
       "n": {"A2": n_a2, "A1": n_a1, "genuine": n_gen}}
(config.OUT_DIR / "d1_detection_dev.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
