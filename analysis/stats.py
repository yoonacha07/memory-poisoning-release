"""Statistics of Section 5.1: exact McNemar, Holm, Wilson and Newcombe paired intervals."""
from math import sqrt

from scipy.stats import binomtest, norm

Z = norm.ppf(0.975)


def wilson(k, n, z=Z):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def paired_table(x, y):
    """x, y: dicts qid -> 0/1 for the two conditions; only questions present in both are used (Section 5.5)."""
    ids = sorted(set(x) & set(y))
    a = sum(1 for i in ids if x[i] and y[i])
    b = sum(1 for i in ids if x[i] and not y[i])
    c = sum(1 for i in ids if not x[i] and y[i])
    d = sum(1 for i in ids if not x[i] and not y[i])
    return a, b, c, d


def mcnemar_exact(b, c):
    """Two-sided exact McNemar test (binomial, p = 0.5)."""
    if b + c == 0:
        return 1.0
    return binomtest(min(b, c), b + c, 0.5, alternative="two-sided").pvalue


def newcombe_paired(a, b, c, d, z=Z):
    """Newcombe (1998) method 10: 95% CI for p1 - p2 with paired data, Wilson-score based, with Newcombe's
    correlation adjustment. Matches MOVER-NW in the R package ratesci (moverpairci, corc = TRUE).
    p1 = accuracy of condition 1 = (a + b) / n, p2 = (a + c) / n."""
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    num = a * d - b * c
    if num > 0:                                   # Newcombe's correlation adjustment (method 10)
        num = max(num - n / 2, 0.0)
    phi = 0.0 if den == 0 else num / sqrt(den)
    delta = p1 - p2
    lo = delta - sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    hi = delta + sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return delta, max(-1.0, lo), min(1.0, hi)


def holm(pvals, alpha=0.05):
    """Holm step-down; returns a list of booleans (significant) in the input order."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    sig = [False] * len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (len(pvals) - rank):
            sig[i] = True
        else:
            break
    return sig


def compare(x, y):
    """Full report for one paired contrast x vs y."""
    a, b, c, d = paired_table(x, y)
    n = a + b + c + d
    delta, lo, hi = newcombe_paired(a, b, c, d)
    return {"n": n, "acc_x": (a + b) / n, "acc_y": (a + c) / n, "ci_x": wilson(a + b, n), "ci_y": wilson(a + c, n),
            "b": b, "c": c, "p": mcnemar_exact(b, c), "diff": delta, "diff_ci": (lo, hi)}
