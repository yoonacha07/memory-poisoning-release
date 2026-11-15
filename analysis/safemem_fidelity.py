"""SAFE-Mem fidelity check (registration 5.7 (a)-(d)) and D6 vs D6' / D0 comparisons for interpreting H5.
Registration 5.7 governs. (a) parse failures above 10% -> every SAFE-Mem result is labelled a degraded reproduction.
(d) on C0, D6 and D6' against D0 by exact McNemar, unadjusted; if D6' is significantly below D0, the report says the
storage pipeline underperforms with this model. The old 10-point D6-vs-D0 note is kept only as an auxiliary remark.
Run only after test judging is committed. Read with docs/interpretation_plan.md section 3 (H5).
Usage (notebook PowerShell, repo root, venv on):
  python analysis/safemem_fidelity.py runs/judged_safemem_n3.jsonl runs/judged_test_n3_run0.jsonl

Fields written by scripts/run_safemem.py for every answer row (one row = question x corpus x setting; the
counters are reset for every row, so totals are summed over rows and then divided):
  extract_calls, parse_fail       claim-extraction calls and unparseable replies
  sessions, zero_claim_sessions   real (non-false-fact) sessions written, and those that produced no claim
  required_use                    use type the question was classified as
  eligible_empty, n_entries       retrieval returned no eligible entry / number of entries retrieved
  ff_in_context                   the wrong answer W appeared in the answer context (C2 only)
Correctness is read only from the judge field "correct".
"""
import collections
import json
import sys


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def need(rows, field):
    miss = sum(1 for r in rows if field not in r)
    if miss:
        print(f"  WARNING: {miss} rows have no '{field}'")
    return miss == 0


def num(x):
    return int(x) if isinstance(x, bool) else (x if isinstance(x, (int, float)) else 0)


def share(a, b):
    return f"{a}/{b} ({a / b:.1%})" if b else f"{a}/0"


def mcnemar_exact(a, b, common):
    """Two-sided exact McNemar (binomial, p=0.5) on paired 0/1 outcomes. Returns (n10, n01, p) with n10 = a right & b wrong."""
    from math import comb
    n10 = sum(1 for q in common if a[q] == 1 and b[q] == 0)
    n01 = sum(1 for q in common if a[q] == 0 and b[q] == 1)
    n = n10 + n01
    if n == 0:
        return n10, n01, 1.0
    k = min(n10, n01)
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    return n10, n01, p


sm, main = load(sys.argv[1]), load(sys.argv[2])
cells = sorted({(r["setting"], r["corpus"]) for r in sm})
print("SAFE-Mem rows:", len(sm), "| questions:", len({r["qid"] for r in sm}))
print("rows per setting x corpus (expect C0 120, C2 115, C3 120):",
      {f"{s}/{c}": n for (s, c), n in sorted(collections.Counter((r["setting"], r["corpus"]) for r in sm).items())})
for f in ("extract_calls", "parse_fail", "sessions", "zero_claim_sessions", "required_use", "eligible_empty",
          "n_entries", "correct"):
    need(sm, f)

print("\n[1] claim-extraction parse failures (sum over rows)")
for s, c in cells + [("ALL", "ALL")]:
    rs = [r for r in sm if (s == "ALL" or (r["setting"], r["corpus"]) == (s, c))]
    print(f"  {s:4} {c:4} {share(sum(num(r.get('parse_fail')) for r in rs), sum(num(r.get('extract_calls')) for r in rs))}")

_ec = sum(num(r.get("extract_calls")) for r in sm)
_pf = sum(num(r.get("parse_fail")) for r in sm)
if _ec and _pf / _ec > 0.10:
    print(f"  REGISTERED FLAG (5.7 (a)): parse failures {_pf / _ec:.1%} exceed 10%: label EVERY SAFE-Mem result, "
          "including the H5 verdict, a degraded reproduction.")
elif _ec:
    print(f"  5.7 (a): parse failures {_pf / _ec:.1%} do not exceed 10%: no degraded-reproduction flag.")

print("\n[2] sessions that produced no claim (sum over rows)")
for s, c in cells + [("ALL", "ALL")]:
    rs = [r for r in sm if (s == "ALL" or (r["setting"], r["corpus"]) == (s, c))]
    print(f"  {s:4} {c:4} {share(sum(num(r.get('zero_claim_sessions')) for r in rs), sum(num(r.get('sessions')) for r in rs))}")

print("\n[3] use-type distribution (required_use) by setting")
for s in sorted({r["setting"] for r in sm}):
    cnt = collections.Counter(str(r.get("required_use")) for r in sm if r["setting"] == s)
    print(f"  {s:4}", dict(cnt.most_common()))

print("\n[4] retrieval with no eligible entry, and mean entries retrieved")
for s, c in cells:
    rs = [r for r in sm if (r["setting"], r["corpus"]) == (s, c)]
    ne = sum(1 for r in rs if r.get("eligible_empty"))
    mean = sum(num(r.get("n_entries")) for r in rs) / len(rs)
    print(f"  {s:4} {c:4} eligible_empty {share(ne, len(rs))} | mean n_entries {mean:.2f}")

print("\n[5] C2: wrong answer W reached the answer context")
for s in sorted({r["setting"] for r in sm}):
    rs = [r for r in sm if r["setting"] == s and r["corpus"] == "C2"]
    print(f"  {s:4} {share(sum(1 for r in rs if r.get('ff_in_context')), len(rs))}")

print("\n[6] accuracy on the same questions (judge field 'correct')")
acc = collections.defaultdict(dict)
for r in sm:
    if "correct" in r:
        acc[(r["setting"], r["corpus"])][r["qid"]] = int(bool(r["correct"]))
qids = {r["qid"] for r in sm}
for r in main:
    if r["qid"] in qids and r["setting"] == "D0" and "correct" in r:
        acc[("D0", r["corpus"])][r["qid"]] = int(bool(r["correct"]))
for c in ("C0", "C2", "C3"):
    a6, a6p, a0 = acc[("D6", c)], acc[("D6p", c)], acc[("D0", c)]
    common = sorted(set(a6) & set(a6p) & set(a0))
    if not common:
        print(f"  {c}: no shared questions with all three settings")
        continue
    m = lambda d: sum(d[q] for q in common) / len(common)
    print(f"  {c} n={len(common)}: D6 {m(a6):.1%} | D6' {m(a6p):.1%} | D0 {m(a0):.1%} | "
          f"D6-D6' {100 * (m(a6) - m(a6p)):+.1f} pt | D6-D0 {100 * (m(a6) - m(a0)):+.1f} pt")
    if c == "C0":
        for name, a in (("D6", a6), ("D6'", a6p)):
            n10, n01, p = mcnemar_exact(a, a0, common)
            below = (n10 < n01) and p < 0.05
            print(f"    5.7 (d) {name} vs D0 on C0: {name}-only correct {n10}, D0-only correct {n01}, exact McNemar p = {p:.4g} (unadjusted)")
            if name == "D6'" and below:
                print("    REGISTERED FLAG (5.7 (d)): D6' is significantly below D0 on C0: state that SAFE-Mem's storage pipeline "
                      "underperforms with this model, so contrast 5 may reflect model capacity rather than authority-based exclusion.")
        if m(a0) - m(a6) >= 0.10:
            print("    Auxiliary remark only (not the registered rule): D6 is 10+ points below D0 on C0.")
print("\nDescriptive only. The H5 verdict comes from analysis/test_report.py; nothing here changes it.")
