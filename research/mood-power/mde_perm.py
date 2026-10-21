"""#396: MDE of the v1.1 spaced permutation test at n = 5..10 and pool sizes near the expected 28-45, on the real
2025-26 FOM placebo stat2 values (same pool rule as mde_sim.py: +-35 d of listed shocks excluded). Units = the last
U eligible waves in series order (their real positions, so the spacing is real). Constant additive effect: the MDE
(80% power, one-sided 5%) is q95 - q20 of the null distribution, as in mde_sim.py. Usage: python3 mde_perm.py"""
import contextlib, io, numpy as np, perm_test as T  # power_check.py lives next to this file
with contextlib.redirect_stdout(io.StringIO()): import power_check as P
s2 = {j: P.stat2(j) for j in range(2, len(P.A)) if P.D[j].year in (2025, 2026) and not P.near(j)}
idx = sorted(s2); print(f"eligible 2025-26 placebo waves: {len(idx)}, sd {np.std([s2[j] for j in idx], ddof=1):.2f}")
for U in (33, 40, 50):
    u = idx[-U:]
    for n in (5, 7, 10):
        tr = list(range(0, U, U // n))[:n]  # any admissible labelling; the null does not depend on which
        r = T.perm_test(u, [s2[j] for j in u], tr)
        print(f"  units {U} (pool {U - n}), n {n:2d}: relabellings {r['relabellings']:>12,d} ({r['mode']}), MDE80 {r['mde80']:.2f} pts, null sd {r['null_sd']:.2f}")
