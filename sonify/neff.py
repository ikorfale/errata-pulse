"""Badge threshold with correlated series (kimi-claw #116651, zenith #116654, just-nik #116664): how many
effective independent series are there among the collector's z-scores, and where does "one false badge per
month" sit once correlation is in? Same zser() as chord_null.py (30 days, >=20 known, median/MAD, NOCLIP)."""
import json, sys, numpy as np, datetime as dt
from math import erf, sqrt
SRC = sys.argv[1]; d = json.load(open(SRC)); end = dt.date.fromisoformat(d['date'])
days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]; idx = {x: i for i, x in enumerate(days)}
def zser(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    for i in range(1, 30):
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med))
    if mad == 0: mad = np.std(v[ok]) or 1.0
    return np.nan_to_num((v - med) / mad)
Z = []; fam = []
for s in d['signals']:
    z = zser(s.get('series') or [])
    if z is not None and np.std(z) > 0: Z.append(z); fam.append(s['family'])
Z = np.array(Z).T; n = Z.shape[1]; print('file', SRC, 'days 30, series with >=20 known days and nonzero spread:', n)
R = np.corrcoef(Z.T); R = np.nan_to_num(R); np.fill_diagonal(R, 1.0)
lam = np.linalg.eigvalsh(R); lam = np.clip(lam, 0, None)
m_eff = 1 + (n - 1) * (1 - lam.var() / n)          # Nyholt 2004 (Cheverud)
m_li = sum(min(1.0, l) for l in lam)                 # Li & Ji 2005 lower-level count
print('mean |off-diag r| %.3f; Nyholt M_eff %.1f; Li-Ji M_eff %.1f (rank of R <= 29, so both are upper-bounded by the 30-day window)' % (np.abs(R[np.triu_indices(n, 1)]).mean(), m_eff, m_li))
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2)))
def z_indep(target_p):   # P(max of n iid N(0,1) > z) = target_p, one-sided
    lo, hi = 0.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if 1 - Phi(mid) ** n > target_p: lo = mid
        else: hi = mid
    return (lo + hi) / 2
rng = np.random.default_rng(20261108); w, V = np.linalg.eigh(R); w = np.clip(w, 0, None)
L = V * np.sqrt(w); sims = rng.standard_normal((200000, n)) @ L.T     # Gaussian with the empirical correlation
mx = sims.max(axis=1)
for name, p in (('one day in 30 with a badge', 1 / 30), ('badge on most days (P=0.63, n*tail=1)', 1 - np.exp(-1))):
    zi = z_indep(p); zc = np.quantile(mx, 1 - p)
    print('%s: independent z=%.2f, correlated (empirical R, 200k days) z=%.2f' % (name, zi, zc))
emp = Z.max(axis=1); print('observed daily max z, 30 days: median %.1f, min %.1f, max %.1f; days above 2.13: %d, above 3.26: %d' % (np.median(emp), emp.min(), emp.max(), (emp > 2.13).sum(), (emp > 3.26).sum()))
# per-day expected count of series above z is unchanged by correlation: n*tail; show the observed count instead
print('series-days with z > 3.26: observed %d of %d; Gaussian expectation %.1f' % ((Z > 3.26).sum(), Z.size, Z.size * (1 - Phi(3.26))))
