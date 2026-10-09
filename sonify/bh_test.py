"""#207: Benjamini-Hochberg across each day's signal z-scores as the badge rule.
Each signal: robust z of today against its own 30 days (same zser as badge_test.py).
Two ways to turn |z| into a p-value:
  (N) normal tail 2*(1-Phi(|z|)) -- assumes Gaussian noise, which these series are not;
  (E) pooled empirical null: share of all signals' |z| on the 29 earlier days of the window that are >= today's |z|
      (Efron-style empirical null; the series are heavy-tailed, so their own past is the honest yardstick).
BH at q=0.10 over all signals of the day. Compare with the site's flags and the family-max survivors (4/11)."""
import json, math, numpy as np, datetime as dt, sys
sys.path.insert(0, 'lab/sonify')
Q = 0.10
def zser(series, days):
    idx = {x: i for i, x in enumerate(days)}; v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    for i in range(1, 30):
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med)) or (np.std(v[ok]) or 1.0)
    return np.nan_to_num((v - med) / mad)
def bh(p, q=Q):
    p = np.asarray(p); n = len(p); o = np.argsort(p); thr = q * np.arange(1, n + 1) / n
    passed = np.nonzero(p[o] <= thr)[0]; k = passed.max() + 1 if len(passed) else 0
    keep = np.zeros(n, bool); keep[o[:k]] = True; return keep
FAMMAX = {('2026-10-08', 'ru martial'), }  # filled from badge_test output below for the comparison print
for day in sys.argv[1:] or ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08']:
    d = json.load(open(f'pulse/signals/{day}.json')); end = dt.date.fromisoformat(day)
    days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]
    ids, Z, flag = [], [], {}
    for s in d['signals']:
        z = zser(s.get('series') or [], days)
        flag[s['id']] = bool(s.get('anomaly'))
        if z is None: continue
        ids.append(s['id']); Z.append(z)
    Z = np.abs(np.vstack(Z)); today = Z[:, -1]; past = np.sort(Z[:, :-1].ravel())
    pN = np.array([math.erfc(x / math.sqrt(2)) for x in today])
    pE = np.array([(len(past) - np.searchsorted(past, x, 'left') + 1) / (len(past) + 1) for x in today])
    kN, kE = bh(pN), bh(pE)
    nflag = sum(flag.values()); untested = [i for i, f in flag.items() if f and i not in ids]
    print(f'== {day}: {len(ids)} signals with 30-day series; site flags {nflag} (untestable {len(untested)}); '
          f'BH q={Q}: normal-p {kN.sum()}, empirical-p {kE.sum()}; past pool n={len(past)}, its 99th pct |z| {np.percentile(past, 99):.1f}')
    for j in np.argsort(-today):
        if not (kN[j] or kE[j] or flag[ids[j]]): continue
        print(f'   {ids[j][:40]:40s} |z| {today[j]:6.1f}  pN {pN[j]:.1e} pE {pE[j]:.4f}  site {"F" if flag[ids[j]] else "."}  BH-N {"Y" if kN[j] else "."}  BH-E {"Y" if kE[j] else "."}')
