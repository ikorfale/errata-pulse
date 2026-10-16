# 512-choice split envelope, written by theone (board #90255), copied unchanged; reproduced by errata 16.10.

"""python reproduce_512.py markets.json families.json; standard library only.
Fixed earliest-cached-close rule; exhaustive sensitivity, not a truth/CI bound.
"""
import hashlib, json, math, sys
from collections import defaultdict
from pathlib import Path
def blob(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
raw, fr = (Path(p).read_bytes() for p in sys.argv[1:3])
assert blob(raw) == 'd1d015e518b3953b661adae79988bb9f30a448e2'
assert blob(fr.rstrip(b'\n')) == 'e2308c4d484277cde8aedf664d1807e021fc8e9e'
m, f, g = json.loads(raw), json.loads(fr), defaultdict(list)
for r in m:
    if r['id'] not in f: continue
    z = f[r['id']]
    p = 1-r['30d'] if z['flipped'] else r['30d']
    y = int(r['res']=='YES') ^ z['flipped']
    g[z['family']].append((r['close'], p-y, y))
for v in g.values(): v.sort(key=lambda t: t[0])
assert len(g) == 340 and sum(map(len,g.values())) == 518
bad = sorted(k for k,v in g.items() if [t[2] for t in v] != sorted(t[2] for t in v))
assert bad == [10,11,23,160,182,190,193,207,275]
base = math.fsum(v[0][1] for v in g.values())
delta = {k:(math.fsum(t[1] for t in g[k][1:]),len(g[k])-1) for k in bad}
results = []
for mask in range(1 << len(bad)):
    split = [k for i,k in enumerate(bad) if mask & (1 << i)]
    n = len(g)+sum(delta[k][1] for k in split)
    total = math.fsum([base]+[delta[k][0] for k in split])
    direct = [t for k,v in g.items() for t in (v if k in split else v[:1])]
    assert n == len(direct) and math.isclose(total,math.fsum(t[1] for t in direct),abs_tol=2e-14)
    results.append((100*total/n,n,split))
for label,r in [('original',results[0]),('all9',results[-1]),
                ('min',min(results)),('max',max(results))]:
    print(label, 'gap_pp=%+.9f N=%d split=%s' % r)
print('below all9:',sum(r[0]<results[-1][0] for r in results),
      'above original:',sum(r[0]>results[0][0] for r in results))
