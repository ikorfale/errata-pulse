"""clear-margin-1020 #95792: the README MDE (2.5*2.7/sqrt(n)) used the v1 statistic's SD. Recalibrate for the planned
v2 test: stat2 = wave - mean(2 preceding waves); placebo = same-year waves, +-35 d of listed shocks excluded.
Draws keep the real series and its dependence: n pseudo-strike waves from the chosen years' placebo weeks, no two
within 3 waves (no treatment wave inside another's 2-wave baseline; greedy over a random order). For a constant
additive effect delta, power = P(null mean > crit - delta), so MDE(80%) = q95 - q20 of the null mean distribution.
Usage: python3 mde_sim.py"""
import numpy as np, power_check as P   # power_check prints its own tables on import
A, D, near, stat2 = P.A, P.D, P.near, P.stat2
rng = np.random.default_rng(95792)
pool = {y: [j for j in range(2, len(A)) if D[j].year == y and not near(j)] for y in range(2022, 2027)}
s2 = np.array([stat2(j) if j >= 2 else np.nan for j in range(len(A))])
def draw(idx, n):
    out = []
    for j in rng.permutation(idx):
        if all(abs(j - k) >= 3 for k in out): out.append(j)
        if len(out) == n: return out
    return None
print("\n== MDE recalibration (v2 statistic, spaced >= 3 waves, 20000 draws) ==")
for y in pool: print(f"  {y}: placebo n={len(pool[y])} sd {np.std(s2[pool[y]], ddof=1):.4f}")
for years in ((2025, 2026), (2023, 2024, 2025, 2026), (2022, 2023, 2024, 2025, 2026)):
    idx = np.array([j for y in years for j in pool[y]])
    for n in (10, 25):
        m = [draw(idx, n) for _ in range(20000)]; ok = [x for x in m if x is not None]
        nm = np.array([s2[x].mean() for x in ok]) - s2[idx].mean()
        q95, q20 = np.percentile(nm, [95, 20]); iid = 2.4865 * np.std(s2[idx], ddof=1) / np.sqrt(n)
        print(f"  years {'-'.join(map(str, (years[0], years[-1])))}: n={n:2d}  MDE(80%, one-sided 5%) {q95 - q20:.2f} pts"
              f"  (iid formula with this pool's sd {iid:.2f}; sd of mean {nm.std():.3f} vs iid {np.std(s2[idx], ddof=1)/np.sqrt(n):.3f}; draws {len(ok)})")
