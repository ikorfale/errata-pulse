"""Does FIRMS sensitivity depend on depth from the Ukrainian border? (scout, 94942)"""
import sys, io, contextlib
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'alert-depth-2026-10-19'))
with contextlib.redirect_stdout(io.StringIO()):
    import evaluate as E
_here = os.getcwd(); os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'alert-depth-2026-10-19'))
from depth import depth
os.chdir(_here)
for name in ('R0 current (20 km, 2 sats, mean+3sd)', 'R2 5 km, 3 sats, Poisson p<0.01'):
    r = E.RULES[name]; rows = []
    for e, v in E.data:
        if not E.is_pos(e): continue
        f = E.flag(r, v, r['w'])
        if f is None: continue
        rows.append((depth((float(e['lat']), float(e['lon']))), f, e['site_key']))
    rows.sort()
    for lo, hi in ((0, 300), (300, 600), (600, 5000)):
        b = [f for d, f, _ in rows if lo <= d < hi]
        print(f'{name[:3]} depth {lo}-{hi} km: flagged {sum(b)}/{len(b)}')
    print(name[:3], 'flagged depths', [round(d) for d, f, _ in rows if f])
