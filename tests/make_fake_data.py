"""Build a tiny LongMemEval-shaped file (no real benchmark content) for end-to-end tests."""
import json, random, sys
from pathlib import Path
root = Path(sys.argv[1])
rng = random.Random(0)
qtypes = ["single-session-user", "multi-session", "temporal-reasoning", "knowledge-update", "single-session-preference", "single-session-assistant"]
data, dev, test = [], [], []
for i in range(12):
    qid = f"q{i:02d}" + ("_abs" if i % 6 == 5 else "")
    sids = [f"s{i}_{j}" for j in range(8)]
    dates = [f"2023/05/{10+j:02d} (Wed) 1{j}:00" for j in range(8)]
    sessions = []
    for j, sid in enumerate(sids):
        turns = []
        for r in range(3):
            content = f"user talk {i}-{j}-{r} about pets and travel"
            if j == 2 and r == 1:
                content = f"I adopted a cat named Miso{i} last week."
            if j == 4 and r == 0:
                content = "I always answer emails in the morning."
            turns += [{"role": "user", "content": content}, {"role": "assistant", "content": f"reply {r} [source: user conversation]"}]
        sessions.append(turns)
    data.append({"question_id": qid, "question_type": qtypes[i % 6], "question": f"What is the name of my cat? ({i})",
                 "answer": f"Miso{i}", "question_date": "2023/06/01 (Thu) 10:00", "haystack_session_ids": sids,
                 "haystack_dates": dates, "haystack_sessions": sessions, "answer_session_ids": [sids[2]]})
    (dev if i < 6 else test).append(qid)
(root / "SAFE-Mem/data/longmemeval").mkdir(parents=True, exist_ok=True)
(root / "SAFE-Mem/data/longmemeval/longmemeval_s_cleaned.json").write_text(json.dumps(data))
(root / "splits").mkdir(exist_ok=True)
(root / "splits/split.json").write_text(json.dumps({"dev": dev, "test": test}))
(root / "splits/safemem_subset.json").write_text(json.dumps({"order": test[:4]}))
print("fake data written")
