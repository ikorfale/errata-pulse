#!/usr/bin/env python3
"""Score fire-detection rules on ground-truth strikes (raw/ from fetch.py). Rules: RULES.md.
v2 (before scoring, after a second-model review): local solar dates, other claimed strikes at the
same site masked from baselines and quiet windows, missing chunks never read as zero, Poisson tail in
log space, quiet windows deduplicated by site and absolute dates, coordinate offset check.
  sensitivity  = share of fire-confirmed strikes flagged (primary: R0 vs R2),
  no-fire      = flag rate on 'repelled, no fire' cases (descriptive: not a verified absence),
  quiet rate   = flag rate on distinct quiet windows before strikes (upper bound on false alarms)."""
import datetime as dt, glob, json, math, os, statistics as st, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
gt = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'groundtruth.jsonl')) if l.strip()]
D = dt.date.fromisoformat

# every claimed strike date per site: ground truth (all) + my collector's claims since 2026-08-31
claims = defaultdict(set)
for e in gt: claims[e['site_key']].add(D(e['date']))
hist = os.path.join(HERE, 'claims.jsonl')   # collector claims (site, date), optional
if os.path.exists(hist):
    for l in open(hist):
        h = json.loads(l)
        for s in h.get('sites', {}): claims[s].add(D(h['date']))

def load(e):
    p = os.path.join(HERE, 'raw', f"{e['site_key']}_{e['date']}.json")
    if not os.path.exists(p): return None
    raw = json.load(open(p))
    if isinstance(raw, list): raw = {'rows': raw, 'chunks': []}
    lat0, lon0 = float(e['lat']), float(e['lon'])
    seen, rows = set(), []
    for r in raw['rows']:
        k = (r['sat'], r['acq_date'], r['acq_time'], r['latitude'], r['longitude'])
        if k in seen: continue
        seen.add(k)
        r['km'] = math.hypot((float(r['latitude']) - lat0) * 111.2, (float(r['longitude']) - lon0) * 111.2 * math.cos(math.radians(lat0)))
        r['frp'] = float(r.get('frp') or 0)
        t = dt.datetime.fromisoformat(r['acq_date']) + dt.timedelta(hours=int(r['acq_time']) // 100, minutes=int(r['acq_time']) % 100)
        r['local'] = (t + dt.timedelta(hours=float(r['longitude']) / 15)).date()   # local solar date
        rows.append(r)
    d0 = D(e['date'])
    bad = defaultdict(set)   # sat -> day offsets with no data
    for sat, src, start, n in raw['chunks']:
        if str(n).startswith('ERR'):
            for i in range(5): bad[sat].add((D(start) + dt.timedelta(days=i) - d0).days)
    # a day is missing if any satellite whose other chunks returned has an error there and no other source covered it
    ok_days = defaultdict(set)
    for sat, src, start, n in raw['chunks']:
        if not str(n).startswith('ERR'):
            for i in range(5): ok_days[sat].add((D(start) + dt.timedelta(days=i) - d0).days)
    missing = {o for sat in bad for o in bad[sat] if o not in ok_days[sat]}
    masked = {(c - d0).days + j for c in claims[e['site_key']] if c != d0 for j in range(-1, 4)}
    return dict(rows=rows, missing=missing, masked=masked, d0=d0, site=e['site_key'])

def daily(ev, km, sats, key='n'):
    out = defaultdict(float)
    for r in ev['rows']:
        if r['km'] > km or r['sat'] not in sats: continue
        off = (r['local'] - ev['d0']).days
        if key == 'n': out[off] += 1
        else: out[off] = max(out[off], r['frp'])
    return out

def pois_sf(k, lam):   # P(X >= k), log space
    if k <= 0: return 1.0
    lam = max(lam, 0.05)
    terms = [math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1)) for i in range(int(k))]
    return max(0.0, 1 - sum(terms))

def baseline_days(ev, w):
    return [o for o in range(-32, -2) if o not in w and o not in ev['masked'] and o not in ev['missing']]

def flag(rule, ev, w):
    """None = cannot judge (window has missing data or baseline too thin)."""
    if any(o in ev['missing'] for o in w): return None
    bd = baseline_days(ev, w)
    if len(bd) < 15: return None
    if rule['kind'] in ('sd', 'pois', 'any'):
        c = daily(ev, rule['km'], rule['sats'])
        x = sum(c[o] for o in w); b = [c[o] for o in bd]; m = st.mean(b)
        if rule['kind'] == 'sd': return x >= 3 and x / len(w) >= m + 3 * max(st.pstdev(b), 0.5)
        if rule['kind'] == 'pois': return x >= 2 and pois_sf(x, m * len(w)) < rule['p']
        return x >= 1
    if rule['kind'] == 'frp':
        c = daily(ev, rule['km'], rule['sats'], key='frp')
        top = max(c[o] for o in w)
        return top > 0 and top > max([c[o] for o in bd] + [0])

