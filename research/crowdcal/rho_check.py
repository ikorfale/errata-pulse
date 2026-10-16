"""Common shocks between question families (glitchfox, board 89994).

glitchfox: with 196 independent families (embedding tau=0.8) the sub-10% bin's "0 YES" has P=1.05e-4 under
calibration, but a one-factor latent "escalation regime" with between-family tetrachoric rho of only ~0.064
lifts it above 1e-2. Proposed test: estimate rho from the residuals blocked by (actor, close-month).

Problem with doing it inside the sub-10% bin: every outcome there is NO, so residuals are just -price and say
nothing about rho. rho has to come from families across the whole price range, where YES outcomes exist.

What this does, on the pinned markets.json, no refetch:
1. Families = embedding average-linkage clusters at tau=0.8 (embed_check.py). One binary per family: its
   earliest-closing market (price 30 days before close, outcome).
2. Blocks = shared shock: (search term, close month) of that market; also month-only and term-only blocks.
3. One-factor probit: family c in block b resolves YES iff sqrt(rho)*Z_b + sqrt(1-rho)*e_c < Phi^-1(p_c) + d,
   Z_b, e_c ~ N(0,1). d is a free probit shift (the crowd's miscalibration), so rho is not asked to explain the
   gap. Likelihood integrated over Z_b by Gauss-Hermite; rho profiled on a grid, d optimised; 95% CI by the
   likelihood-ratio rule (drop of 1.92).
4. Reproduce glitchfox's equicorrelated table, then P(0 YES) in the sub-10% bin under the fitted rho with the
   real block structure (families in different blocks independent), for d=0 (calibrated) and d fitted.
Needs scipy (run with ~/venv/bin/python).
"""
import contextlib, io, os, sys
from collections import defaultdict
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar

sys.argv = sys.argv[:1]
with contextlib.redirect_stdout(io.StringIO()):
    import embed_check as EC
L, C = EC.L, EC.C
R, x, y = EC.R, EC.x, EC.y
low = EC.low
# FLIP=1: five titles in the escalation group are asked the peace way round ("China will not launch ...",
# "No nuclear weapon use?"); flip their price and outcome so every question points the escalation way.
INVERTED = ('China will not launch a full-scale invasion of Taiwan', 'Will no non-test nuclear weapons be detonated',
            'International affairs 2023: No nuclear weapon use', 'International affairs 2023: No Chinese attack on Taiwan',
            'Will November 2024 pass with no missile alarms in Haifa')
inv = [i for i, r in enumerate(R) if r['q'].startswith(INVERTED)]
if os.environ.get('FLIP', '1') == '1':  # default: escalation coding (Fable review)
    x = x.copy(); y = y.copy()
    x[inv] = 1 - x[inv]; y[inv] = 1 - y[inv]
    low = x < 0.10
print(f'inverted titles found: {len(inv)}; flipped: {os.environ.get("FLIP", "1") == "1"}')
g = L.hier_groups(R, EC.SE, 0.8, 'average')
G = L.groups_of(g)
close = np.array([r['close'] for r in R])
first = np.array([v[np.argmin(close[v])] for v in G])
print(f'families (tau=0.8, average linkage): {len(G)}; earliest-rung YES: {int(y[first].sum())}; '
      f'mean price {x[first].mean():.4f}')

GH_z, GH_w = np.polynomial.hermite_e.hermegauss(60)
GH_w = GH_w / GH_w.sum()


def block_ll(t, rho):
    """log P(outcomes in one block | thresholds t) integrated over the block shock."""
    t, yy = t
    s = np.sqrt(rho); u = np.sqrt(1 - rho)
    P = norm.cdf((t[:, None] - s * GH_z[None, :]) / u)  # P(YES | z)
    P = np.clip(P, 1e-300, 1 - 1e-16)
    lp = np.where(yy[:, None] == 1, np.log(P), np.log1p(-P)).sum(0)
    m = lp.max()
    return m + np.log((GH_w * np.exp(lp - m)).sum())


def blocks_of(idx, key):
    by = defaultdict(list)
    for i in idx:
        by[key(R[i])].append(i)
    return [np.array(v) for v in by.values()]


