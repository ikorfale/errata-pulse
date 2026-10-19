"""intervals.py REPLAY T0: contiguous runs where official and map disagree, with why (absent / stale)."""
import json, sys, datetime as dt
R = json.load(open(sys.argv[1])); O = json.load(open('official.json')); T0 = sys.argv[2]
P = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
on = lambda iv, t: any(P(a) <= t < P(b) for a, b in iv)
for iso, o in O.items():
    if iso.startswith('_'): continue
    run = None
    for k in sorted(x for x in R if x >= T0) + ['END']:
        if k == 'END': lab = None
        else:
            t = P(k); off = on(o['uav'] + o['missile'], t); s = R[k].get(iso)
            m = bool(s) and not s['stale']
            lab = None if off == m else ('missed:' + ('stale' if s else 'absent')) if off else 'false'
        if run and lab != run[0]: print(iso, run[0], run[1][5:16], '->', run[2][5:16], f'{(P(run[2]) - P(run[1])).seconds // 60 + 5} min'); run = None
        if lab and not run: run = [lab, k, k]
        elif lab: run[2] = k
