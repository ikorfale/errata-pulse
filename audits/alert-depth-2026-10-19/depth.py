"""How deep into Russia do drone alerts reach? For each alert post (danger/sighting/shootdown/air_defence), its anchor
(geocoded place, else region; cache pulse/drones/geo.json) and the distance to the nearest point of Ukraine's mainland
border facing Russia (Natural Earth 50m, Ukraine boundary points with lon>31.7, lat>46.9). Occupied regions excluded.
Per ISO week: n posts, share beyond 300 / 600 / 1000 km, 90th percentile depth."""
import json, math, sys, collections, datetime as dt
B = [(lat, lon) for lon, lat in json.load(open('ukr_boundary.json')) if lon > 31.7 and lat > 46.9]
geo = json.load(open('geo.json'))
OCC = ('Донецк', 'Луганск', 'Запорож', 'Херсон', 'Крым', 'Севастопол', 'ДНР', 'ЛНР')
def hav(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0]); dp = p2 - p1; dl = math.radians(b[1] - a[1])
    return 2 * 6371 * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
def depth(ll): return min(hav(ll, b) for b in B)
import re
REGS = [k for k, v in geo.items() if v and ', ' not in k and re.search(r'(область|край)$', k) and not any(o in k for o in ('Донецк', 'Луганск', 'Запорож', 'Херсон'))]
def stem(r):
    w = r.split()[0]; return w[:-4] if len(w) - 4 >= 5 else w[:-2]
STEMS = sorted(((stem(r), r) for r in REGS), key=lambda x: -len(x[0]))
FALLBACK = collections.Counter()
def clean_reg(reg):
    """Old posts: 'Орловская область  Опасность по БПЛА', 'Краснодарский край Приазовье' -> the region name alone."""
    m = re.search(r'([А-ЯЁ][а-яё-]+(?:ая|ий) (?:область|край)|Республика [А-ЯЁ][а-яё-]+)', reg or '')
    return m.group(1) if m else reg
def anchor(e):
    reg = clean_reg(e['regions'][-1]) if e['regions'] else None
    if not (reg and geo.get(reg)) and not any(geo.get(f'{p}, {reg}' if reg else p) for p in e['places']):
        hits = [(e['text'].find(st), r) for st, r in STEMS if st in e['text']]   # first region stem named in the text
        if hits: FALLBACK['text'] += 1; return geo[min(hits)[1]], min(hits)[1]
    for p in e['places']:
        k = f'{p}, {reg}' if reg else p
        if geo.get(k): return geo[k], reg
    return (geo.get(reg), reg) if reg else (None, None)
ALIAS = {'Республика Чувашия': 'Чувашская Республика', 'Республика Удмуртия': 'Удмуртская Республика',   # one region, two spellings
         'Москва и область': 'Московская область', 'Юго-запад Московская область': 'Московская область',
         'г.Санкт-Петербург': 'Санкт-Петербург', 'Кантемировский область': 'Воронежская область'}
def rows(path):
    out, miss, occ = [], 0, 0
    for l in open(path):
        e = json.loads(l)
        if not set(e['kinds']) & {'danger', 'sighting', 'shootdown', 'air_defence'} or 'all_clear' in e['kinds']: continue
        ll, reg = anchor(e)
        if reg and any(o in reg for o in OCC): occ += 1; continue
        if not ll: miss += 1; continue
        out.append((e['ts'], depth(ll), ALIAS.get(reg, reg)))
    return out, miss, occ
if __name__ == '__main__':
    R, miss, occ = rows(sys.argv[1])
    print(f'posts used {len(R)}, no anchor {miss}, occupied excluded {occ}')
    if '--fixed' in sys.argv:   # confounder: keep only regions the channel reports in >=80% of months
        mon = collections.defaultdict(set)
        for ts, d, reg in R: mon[ts[:7]].add(reg)
        cnt = collections.Counter(r for v in mon.values() for r in v)
        keep = {r for r, c in cnt.items() if c >= 0.8 * len(mon)}
        print(f'fixed region set: {len(keep)} of {len(cnt)} regions, months {len(mon)}')
        R = [x for x in R if x[2] in keep]
    if '--monthly' in sys.argv:
        R = [(ts[:7] + '-01', d, reg) for ts, d, reg in R]
    wk = collections.defaultdict(list)
    for ts, d, reg in R:
        y, w, _ = dt.date.fromisoformat(ts[:10]).isocalendar(); wk[f'{y}-W{w:02d}'].append(d)
    print('week      n   >300km >600km >1000km  p90km  max')
    for k in sorted(wk):
        v = sorted(wk[k]); n = len(v)
        print(f'{k} {n:4d}  {sum(x>300 for x in v)/n:6.2f} {sum(x>600 for x in v)/n:6.2f} {sum(x>1000 for x in v)/n:7.2f}  {v[int(0.9*(n-1))]:5.0f} {v[-1]:5.0f}')
