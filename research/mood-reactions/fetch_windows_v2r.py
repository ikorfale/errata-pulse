#!/usr/bin/env python3
# data_v2r: re-fetch of data_v2 with parse_v2r (27.10, #536); otherwise identical to fetch_windows.py.
"""#514: fetch only the windows Mood v2 needs, per channel: [hour0 - 30 d, hour0 + 2 d] for every register event in the
channel's region (block -29 is the oldest baseline block; overlapping windows merged). Jumps into a channel's history
by bisecting on post id (t.me/s/CH?before=ID), then pages back as fetch.py does. Polite: 3 s between requests.
Writes data_v2/CHANNEL.jsonl and data_v2/coverage.tsv (posts and first/last time per window). Reads no reactions:
the coverage check (does the fetch reach past block -29?) needs times only, so it can run before the freeze."""
import json, os, sys, time, urllib.request, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_v2r import parse   # #536: keeps custom emoji and paid stars (fetch.parse dropped them)
D = os.path.dirname(os.path.abspath(__file__)); OUT = f'{D}/data_v2r'; os.makedirs(OUT, exist_ok=True)
CH = {'Smolensk': 'inc_smol', 'Bryansk': 'br_gorod', 'Crimea': 'chp_crimea', 'Ryazan': 'overheardryazan',
      'Tambov': 'tambov_smi', 'Belgorod': 'belgorod_granica', 'Kirov': 'kirov_bezcenz', 'Rostov': 'privet_rostov_ru',
      'Krasnodar': 'krasnodarkray1', 'Tatarstan': 'kazancity'}            # usernames-v2.tsv
GOV = {'anohin67': 'Smolensk', 'avbogomaz': 'Bryansk', 'Aksenov82': 'Crimea', 'pavelmalkov_official': 'Ryazan',
       'PervyshovEA': 'Tambov', 'aleksandr_shuvaev': 'Belgorod', 'aleksandrsokolov43': 'Kirov', 'Yuri_Slusar': 'Rostov',
       'kondratyevvi': 'Krasnodar', 'radmirbelyaev': 'Tatarstan'}          # vorobiev_live = Moscow obl: no channel, drops
ev = {}
for l in open(f'{D}/../mood/civ_verify_b.tsv').read().splitlines()[1:]:
    f = l.split('\t'); h = f[1].split('/')[3]; t0 = dt.datetime.fromisoformat(f[2][:25])
    if h in GOV: ev.setdefault(GOV[h], []).append((f[0], t0))
def get(ch, before=None):
    u = f'https://t.me/s/{ch}' + (f'?before={before}' if before else '')
    r = urllib.request.Request(u, headers={'User-Agent': 'errata-research/1.0 (AI agent; errata@agentmail.to)'})
    for k in range(3):
        try: h = urllib.request.urlopen(r, timeout=30).read().decode('utf-8', 'replace'); time.sleep(3); return parse(h)[0]
        except Exception as e: print('retry', ch, before, e, flush=True); time.sleep(20)
    return []
T = lambda p: dt.datetime.fromisoformat(p['time'])
only = [a for a in sys.argv[1:] if '=' not in a]
for a in sys.argv[1:]:                                   # Region=username: fetch another channel for that region
    if '=' in a: r, u = a.split('=', 1); CH[r] = u; only.append(u)
for reg, ch in CH.items():
    if only and ch not in only: continue
    wins = sorted((t - dt.timedelta(days=30), t + dt.timedelta(days=2)) for _, t in ev.get(reg, []))
    merged = []
    for a, b in wins:
        if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
        else: merged.append([a, b])
    top = get(ch); hi = max(p['id'] for p in top) + 1; rows = {}
    cov = []
    for a, b in merged:
        lo, h2 = 1, hi                                   # smallest id whose page (posts before it) ends after b
        while h2 - lo > 20:
            mid = (lo + h2) // 2; ps = get(ch, mid)
            if not ps: lo = mid; continue
            if max(T(p) for p in ps) > b: h2 = mid
            else: lo = mid
        before, n0, oldest = h2 + 20, len(rows), None
        for page in range(1500):
            ps = get(ch, before)
            if not ps: break
            for p in ps: rows[p['id']] = p
            oldest = min(T(p) for p in ps); before = min(p['id'] for p in ps)
            if oldest < a: break
        inwin = [p for p in rows.values() if a <= T(p) <= b]
        cov.append((reg, ch, a.isoformat()[:16], b.isoformat()[:16], len(inwin), oldest.isoformat()[:16] if oldest else '',
                    'reaches_start' if oldest and oldest < a else 'SHORT'))
        print(*cov[-1], flush=True)
    with open(f'{OUT}/{ch}.jsonl', 'w') as f:
        for i in sorted(rows): f.write(json.dumps(rows[i], ensure_ascii=False) + '\n')
    with open(f'{OUT}/coverage.tsv', 'a') as f:
        for c in cov: f.write('\t'.join(map(str, c)) + '\n')
