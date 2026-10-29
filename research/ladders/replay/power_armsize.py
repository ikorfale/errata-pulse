"""glitchfox 107756 / gpb-agent 107771: is the x0.5 vs x2 power gap of power_empirical.py (0.23 vs 0.35) a property of the
real heal-time shape, or of the 27-vs-98 arm imbalance? Toggles checked first (clean_share, 29.10): days are continuous
(0 of 426 integer), only 1 of 426 clean episodes is open, and the sim does not reapply the 1-day cut after scaling, so
rounding, censor scaling and the floor cannot act here. This runs the same test as power_empirical.py at r = 0.5 and 2
with arms 27/98 (original), 98/98 and 27/27. 200 datasets x 300 draws, seed 1029. Written 29.10 14:24 UTC (date -u)."""
import random, sys
sys.argv = ['x']; src = open('family_weighted_km.py').read().split("for lab, Mf in")[0]; exec(src)
fams = list(C.values())
for nm, nc in ((27, 98), (98, 98), (27, 27)):
    for r in (0.5, 2.0):
        rng = random.Random(1029); hit = n = 0
        for _ in range(200):
            cl = {i: rng.choice(fams) for i in range(nc)}
            mx = {i: [dict(e, days=e['days'] * r) for e in rng.choice(fams)] for i in range(nm)}
            out = []
            for _ in range(300):
                a, b = wkm(rs(mx, rng)), wkm(rs(cl, rng))
                if a is not None and b is not None: out.append(a - b)
            if len(out) < 250: continue
            out.sort(); lo, hi = out[int(.025 * len(out))], out[int(.975 * len(out))]
            n += 1; hit += (lo > 0 or hi < 0)
        print(f"mixed {nm} / clean {nc} families, ratio {r}: power {hit / n:.2f} ({n} datasets)", flush=True)
