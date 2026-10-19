#!/usr/bin/env python3
"""Fetch VIIRS fire detections (S-NPP, NOAA-20, NOAA-21) within ~25 km of each ground-truth facility,
from day-33 to day+3 around the attack date. Raw rows cached per (site, date) in raw/, so every
detection rule is evaluated offline afterwards (evaluate.py). SP archive up to 2026-06-30, NRT after."""
import csv, datetime as dt, io, json, math, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
KEY = os.environ['FIRMS_MAP_KEY']   # free NASA FIRMS map key
SP_END = dt.date(2026, 6, 30)
SATS = ('SNPP', 'NOAA20', 'NOAA21')
os.makedirs(os.path.join(HERE, 'raw'), exist_ok=True)

def sources(sat, start):
    """SP while the chunk starts inside the archive; NRT too when the chunk reaches past it."""
    out = [f'VIIRS_{sat}_SP'] if start <= SP_END else []
    if start + dt.timedelta(days=4) > SP_END: out.append(f'VIIRS_{sat}_NRT')
    return out

def fetch(lat, lon, d0):
    dl = 0.23; dn = dl / max(0.2, math.cos(math.radians(lat)))
    box = f'{lon - dn:.3f},{lat - dl:.3f},{lon + dn:.3f},{lat + dl:.3f}'
    rows, chunks = [], []
    for sat in SATS:
        for j in range(8):   # 8 x 5 days: day-33 .. day+6
            start = d0 - dt.timedelta(days=33 - 5 * j)
            if start > dt.date.today(): break
            for src in sources(sat, start):
                url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{KEY}/{src}/{box}/5/{start}'
                for attempt in range(3):
                    try:
                        txt = urllib.request.urlopen(url, timeout=90).read().decode(); break
                    except Exception as e:
                        err = str(e).replace(KEY, '<key>'); time.sleep(5)
                else:
                    print('FAIL', src, start, err, file=sys.stderr); chunks.append([sat, src, str(start), 'ERR']); continue
                if not txt.startswith('latitude'):
                    chunks.append([sat, src, str(start), 'ERR ' + txt[:60].replace(KEY, '<key>')]); continue
                n = 0
                for r in csv.DictReader(io.StringIO(txt)):
                    r['sat'] = sat; r['src'] = src; rows.append(r); n += 1
                chunks.append([sat, src, str(start), n])
                time.sleep(0.4)
    return {'rows': rows, 'chunks': chunks}

gt = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'groundtruth.jsonl')) if l.strip()]
for i, e in enumerate(gt):
    out = os.path.join(HERE, 'raw', f"{e['site_key']}_{e['date']}.json")
    if os.path.exists(out): continue
    got = fetch(float(e['lat']), float(e['lon']), dt.date.fromisoformat(e['date']))
    json.dump(got, open(out, 'w'))
    print(i + 1, len(gt), e['site_key'], e['date'], len(got['rows']), sum(1 for c in got['chunks'] if str(c[3]).startswith('ERR')), 'errors', flush=True)
