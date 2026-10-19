"""Second source for alert depth (claude-sonnet-scout, board 94786): Exilenova+ strike posts, days 8-14 of each month.
Each post (deduplicated on its first 60 characters) is anchored at the first Russian place or region it names
(geo cache pulse/drones/geo.json; Ukrainian spellings normalised: i->и, doubled letters collapsed, stems).
Occupied regions excluded. Per month: n anchored posts, share beyond 300 / 600 km, a band from a bootstrap over days.
Compared with alert posts (events_sample.jsonl) on the same days."""
import json, re, random, collections, datetime as dt
import importlib.util
spec = importlib.util.spec_from_file_location('depth', 'depth.py'); D = importlib.util.module_from_spec(spec)
src = open(spec.origin).read(); exec(compile(src, 'depth.py', 'exec'), D.__dict__)
def norm(s): return re.sub(r'(.)\1', r'\1', s.lower().replace('і', 'и').replace('ї', 'и').replace('є', 'е').replace('ё', 'е').replace("'", '').replace('’', ''))
def st(w): w = norm(w); return w[:max(5, len(w) - 2)]
LOC = {}
for k, ll in D.geo.items():
    if not ll or any(o in k for o in D.OCC): continue
    name = k.split(',')[0].replace(' и близлежащие', '').strip()
    if ', ' in k and len(name) >= 5 and ' ' not in name: LOC.setdefault(st(name), ll)
for s, r in D.STEMS:
    if not any(o in r for o in D.OCC): LOC.setdefault(norm(s), D.geo[r])
STEMS = sorted(LOC, key=len, reverse=True)
seen, by = set(), collections.defaultdict(list)
import glob
for l in (l for f in sorted(glob.glob('exilenova/posts*.jsonl')) for l in open(f)):   # second fetcher wrote posts_b.jsonl; duplicates drop by text key
    p = json.loads(l); key = p['text'][:60]
    if not key or key in seen: continue
    seen.add(key); t = re.sub(r'москов[иы]т\w*|московщ\w*', '', norm(p['text']))   # 'Muscovites' = Russians in general, not Moscow (sample check 19.10: 1 of 14 false)
    hits = [(t.find(s), s) for s in STEMS if re.search(r'(?<![а-я])' + re.escape(s), t)]
    if not hits: continue
    pos = min(h[0] for h in hits); s = max((h for h in hits if h[0] == pos), key=lambda h: len(h[1]))[1]
    by[p['time'][:7]].append((p['time'][:10], D.depth(LOC[s]), s))
A = collections.defaultdict(list)   # alert posts on the same days (8-14 of each month), same anchors and depth
for ts, d, reg in D.rows('events_sample.jsonl')[0]:
    if 8 <= int(ts[8:10]) <= 14: A[ts[:7]].append(d)
random.seed(1); out = {}
for mo in sorted(by):
    rows = by[mo]; days = sorted({r[0] for r in rows}); f = lambda rs, km: sum(r[1] > km for r in rs) / len(rs)
    boots = sorted(f([r for d in random.choices(days, k=len(days)) for r in rows if r[0] == d] or rows, 300) for _ in range(2000))
    out[mo] = {'n': len(rows), 'gt300': round(f(rows, 300), 3), 'band300': [round(boots[50], 3), round(boots[1949], 3)],
               'gt600': round(f(rows, 600), 3), 'alert_n': len(A[mo]), 'alert_gt300': round(sum(x > 300 for x in A[mo]) / len(A[mo]), 3) if A[mo] else None,
               'top': collections.Counter(r[2] for r in rows).most_common(4)}
    o = out[mo]; print(mo, o['n'], o['gt300'], o['band300'], o['gt600'], 'alerts', o['alert_gt300'], o['top'])
json.dump(out, open('exilenova/depth_monthly.json', 'w'), ensure_ascii=False, indent=1)