def nll(rho, d, B):
    return -sum(block_ll((norm.ppf(np.clip(x[b], 1e-4, 1 - 1e-4)) + d, y[b]), rho) for b in B)


def fit(B, label):
    grid = np.round(np.arange(0, 0.951, 0.025), 3)
    prof = []
    for rho in grid:
        r = minimize_scalar(lambda d: nll(rho, d, B), bounds=(-2, 2), method='bounded')
        prof.append((rho, r.fun, r.x))
    best = min(prof, key=lambda p: p[1])
    inside = [p[0] for p in prof if p[1] - best[1] <= 1.92]
    sizes = np.array([len(b) for b in B])
    print(f'{label:<22} blocks {len(B):4d} (with >=2 families: {int((sizes >= 2).sum())}, largest {sizes.max()}) '
          f'rho_hat {best[0]:.2f}  95% CI [{min(inside):.2f}, {max(inside):.2f}]{"+" if max(inside) >= grid[-1] else ""}  '
          f'd_hat {best[2]:+.3f}  (-2 dLL at rho=0: {2 * (prof[0][1] - best[1]):.2f})')
    return best, min(inside), max(inside)


month = lambda r: C.month(r)
keys = {'term x close-month': lambda r: (r['term'], month(r)), 'close-month': month, 'term': lambda r: r['term']}
fits = {k: fit(blocks_of(first, f), k) for k, f in keys.items()}

# sub-10% bin, as estimators(): cluster-level mean price of the bin's markets; block from its earliest low market
lowG = [v[low[v]] for v in G]
lowG = [v for v in lowG if len(v)]
pc = np.array([x[v].mean() for v in lowG])
anyyes = sum(int(y[v].max()) for v in lowG)
rep = [v[np.argmin(close[v])] for v in lowG]
print(f'\nsub-10% families: {len(pc)}, YES among them: {anyyes}, mean p {pc.mean():.4f}, independent P(0 YES) {np.prod(1 - pc):.2e}')


def p_zero(rho, d, key):
    by = defaultdict(list)
    for p, i in zip(pc, rep):
        by[key(R[i]) if key else 0].append(p)
    lp = 0.0
    for ps in by.values():
        t = norm.ppf(np.array(ps)) + d
        P0 = 1 - norm.cdf((t[:, None] - np.sqrt(rho) * GH_z[None, :]) / np.sqrt(1 - rho))
        lp += np.log((GH_w * np.exp(np.log(np.clip(P0, 1e-300, 1)).sum(0))).sum())
    return np.exp(lp)


print('\nglitchfox check, one shock shared by all families (homogeneous p replaced by the real p_c):')
for rho in (0, 0.02, 0.05, 0.064, 0.10):
    print(f'  rho {rho:.3f}  P(0 YES) {p_zero(rho, 0, None):.2e}')
print('\nwith the fitted rho and its CI, shocks shared only inside a block:')
for k, (best, lo, hi) in fits.items():
    for d, dl in ((0.0, 'calibrated d=0'), (best[2], f'fitted d={best[2]:+.3f}')):
        vals = ' '.join(f'{p_zero(r, d, keys[k]):.2e}' for r in (lo, best[0], hi))
        print(f'  {k:<20} {dl:<18} P(0 YES) at rho lo/hat/hi: {vals}')

# which close-months carry the shock: families and YES per month, top 6 by YES
by = defaultdict(list)
for i in first:
    by[month(R[i])].append(i)
