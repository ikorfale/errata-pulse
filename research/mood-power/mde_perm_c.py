"""PREREG v1.4 item 10, sensitivity C: null sd and MDE of the spaced permutation test for stat3 = A[W1] - mean(A[W1-2],
A[W1-3]) with spacing >= 4, on the real 2025-26 FOM placebo waves, by the same computation as mde_perm.py (stat2,
spacing 3), which is printed beside it for comparison. Eligible: 2025-26 waves outside +-35 d of listed shocks whose 4
consecutive waves W-3..W are each <= 10 days apart (C's measurability rule; mde_perm.py applies no such rule, so the
stat2 rows here use the same eligibility to compare like with like). Units = the last U eligible waves in series order
(real positions, so the spacing is real). MDE80 = q95 - q20 of the null. Usage: python3 mde_perm_c.py"""
import contextlib, io, numpy as np, perm_test as T
with contextlib.redirect_stdout(io.StringIO()): import power_check as P
ok = lambda j: j >= 3 and all((P.D[k] - P.D[k - 1]).days <= 10 for k in range(j - 2, j + 1))
stat3 = lambda j: P.A[j] - P.A[[j - 2, j - 3]].mean()
idx = [j for j in range(3, len(P.A)) if P.D[j].year in (2025, 2026) and not P.near(j) and ok(j)]
for name, f, gap in (('stat3 (C), gap 4', stat3, 4), ('stat2 (primary), gap 3', P.stat2, 3)):
    v = {j: f(j) for j in idx}
    print(f"{name}: eligible 2025-26 placebo waves {len(idx)}, sd {np.std(list(v.values()), ddof=1):.2f}")
    for U in (20, 25, 33, 40):
        u = idx[-U:]
        for n in (5, 7):
            tr = []  # any admissible labelling (the null does not depend on which): greedy from the first unit
            for k in range(U):
                if not tr or u[k] - u[tr[-1]] >= gap: tr.append(k)
            tr = tr[:n]
            if len(tr) < n: print(f"  units {U}: n {n} not reachable with gap {gap}"); continue
            r = T.perm_test(u, [v[j] for j in u], tr, gap=gap)
            print(f"  units {U} (pool {U - n}), n {n}: relabellings {r['relabellings']:>10,d} ({r['mode']}), MDE80 {r['mde80']:.2f} pts, null sd {r['null_sd']:.2f}")
