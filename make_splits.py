import collections, hashlib, json, random
from pathlib import Path

SEED = 20261028
DATA = Path("SAFE-Mem/data/longmemeval/longmemeval_s_cleaned.json")
data = json.loads(DATA.read_text(encoding="utf-8"))

def stratum(x):  # 문항 유형, 답할 수 없는 문항(_abs)은 따로
    t = x["question_type"]
    return t + ("_abs" if str(x["question_id"]).endswith("_abs") else "")

def allocate(sizes, total):  # 비율대로 나누고 남는 자리는 소수점이 큰 순서로
    n = sum(sizes.values())
    raw = {k: v * total / n for k, v in sizes.items()}
    out = {k: int(r) for k, r in raw.items()}
    for k in sorted(raw, key=lambda k: (-(raw[k] - out[k]), k))[: total - sum(out.values())]:
        out[k] += 1
    return out

groups = collections.defaultdict(list)
for x in data:
    groups[stratum(x)].append(str(x["question_id"]))

rng = random.Random(SEED)
for k in sorted(groups):
    groups[k].sort()
    rng.shuffle(groups[k])

dev_n = allocate({k: len(v) for k, v in groups.items()}, 150)
dev, test_g = [], {}
for k in sorted(groups):
    dev += groups[k][: dev_n[k]]
    test_g[k] = groups[k][dev_n[k]:]
test = [i for k in sorted(test_g) for i in test_g[k]]

sub_n = allocate({k: len(v) for k, v in test_g.items()}, 120)
sub = [i for k in sorted(test_g) for i in test_g[k][: sub_n[k]]]
rng.shuffle(sub)

sha = hashlib.sha256(DATA.read_bytes()).hexdigest()
Path("splits").mkdir(exist_ok=True)
meta = {"seed": SEED, "source": DATA.name, "sha256": sha}
Path("splits/split.json").write_text(json.dumps({**meta, "dev": sorted(dev), "test": sorted(test)}, indent=1))
Path("splits/safemem_subset.json").write_text(json.dumps({**meta, "order": sub}, indent=1))

print(f"데이터 SHA-256: {sha}")
print(f"{'유형':<34}{'전체':>5}{'dev':>5}{'test':>5}{'SAFE-Mem':>9}")
for k in sorted(groups):
    print(f"{k:<34}{len(groups[k]):>5}{dev_n[k]:>5}{len(test_g[k]):>5}{sub_n[k]:>9}")
print(f"{'합계':<34}{len(data):>5}{len(dev):>5}{len(test):>5}{len(sub):>9}")