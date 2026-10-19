"""compare.py REPLAY T0: per 5-min step from T0, official region state vs replayed map state (any alert = uav or missile)."""
import json, sys, datetime as dt
R = json.load(open(sys.argv[1])); O = json.load(open('official.json')); T0 = sys.argv[2]
P = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
def on(iv, t): return any(P(a) <= t < P(b) for a, b in iv)
for iso, o in O.items():
    if iso.startswith('_'): continue
    n = agree = miss = false = 0; onsets = []; prev_map = prev_off = None; lag_on = []; lag_off = []
    steps = sorted(k for k in R if k >= T0)
    for k in steps:
        t = P(k); off = on(o['uav'] + o['missile'], t); m = iso in R[k] and not R[k][iso]['stale']
        n += 1; agree += off == m; miss += off and not m; false += m and not off
    # latency: first map step showing alert after official onset / first map-off step after official end
    for a, b in o['uav']:
        if P(a) < P(T0): continue
        first = next((k for k in steps if P(k) >= P(a) and iso in R[k]), None)
        lag_on.append(None if not first else round((P(first) - P(a)).total_seconds() / 60))
    for a, b in o['uav']:
        if P(b) < P(T0): continue
        first = next((k for k in steps if P(k) >= P(b) and iso not in R[k]), None)
        lag_off.append(None if not first else round((P(first) - P(b)).total_seconds() / 60))
    print(f"{iso} steps {n}  agree {agree} ({100*agree/n:.0f}%)  missed {miss} ({miss*5} min)  false {false} ({false*5} min)  onset lag min {lag_on}  clear lag min {lag_off}")
