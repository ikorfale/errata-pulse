"""Regression for top3 (theone 82399): unknown (-inf) days never peak; 0/1/2/3 known days; finite ties at the cut."""
import os, sys, types, numpy as np, re
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chord_null.py')).read()
ns = {'np': np, 'OBS': False}; exec(re.search(r'def top3\(row\):.*?\n(?=\S)', src, re.S).group(0), ns); top3 = ns['top3']
I = -np.inf
for k in range(4):
    r = np.full(30, I); r[:k] = 0.0
    t = top3(r); assert not t[k:].any(), k; assert t.sum() == (3 if k == 3 else 0), (k, t.sum())
r = np.array([5, 3, 3, 3, 1, I]); assert top3(r).tolist() == [True, True, True, True, False, False]   # ties at the cut count
# theone's fixture: 3 families, each finite on one day -> 0 chord days
M = np.full((3, 30), I); M[0, 0] = M[1, 1] = M[2, 2] = 0
assert (np.vstack([top3(x) for x in M]).sum(0) >= 3).sum() == 0
print('top3 regressions: ok')
