"""glitchfox 107756: share of clean episodes healed within 1-3 days, integer days, open episodes. Written 29.10, before 14:24 UTC (date -u of the next step)."""
import sys
from collections import defaultdict
import random
sys.argv=['x']; exec(open('censor_check.py').read().split("for name, sel in")[0])
src=open('family_weighted_km.py').read(); exec(src[src.index('def wkm'):src.index('for lab, Mf in')])
eps=[e for f in C.values() for e in f]
h=[e['days'] for e in eps if e['end'] is not None]; o=[e['days'] for e in eps if e['end'] is None]
print('clean families',len(C),'episodes',len(eps),'healed',len(h),'open',len(o))
print('integer-valued days:', sum(float(x).is_integer() for x in h+o), 'of', len(h+o), '; smallest healed', sorted(h)[:8])
for kk in (1,2,3,7,14): print(f'healed <= {kk} d: {sum(x<=kk for x in h)}/{len(h)} = {sum(x<=kk for x in h)/len(h):.2f}')
w=sum(sum(e['end'] is not None and e['days']<=3 for e in f)/len(f) for f in C.values())/len(C); print('family-weighted share of clean episodes healed <=3 d', round(w,3))
print('weighted KM median clean', wkm(C))
