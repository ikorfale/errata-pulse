"""#566: post-hoc minimum detectable effect for the #564 resolved-ladder verdict (P1: KM median heal time per
time-to-close bin), at the family counts actually fetched, with the real between-family spread and censoring.

For each adjacent pair of bins (A, B) with their real family counts (nA, nB): the null world pools the families of
both bins; each simulated dataset draws nA and nB families with replacement from that pool, multiplies B's heal times
by r (expired episodes stay censored, their time scaled too), and runs a family bootstrap (B_BOOT draws) of
log(KM median B / KM median A). Power = share of datasets whose 95% interval excludes 0. The ratio scale is used
because bin medians differ by x10 across the range, so a day difference would mean different things per pair.
Then the stopping rule: power at r = 2 against families per bin (n per arm) on the pooled set of all bins.
Estimator: argv[1] = 'h1' (share healed within 1 h: the 01.11 primary, 110446; ratio of shares, so r>1 = fewer
healed), 'ep' (episode-weighted KM median, as resolved_verdict.py ran it) or 'fw' (family-weighted,
each family weight 1, its episodes 1/n_f each, as family_weighted_km.py). Part C (observed intervals) was added
after A and B of the 'ep' run had printed.
Seed 566. Written 2026-11-03 (date -u). Run: python3 power_resolved.py ep|fw > power_resolved_<est>.txt"""
import json, math, random, sys
from collections import defaultdict

N_DATA, B_BOOT, SEED = 120, 200, 566
rows = [json.loads(l) for l in open('resolved/episodes.jsonl')]
BINS = [(0, 7, '<7'), (7, 30, '7-30'), (30, 180, '30-180'), (180, 365, '180-365'), (365, 1e9, '>365')]


def km_median(eps):
    """Same KM median as resolved_verdict.py: expired episodes censored at their heal time; None if S stays > 0.5."""
    s, n = 1.0, len(eps)
    for t, ev in sorted(eps):
        if ev:
            s *= (n - 1) / n
            if s <= 0.5:
                return t
        n -= 1
    return None


def fams_of(lo, hi):
    fb = defaultdict(list)
    for r in rows:
        if lo <= r['ttc'] < hi:
            fb[(r['family'], lo)].append((r['heal'], not r['expired']))
    return list(fb.values())


def draw(pool, n, rng):
    return [rng.choice(pool) for _ in range(n)]


def wkm_median(fams):
    """Family-weighted KM median: episode weight 1/n_f, so every family counts once."""
    t = sorted((h, ev, 1 / len(f)) for f in fams for h, ev in f)
    n = sum(w for *_, w in t); s = 1.0; i = 0
    while i < len(t):
        x = t[i][0]; d = c = 0
        while i < len(t) and t[i][0] == x: d += t[i][2] * t[i][1]; c += t[i][2]; i += 1
        if d: s *= 1 - d / n
        n -= c
        if s <= .5: return x
    return None


EST = sys.argv[1] if len(sys.argv) > 1 else 'ep'


def h1(fams):
    """Share of episodes healed within 1 h (expired = not healed; splits not separated here: 2-7% per bin, cif.txt)."""
    e = [x for f in fams for x in f]
    return sum(1 for t, ev in e if ev and t <= 1 / 24) / len(e) if e else None


def med(fams):
    if EST == 'h1': return h1(fams)
    return km_median([e for f in fams for e in f]) if EST == 'ep' else wkm_median(fams)


def logratio(fa, fb):
    a = med(fa); b = med(fb)
    if not a or not b: return None
    return math.log(b / a)


def power(pool, nA, nB, r, rng):
    hit = n_ok = 0; widths = []
    for _ in range(N_DATA):
        A = draw(pool, nA, rng)
        B = [[(t * r, ev) for t, ev in f] for f in draw(pool, nB, rng)]
        out = []
        for _ in range(B_BOOT):
            x = logratio(draw(A, nA, rng), draw(B, nB, rng))
            if x is not None: out.append(x)
        if len(out) < 0.9 * B_BOOT: continue
        out.sort(); lo, hi = out[int(.025 * len(out))], out[int(.975 * len(out))]
        n_ok += 1; hit += (lo > 0 or hi < 0); widths.append(hi - lo)
    widths.sort()
    return hit / n_ok if n_ok else float('nan'), n_ok, math.exp(widths[len(widths) // 2] / 2) if widths else float('nan')


F = {name: fams_of(lo, hi) for lo, hi, name in BINS}
print('estimator:', EST, '| families per bin:', {k: len(v) for k, v in F.items()})
print(f'{N_DATA} datasets x {B_BOOT} family-bootstrap draws, seed {SEED}; power = 95% CI of log(KM med B/A) excludes 0')
print('\nA. adjacent bins at the real family counts (null = both bins pooled); "CI x" = median half-width as a factor')
names = [b[2] for b in BINS]
for a, b in zip(names, names[1:]):
    pool = F[a] + F[b]
    for r in (1.0, 1.5, 2.0, 3.0):
        p, n_ok, cw = power(pool, len(F[a]), len(F[b]), r, random.Random(SEED))
        print(f'{a:>8} ({len(F[a])}) vs {b:<8} ({len(F[b])})  r={r:<4} power {p:.2f}  ({n_ok} ok)  CI x{cw:.1f}', flush=True)
print('\nB. stopping rule: power at r = 2 vs families per bin (null = all 230 families pooled)')
allp = [f for v in F.values() for f in v]
for n in (25, 50, 100, 200):
    p, n_ok, cw = power(allp, n, n, 2.0, random.Random(SEED))
    print(f'n = {n:>3} families per bin  power {p:.2f}  ({n_ok} ok)  CI x{cw:.1f}', flush=True)
print('\nC. observed: log-ratio of KM medians for each adjacent pair on the real data, family bootstrap (2000 draws)')
rng = random.Random(SEED)
for a, b in zip(names, names[1:]):
    est = logratio(F[a], F[b]); out = []
    for _ in range(2000):
        x = logratio(draw(F[a], len(F[a]), rng), draw(F[b], len(F[b]), rng))
        if x is not None: out.append(x)
    out.sort(); lo, hi = out[int(.025 * len(out))], out[int(.975 * len(out))]
    print(f'{a:>8} -> {b:<8} ratio x{math.exp(est):.2f}  95% CI x{math.exp(lo):.2f} .. x{math.exp(hi):.2f}  '
          f'({len(out)} ok){"  excludes 1" if lo > 0 or hi < 0 else ""}', flush=True)
