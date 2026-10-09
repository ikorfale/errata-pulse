"""deal-to-rule 80564: per day, how many of the series are at or above their own 3rd-highest day (strict top 3 of 30)
and how many have robust |z| >= 3. A count, not a sigma."""
import json, sys, numpy as np, datetime as dt
exec(open('sonify/chord_null.py').read().split('import os;')[0].split('"""',2)[2])
Z = [z for s in d['signals'] if (z := zser(s.get('series') or [])) is not None]
Z = np.vstack(Z); n = len(Z)
top = np.vstack([np.abs(r) >= np.sort(np.abs(r))[-3] for r in Z]).sum(axis=0)
big = (np.abs(Z) >= 3).sum(axis=0)
print('series n =', n)
for i, day in enumerate(days): print(day, 'top3:', int(top[i]), ' |z|>=3:', int(big[i]))
print('median top3/day', np.median(top), ' median |z|>=3/day', np.median(big))
