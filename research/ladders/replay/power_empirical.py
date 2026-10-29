"""glitchfox 107696: power of the family-weighted KM test at 27 vs 98 families, with the real between-family spread and
censoring instead of a lognormal sigma=1. Each simulated dataset draws 98 'clean' and 27 'mixed' families with replacement
from the real clean families (null world, real spread, real open episodes), multiplies the mixed episodes' days by a
ratio r (open episodes stay open), and runs the family bootstrap (300 draws) of the weighted KM median difference; power
= share of datasets whose 95% interval excludes 0. 200 datasets per r, seed 1029. Written 29.10 13:36 UTC (date -u)."""
import random, sys
sys.argv = ['x']; src = open('family_weighted_km.py').read().split("for lab, Mf in")[0]; exec(src)
fams = list(C.values()); R = [1.0, 1.5, 2.0, 3.0, 0.5, 0.33]
for r in R:
    rng = random.Random(1029); hit = 0; widths = []; n = 0
    for _ in range(200):
        cl = {i: rng.choice(fams) for i in range(98)}
        mx = {i: [dict(e, days=e['days'] * r) for e in rng.choice(fams)] for i in range(27)}
        out = []
        for _ in range(300):
            a, b = wkm(rs(mx, rng)), wkm(rs(cl, rng))
            if a is not None and b is not None: out.append(a - b)
        if len(out) < 250: continue
        out.sort(); lo, hi = out[int(.025 * len(out))], out[int(.975 * len(out))]
        n += 1; hit += (lo > 0 or hi < 0); widths.append(hi - lo)
    widths.sort()
    print(f"ratio {r}: power {hit / n:.2f} ({n} datasets), median 95% CI width {widths[len(widths) // 2]:.1f} d", flush=True)
