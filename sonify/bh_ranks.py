"""gpb 81018: for each day, the smallest empirical p-values (plus-one) against the BH step-up thresholds q*k/m,
and how many past pooled cells are >= today's |z| for each. Same zser/pE as bh_test.py."""
import sys, json, datetime as dt, numpy as np
sys.argv = sys.argv[:1]
import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bh_test.py')).read().split('FAMMAX')[0]
exec(src)
for day in ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08']:
    d = json.load(open(f'pulse/signals/{day}.json')); end = dt.date.fromisoformat(day)
    days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]
    ids, Z = [], []
    for s in d['signals']:
        z = zser(s.get('series') or [], days)
        if z is None: continue
        ids.append(s['id']); Z.append(z)
    Z = np.abs(np.vstack(Z)); today = Z[:, -1]; past = np.sort(Z[:, :-1].ravel()); m = len(ids); n = len(past)
    ge = np.array([n - np.searchsorted(past, x, 'left') for x in today]); pE = (ge + 1) / (n + 1)
    o = np.argsort(pE); thr = Q * np.arange(1, m + 1) / m
    passing = [k + 1 for k in range(m) if pE[o[k]] <= thr[k]]
    print(f'== {day}: m={m} pool n={n}; min possible p {1/(n+1):.5f}; first threshold {thr[0]:.5f}; ranks passing: {passing or "none"}')
    for k in range(5):
        j = o[k]
        print(f'   rank {k+1}: {ids[j][:38]:38s} |z| {today[j]:5.1f}  past cells >= {ge[j]:3d}  p {pE[j]:.5f}  thr {thr[k]:.5f}  ratio {pE[j]/thr[k]:.1f}')
