"""glitchfox 107596: family as the resampling unit. (1) family-cluster bootstrap (2000 draws, families resampled with
replacement, all their episodes kept) of the KM median difference mixed - clean, with and without the AGI family;
(2) leave-one-family-out on the clean KM median (14.3 d); (3) share of episodes held by the largest family per class.
Same cut and classes as censor_check.py. Written 29.10 11:46 UTC (date -u)."""
import json, random, sys
from collections import defaultdict
sys.argv = ['x']; src = open('censor_check.py').read().split("for name, sel in")[0]; exec(src)
def kmm(eps): return km(eps)[0]
C = defaultdict(list); M = defaultdict(list)
for r in k: (C if cls[(r['early'], r['late'])] == 'same' else M)[r['family']].append(r)
agi = [f for f in M if f.startswith('will we get agi')]
def boot(Cf, Mf, n=2000, seed=1029):
    rng = random.Random(seed); cf, mf = list(Cf), list(Mf); out = []
    for _ in range(n):
        c = [r for f in (rng.choice(cf) for _ in cf) for r in Cf[f]]; m = [r for f in (rng.choice(mf) for _ in mf) for r in Mf[f]]
        a, b = kmm(m), kmm(c)
        if a is not None and b is not None: out.append(a - b)
    out.sort(); return out[int(.025 * len(out))], out[int(.975 * len(out))], len(out)
fl = lambda D: [r for v in D.values() for r in v]
for lab, Mf in (('all mixed', M), ('mixed without AGI', {f: v for f, v in M.items() if f not in agi})):
    lo, hi, n = boot(C, Mf)
    print(f"{lab}: KM median mixed {kmm(fl(Mf)):.1f} d vs clean {kmm(fl(C)):.1f} d, diff {kmm(fl(Mf)) - kmm(fl(C)):+.1f}; family bootstrap 95% {lo:+.1f} .. {hi:+.1f} ({n} draws)")
lofo = sorted((kmm(fl({g: v for g, v in C.items() if g != f})), f, len(C[f])) for f in C)
print(f"clean leave-one-family-out KM median: min {lofo[0][0]:.1f} d (drop '{lofo[0][1][:40]}', {lofo[0][2]} ep), max {lofo[-1][0]:.1f} d (drop '{lofo[-1][1][:40]}', {lofo[-1][2]} ep), of {len(lofo)} families")
rng = random.Random(7); cf = list(C); bm = sorted(kmm([r for f in (rng.choice(cf) for _ in cf) for r in C[f]]) for _ in range(2000))
print(f"clean KM median family bootstrap 95%: {bm[50]:.1f} .. {bm[1949]:.1f} d")
for lab, D in (('clean', C), ('mixed', M), ('mixed without AGI', {f: v for f, v in M.items() if f not in agi})):
    n = sum(map(len, D.values())); big = max(D, key=lambda f: len(D[f]))
    print(f"{lab}: {n} episodes, {len(D)} families, largest '{big[:40]}' {len(D[big])} = {len(D[big]) / n:.0%}")