top = sorted(by.items(), key=lambda kv: -y[kv[1]].sum())[:6]
print('\nclose-months with most YES families (month = close // 30 days; first YES title shown):')
for m, v in top:
    v = np.array(v); yi = v[y[v] == 1]
    import datetime
    d0 = datetime.datetime.fromtimestamp(close[v].min() / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
    print(f'  {d0}  families {len(v):3d}  YES {len(yi):2d}  expected {x[v].sum():5.2f}  e.g. {R[yi[0]]["q"][:70]}')

# does the crowd's overpricing survive the shock? profile the probit shift d (LR 95% CI) with rho fixed
print('\nprobit shift d (negative = crowd overprices YES), LR 95% CI, rho fixed:')
for k, (best, lo, hi) in fits.items():
    B = blocks_of(first, keys[k])
    for rho in sorted({0.0, best[0]}):
        ds = np.round(np.arange(-0.6, 0.31, 0.01), 2)
        f = np.array([nll(rho, d, B) for d in ds])
        ok = ds[f - f.min() <= 1.92]
        print(f'  {k:<20} rho {rho:.2f} fixed: d_hat {ds[f.argmin()]:+.2f} [{ok.min():+.2f}, {ok.max():+.2f}]')
    # profile CI: rho optimised at each d (Fable: the fixed-rho interval is conditional)
    ds = np.round(np.arange(-0.6, 0.31, 0.02), 2)
    f = np.array([minimize_scalar(lambda r: nll(r, d, B), bounds=(0, 0.95), method='bounded').fun for d in ds])
    ok = ds[f - f.min() <= 1.92]
    print(f'  {k:<20} rho profiled: d_hat {ds[f.argmin()]:+.2f} [{ok.min():+.2f}, {ok.max():+.2f}]')

# model-free check: earliest-rung gap (price - outcome), bootstrap resampling families vs whole close-month blocks
er = x[first] - y[first]
rng = np.random.default_rng(7)
print(f'\nearliest-rung gap {100 * er.mean():+.2f} pp over {len(first)} families; 95% bootstrap interval:')
for k in ('family', 'close-month', 'term x close-month'):
    B = [np.arange(len(first))[:, None][i] for i in range(len(first))] if k == 'family' else \
        [np.array([j for j, i in enumerate(first) if keys[k](R[i]) == kk]) for kk in {keys[k](R[i]) for i in first}]
    bs = []
    for _ in range(4000):
        j = rng.integers(0, len(B), len(B))
        v = np.concatenate([B[t] for t in j]); bs.append(er[v].mean())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f'  resample {k:<20} ({len(B):3d} units): [{100 * lo:+.2f}, {100 * hi:+.2f}]')

# quadrature check: 60 vs 120 Gauss-Hermite nodes, biggest block, high rho
Bm = blocks_of(first, keys['close-month'])
a = nll(0.9, -0.1, Bm)
GH_z, GH_w = np.polynomial.hermite_e.hermegauss(120); GH_w = GH_w / GH_w.sum()
print(f'\nquadrature: nll at rho 0.9 with 60 nodes {a:.4f}, with 120 nodes {nll(0.9, -0.1, Bm):.4f}')

# where the gap lives: price bins, and leave-one-close-month-out (Fable: lumpy 49-unit bootstrap)
lo10 = x[first] < 0.10
print(f'\ngap by price: sub-10% {lo10.sum()} families, YES {int(y[first][lo10].sum())}, expected {x[first][lo10].sum():.2f}, '
      f'gap {100 * er[lo10].mean():+.2f} pp; >=10% {(~lo10).sum()} families, YES {int(y[first][~lo10].sum())}, '
      f'expected {x[first][~lo10].sum():.2f}, gap {100 * er[~lo10].mean():+.2f} pp')
mk = np.array([month(R[i]) for i in first])
loo = []
for m in set(mk):
    keep = mk != m
    loo.append((er[keep].mean(), m, int((~keep).sum())))
loo.sort()
import datetime
dd = lambda m: datetime.datetime.fromtimestamp(close[first][mk == m].min() / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
print('leave one close-month out, gap pp: min {:+.2f} (drop {} , {} families), max {:+.2f} (drop {}, {} families)'.format(
    100 * loo[0][0], dd(loo[0][1]), loo[0][2], 100 * loo[-1][0], dd(loo[-1][1]), loo[-1][2]))
big = max(set(mk), key=lambda m: (mk == m).sum())
keep = mk != big
print(f'drop the biggest block ({dd(big)}, {int((~keep).sum())} families): gap {100 * er[keep].mean():+.2f} pp; '
      f'sub-10% gap without it {100 * er[keep & lo10].mean():+.2f}, >=10% {100 * er[keep & ~lo10].mean():+.2f}')
