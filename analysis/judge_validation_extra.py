"""Judge-validation numbers (registration 5.2 + the extras fixed in 7c7d8f5).
RUN ONLY AFTER both human scorings (answers first, then attacks) are saved AND committed: this script opens the key.
Usage (notebook PowerShell, repo root, venv on). judge_sample.py writes its files into runs/:
  python analysis/judge_validation_extra.py --answers-csv runs/judge_validation_blind.csv --attack-csv runs/judge_attack_blind.csv ^
     --key runs/judge_validation_key.json --judged runs/judged_test_n3_run0.jsonl --judged-cut runs/judged_cut_test_n3_run0.jsonl
(In PowerShell use a backtick ` instead of ^ for line breaks, or put it all on one line.)
Layouts used, read from analysis/judge_sample.py:
  key.json: list of {item, setting, corpus, qid, correct, attack_success}
  answers csv: item, ..., "human_correct (1/0)", notes
  attack csv : item, ..., "human_adopts_W (1/0)", notes
"""
import argparse, csv, json, collections

ap = argparse.ArgumentParser()
ap.add_argument("--answers-csv", required=True); ap.add_argument("--attack-csv"); ap.add_argument("--key", required=True)
ap.add_argument("--judged", required=True); ap.add_argument("--judged-cut")
a = ap.parse_args()

def jl(p): return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
def b(v):
    s = str(v).strip().lower()
    return 1 if s in ("1", "true", "yes") else 0 if s in ("0", "false", "no") else None
def kappa(x, y):
    n = len(x); po = sum(i == j for i, j in zip(x, y)) / n
    px, py = collections.Counter(x), collections.Counter(y)
    pe = sum((px[c] / n) * (py[c] / n) for c in set(x) | set(y))
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")
def rep(name, pairs):
    if len(pairs) < 2: print(f"{name}: n={len(pairs)} (too few)"); return
    h = [p[0] for p in pairs]; j = [p[1] for p in pairs]
    print(f"{name}: n={len(pairs)}  agreement={sum(p == q for p, q in pairs)/len(pairs):.3f}  kappa={kappa(h, j):.3f}")

key = {k["item"]: k for k in json.load(open(a.key, encoding="utf-8"))}
judged = {(r["setting"], r["corpus"], r["qid"], r.get("run", 0)): r for r in jl(a.judged)}
cuts = {(r["setting"], r["corpus"], r["qid"], r.get("run", 0)): r for r in jl(a.judged_cut)} if a.judged_cut else {}

# ---- answers pass ----
rows = list(csv.DictReader(open(a.answers_csv, encoding="utf-8-sig")))
hcol = next(c for c in rows[0] if c.startswith("human_correct"))
recs = []
for r in rows:
    k = key[int(r["item"])]; h = b(r[hcol])
    if h is None: print("item", r["item"], "has no human score"); continue
    full = judged.get((k["setting"], k["corpus"], k["qid"], 0), {})
    recs.append(dict(h=h, j=int(bool(k["correct"])), setting=k["setting"], cut=bool(full.get("empty_or_cut")),
                     unsure=str(r.get("notes", "")).lower().startswith("unsure"),
                     cutj=(cuts.get((k["setting"], k["corpus"], k["qid"], 0)) or {}).get("correct_cut")))
print("== answer scoring ==")
rep("ALL", [(x["h"], x["j"]) for x in recs])
for s in sorted({x["setting"] for x in recs}): rep(f"setting {s}", [(x["h"], x["j"]) for x in recs if x["setting"] == s])
rep("NOT truncated", [(x["h"], x["j"]) for x in recs if not x["cut"]])
cut = [x for x in recs if x["cut"]]
print("truncated rows:", len(cut), "| human scored 1 among them:", sum(x["h"] for x in cut))
cj = [(x["h"], int(bool(x["cutj"]))) for x in cut if x["cutj"] is not None]
if cj: rep("truncated: human vs judged_cut re-judgment", cj)
un = [x for x in recs if x["unsure"]]
print("unsure rows:", len(un)); rep("unsure rows", [(x["h"], x["j"]) for x in un])
print("disagreements (list them and classify: judge error / human error / ambiguous rubric):")
for r in rows:
    k = key[int(r["item"])]; h = b(r[hcol])
    if h is not None and h != int(bool(k["correct"])): print("  item", r["item"], k["setting"], k["corpus"], "human", h, "judge", int(bool(k["correct"])))

# ---- attack pass ----
if a.attack_csv:
    rows = list(csv.DictReader(open(a.attack_csv, encoding="utf-8-sig")))
    hcol = next(c for c in rows[0] if c.startswith("human_adopts_W"))
    pairs, un = [], []
    for r in rows:
        k = key[int(r["item"])]; h = b(r[hcol])
        if h is None: print("attack item", r["item"], "has no human score"); continue
        p = (h, int(bool(k["attack_success"]))); pairs.append(p)
        if str(r.get("notes", "")).lower().startswith("unsure"): un.append(p)
    print("\n== attack scoring ==")
    rep("ATTACK", pairs); print("unsure rows:", len(un)); rep("unsure rows", un)