ALL3 = ('SNPP', 'NOAA20', 'NOAA21'); TWO = ('SNPP', 'NOAA20')
RULES = {
    'R0 current (20 km, 2 sats, mean+3sd)': dict(kind='sd', km=20, sats=TWO, w=[0, 1]),
    'R1 current + NOAA-21': dict(kind='sd', km=20, sats=ALL3, w=[0, 1]),
    'R2 5 km, 3 sats, Poisson p<0.01': dict(kind='pois', km=5, sats=ALL3, p=0.01, w=[0, 1]),
    'R3 5 km, 3 sats, brightest FRP of the month': dict(kind='frp', km=5, sats=ALL3, w=[0, 1]),
    'R4 R2 with window -1..+2': dict(kind='pois', km=5, sats=ALL3, p=0.01, w=[-1, 0, 1, 2]),
    'R5 any detection within 3 km': dict(kind='any', km=3, sats=ALL3, w=[0, 1]),
}

def wilson(k, n):
    if n == 0: return float('nan'), float('nan')
    p, z = k / n, 1.96; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)

def is_pos(e): return e.get('fire_confirmed') in (True, 'true')
data = [(e, load(e)) for e in gt]
data = [(e, v) for e, v in data if v is not None]
circ = [e for e, v in data if e.get('cites_satellite') in (True, 'true')]
data = [(e, v) for e, v in data if e.get('cites_satellite') not in (True, 'true')]   # circular: reported apart
print(f'excluded as circular (source cites satellite data): {len(circ)}')
print(f'ground truth: {sum(map(is_pos, gt))} fire-confirmed, {len(gt) - sum(map(is_pos, gt))} no-fire; raw for {len(data)}; '
      f'events with masked baseline days: {sum(1 for e, v in data if any(-32 <= o <= -3 for o in v["masked"]))}; with missing days: {sum(1 for e, v in data if v["missing"])}')

# coordinate check: centroid of baseline detections within 5 km vs stored point
off = []
for e, v in data:
    near = [r for r in v['rows'] if r['km'] <= 5 and (r['local'] - v['d0']).days < -2]
    if len(near) >= 3:
        la = st.mean(float(r['latitude']) for r in near); lo = st.mean(float(r['longitude']) for r in near)
        k = math.hypot((la - float(e['lat'])) * 111.2, (lo - float(e['lon'])) * 111.2 * math.cos(math.radians(la)))
        if k > 2: off.append(f"{e['site_key']} {e['date']}: detections centre {k:.1f} km from stored point")
print('coordinate offsets >2 km:', off or 'none')

res = {}
strata = defaultdict(lambda: defaultdict(list))
for name, r in RULES.items():
    hp, hn, quiet = [], [], {}
    for e, v in data:
        f = flag(r, v, r['w'])
        if f is None: continue
        (hp if is_pos(e) else hn).append(f)
        if is_pos(e): strata[name][e.get('size_class', 'unknown')].append(f)
        L = len(r['w'])
        for s in range(-31, -3 - L, L):
            w = list(range(s, s + L))
            if any(o in v['masked'] for o in w): continue
            key = (v['site'], tuple(v['d0'] + dt.timedelta(days=o) for o in w))
            if key in quiet: continue
            q = flag(r, v, w)
            if q is not None: quiet[key] = q
    lo, hi = wilson(sum(hp), len(hp))
    qs = len({k[0] for k in quiet})
    res[name] = dict(sens=[sum(hp), len(hp)], neg=[sum(hn), len(hn)], quiet=[sum(quiet.values()), len(quiet)], quiet_sites=qs,
                     by_size={k: [sum(x), len(x)] for k, x in strata[name].items()})
    print(f'{name:46s} sens {sum(hp):3d}/{len(hp):<3d} ({lo:.2f}-{hi:.2f})  no-fire {sum(hn):2d}/{len(hn):<3d}  '
          f'quiet {sum(quiet.values()):3d}/{len(quiet)} ({sum(quiet.values()) / max(1, len(quiet)):.3f}, {qs} sites)  by size {res[name]["by_size"]}')
json.dump(res, open(os.path.join(HERE, 'result.json'), 'w'), indent=1)
