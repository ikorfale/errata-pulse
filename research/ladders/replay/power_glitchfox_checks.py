"""glitchfox 107783: two checks on the 27/98 power asymmetry (x0.5 0.23 vs x2 0.35 in power_armsize.py).
(1) invariance: mixed x0.5 vs clean x1 must give exactly the same decisions as mixed x1 vs clean x2 (KM medians scale
with days, censoring too, so the CI-excludes-0 decision is scale-free); same seed 1029, 200 datasets.
(2) second seed: 27/98 at r = 0.5 and 2 with seed 2029 and N datasets (argv[1], default 1000), 300 draws each.
Written 29.10 15:45 UTC (date -u)."""
import random, sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000; part = sys.argv[2] if len(sys.argv) > 2 else 'both'
sys.argv = ['x']; src = open('family_weighted_km.py').read().split("for lab, Mf in")[0]; exec(src)
fams = list(C.values())
def run(nm, nc, rm, rc, seed, nd):
    rng = random.Random(seed); dec = []
    for _ in range(nd):
        cl = {i: [dict(e, days=e['days'] * rc) for e in rng.choice(fams)] for i in range(nc)}
        mx = {i: [dict(e, days=e['days'] * rm) for e in rng.choice(fams)] for i in range(nm)}
        out = []
        for _ in range(300):
            a, b = wkm(rs(mx, rng)), wkm(rs(cl, rng))
            if a is not None and b is not None: out.append(a - b)
        if len(out) < 250: dec.append(None); continue
        out.sort(); lo, hi = out[int(.025 * len(out))], out[int(.975 * len(out))]
        dec.append(lo > 0 or hi < 0)
    v = [d for d in dec if d is not None]; return dec, sum(v) / len(v), len(v)
if part in ('both', 'inv'):
    d1, p1, n1 = run(27, 98, 0.5, 1.0, 1029, 200); d2, p2, n2 = run(27, 98, 1.0, 2.0, 1029, 200)
    print(f"(1) mixed x0.5 / clean x1: power {p1:.2f} ({n1}); mixed x1 / clean x2: power {p2:.2f} ({n2}); "
          f"decisions identical in {sum(a == b for a, b in zip(d1, d2))}/{len(d1)} datasets", flush=True)
if part in ('both', 'seed'):
    for r in (0.5, 2.0):
        _, p, n = run(27, 98, r, 1.0, 2029, N); se = (p * (1 - p) / n) ** .5
        print(f"(2) seed 2029, 27/98, ratio {r}: power {p:.3f} ({n} datasets, binomial SE {se:.3f})", flush=True)
