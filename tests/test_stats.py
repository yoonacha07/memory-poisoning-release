"""Checks of analysis/stats.py against published reference values.
Paired-difference values are the expected results in the test suite of the R package ratesci
(tests/testthat/test3.R: moverpairci(..., contrast = "RD", type = "wilson", corc = TRUE)), which reproduce
Newcombe (1998) method 10 and Fagerland et al.; tables are (a, b, c, d) with p1 = (a + b)/n, p2 = (a + c)/n."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analysis.stats import newcombe_paired, wilson, mcnemar_exact, holm

for tab, (elo, ehi) in [((20, 12, 2, 16), (0.0562, 0.3292)),
                        ((8, 3, 1, 2), (-0.1574, 0.4136)),
                        ((1, 1, 7, 12), (-0.507, -0.026))]:
    _, lo, hi = newcombe_paired(*tab)
    tol = 5e-4 if len(str(elo).split(".")[1]) == 3 else 5e-5
    assert abs(lo - elo) < tol and abs(hi - ehi) < tol, (tab, lo, hi)
l, u = wilson(81, 263)                     # Newcombe (1998a) single-proportion example: 0.2553 to 0.3662
assert abs(l - 0.2553) < 5e-5 and abs(u - 0.3662) < 5e-5, (l, u)
assert abs(mcnemar_exact(12, 2) - 0.012939) < 1e-5
assert holm([0.001, 0.04, 0.012, 0.3, 0.02]) == [True, False, True, False, False]
print("stats tests passed")
