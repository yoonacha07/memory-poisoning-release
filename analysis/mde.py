"""Minimum detectable paired difference for the exact McNemar test.
Normal approximation of Connor (1987), Biometrics 43(1):207-211:
  n = (z_a*sqrt(pd) + z_b*sqrt(pd - d^2))^2 / d^2
where pd is the proportion of discordant pairs and d the paired difference.
Reproduces Section 3.3 of the preregistration (osf.io/[withheld for review]).
"""
from math import sqrt
from scipy.stats import norm

def mde(n, pd, alpha=0.05, power=0.8):
    za, zb = norm.ppf(1 - alpha / 2), norm.ppf(power)
    lo, hi = 1e-6, pd
    for _ in range(200):
        d = (lo + hi) / 2
        need = (za * sqrt(pd) + zb * sqrt(pd - d * d)) ** 2 / d ** 2
        lo, hi = (d, hi) if need > n else (lo, d)
    return d

if __name__ == "__main__":
    for alpha in (0.05, 0.01):
        for n in (350, 120, 60):
            vals = [round(100 * mde(n, p, alpha), 1) for p in (0.15, 0.20, 0.25)]
            print(f"alpha={alpha} n={n}: pd 15/20/25% -> {vals} percentage points")
