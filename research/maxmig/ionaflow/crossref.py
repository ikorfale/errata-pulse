#!/usr/bin/env python3
"""Cross-reference IONAFLOW's raw daily post counts of Russian heads of regions on Max and Telegram.
Source of all counts: IONAFLOW (https://ionaflow.com). Matching and analysis: errata.
Key = first name + surname from name_ru, with spelling variants in the Telegram list fixed by hand."""
import csv, glob, json, re, statistics, collections, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '..', 'data', 'ionaflow')
FIX = {'Развозжаев': 'Развожаев', 'Кумилов': 'Кумпилов', 'Хазиков': 'Хасиков',
       'Манохин': 'Махонин', 'Парслер': 'Паслер'}

def key(name_ru):
    s = re.sub(r'\(.*?\)', ' ', name_ru)
    s = s.replace('— официальный канал', ' ')
    w = s.split()
    first, last = w[-2], FIX.get(w[-1], w[-1])
    return f'{first} {last}'

# Corrections from IONAFLOW (letter 2026-11-07): (key, period-or-None, source_type) -> drop as missing/invalid.
# Kurinny: a Vedomosti Max channel mislabelled as a governor -> invalid everywhere.
# Gladkov: governor until 13.05.2026 -> not a sitting governor in July/October.
# Drozdenko: Telegram channel address changed, not collected -> Telegram missing, not zero.
# Fedorishchev: Telegram monitoring paused 20.08, so the October Telegram count is missing, not zero.
DROP = [('Алексей Куринный', None, None), ('Вячеслав Гладков', '2026-07-15', None),
        ('Вячеслав Гладков', '2026-10-24', None), ('Александр Дрозденко', None, 'telegram'),
        ('Вячеслав Федорищев', '2026-10-24', 'telegram')]
def dropped(k, path, t):
    return any(k == dk and (dp is None or dp in path) and (dt is None or dt == t) for dk, dp, dt in DROP)

def load(path):
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    per = collections.defaultdict(lambda: {'max': None, 'telegram': None, 'days': {}})
    for r in rows:
        k = key(r['name_ru'])
        t = r['source_type']
        if dropped(k, path, t):
            per[k]['missing'] = per[k].get('missing', set()) | {t}
            per[k].setdefault('label', r['name_ru'].strip())
            continue
        p = per[k]
        p[t] = (p[t] or 0) + int(r['posts'])
        p['days'].setdefault(r['date'], {})[t] = int(r['posts'])
        p.setdefault('label', r['name_ru'].strip())
    return per

def summary(per):
    per = {k: p for k, p in per.items() if not p.get('missing')}  # any side missing -> out of platform comparisons
    both_listed = [k for k, p in per.items() if p['max'] is not None and p['telegram'] is not None]
    out = {'listed_max': sum(p['max'] is not None for p in per.values()),
           'listed_tg': sum(p['telegram'] is not None for p in per.values()),
           'listed_both': len(both_listed)}
    mx = lambda p: (p['max'] or 0) > 0
    tg = lambda p: (p['telegram'] or 0) > 0
    out['posted_max'] = sum(mx(p) for p in per.values())
    out['posted_tg'] = sum(tg(p) for p in per.values())
    out['max_only'] = sorted(k for k, p in per.items() if mx(p) and not tg(p))
    out['tg_only'] = sorted(k for k, p in per.items() if tg(p) and not mx(p))
    out['both'] = sum(mx(p) and tg(p) for p in per.values())
    out['neither'] = sorted(k for k, p in per.items() if not mx(p) and not tg(p))
    out['posts_max'] = sum(p['max'] or 0 for p in per.values())
    out['posts_tg'] = sum(p['telegram'] or 0 for p in per.values())
    # mirroring: among governors listed on both and active on both, share of days with equal counts
    eq = []
    shares = []
    for k in both_listed:
        p = per[k]
        if mx(p) and tg(p):
            d = p['days'].values()
            eq.append(sum(1 for x in d if x.get('max') == x.get('telegram')) / len(p['days']))
            shares.append(p['max'] / (p['max'] + p['telegram']))
    out['median_max_share_both_active'] = round(statistics.median(shares), 3) if shares else None
    out['n_both_active'] = len(shares)
    out['identical_all_7_days'] = sum(1 for e in eq if e == 1.0)
    out['median_share_days_equal'] = round(statistics.median(eq), 3) if eq else None
    return out

if __name__ == '__main__':
    periods = {}
    table = collections.defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(DATA, 'sources_daily_posts_*.csv'))):
        lab = re.search(r'(\d{4}-\d\d-\d\d)_(\d{4}-\d\d-\d\d)', f).group(0)
        per = load(f)
        periods[lab] = summary(per)
        for k, p in per.items():
            table[k]['label'] = p['label']
            table[k][lab] = (p['max'], p['telegram'])
    json.dump(periods, open(os.path.join(HERE, 'summary.json'), 'w'), ensure_ascii=False, indent=1)
    labs = sorted(periods, key=lambda s: s[:10])
    with open(os.path.join(HERE, 'per_governor.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['governor_key', 'label'] + [f'{l}_{t}' for l in labs for t in ('max', 'telegram')])
        for k in sorted(table):
            w.writerow([k, table[k]['label']] + [('' if table[k].get(l, (None, None))[i] is None else table[k][l][i]) for l in labs for i in (0, 1)])
    for l in labs:
        print(l, json.dumps(periods[l], ensure_ascii=False))
