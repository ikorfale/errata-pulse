#!/usr/bin/env python3
"""Reader reactions in a city's news channel after a local drone strike, against the same channel's own norm.
Design (frozen before looking at outcomes, see PREREG.md): two difference cells, posts as units, bootstrap over posts."""
import json, re, sys, random, statistics as st
from datetime import datetime, timedelta, timezone

BUCKETS = {
    'fear': set('😱 😨 😢 😭'.split()),
    'anger': set('😡 🤬'.split()),
    'derision': set('🤡 💩 😁 🤣 😂'.split()),
    'support': set('❤ 👍 🔥 🫡 ❤‍🔥'.split()),
    'pray': {'🙏'},
}
STRIKE = re.compile(r'бпла|беспилотн|дрон|ракетн|ракет[аыу]|атак[аиуе]|взрыв|прилет|прилёт|сбит|пво|нпз|обломк|ковер|ковёр|ограничени[яй] .*аэропорт', re.I)
CASES = {  # channel, local strike day (local calendar), UTC offset hours
    'spb-1018': ('fontankaspb', '2026-10-18', 3),
    'omsk-1008': ('Om1_Omsk', '2026-10-08', 6),
    'ryazan-1015': ('ryazan_chp62', '2026-10-15', 3),
}
MIN_REACT, BASE_DAYS = 30, 10

def load(ch, off):
    rows = []
    for l in open(f'data/{ch}.jsonl'):
        p = json.loads(l)
        t = datetime.fromisoformat(p['time']).astimezone(timezone(timedelta(hours=off)))
        p['day'] = t.date().isoformat()
        p['n'] = sum(p['reacts'].values())
        rows.append(p)
    return rows

def shares(p):
    return {b: sum(v for e, v in p['reacts'].items() if e in s) / p['n'] for b, s in BUCKETS.items()}

def boot_diff(a, b, key, n=4000, seed=7):
    rnd = random.Random(seed)
    va, vb = [x[key] for x in a], [x[key] for x in b]
    d = []
    for _ in range(n):
        d.append(st.median(rnd.choices(va, k=len(va))) - st.median(rnd.choices(vb, k=len(vb))))
    d.sort()
    return st.median(va) - st.median(vb), d[int(.025 * n)], d[int(.975 * n) - 1]

def run(case):
    ch, day, off = CASES[case]
    rows = load(ch, off)
    d0 = datetime.fromisoformat(day).date()
    out_days = {d0.isoformat(), (d0 + timedelta(days=1)).isoformat()}
    base_days = {(d0 - timedelta(days=k)).isoformat() for k in range(1, BASE_DAYS + 1)}
    have = sorted({r['day'] for r in rows})
    missing = sorted(base_days - set(have))
    allowed = {}
    cells = {}
    for r in rows:
        per = 'out' if r['day'] in out_days else 'base' if r['day'] in base_days else None
        if per is None:
            continue
        for e in r['reacts']:
            allowed.setdefault(per, set()).add(e)
        if r['n'] < MIN_REACT:
            continue
        x = shares(r)
        x['per1k'] = 1000 * r['n'] / r['views'] if r['views'] else 0
        topic = 'strike' if STRIKE.search(r['text']) else 'other'
        cells.setdefault((topic, per), []).append(x)
    print(f'== {case}: {ch}, strike day {day} (UTC+{off}); base {BASE_DAYS} days, missing base days {missing or "none"}')
    print('  emoji seen only in base:', ''.join(sorted(allowed.get('base', set()) - allowed.get('out', set()))) or '-',
          '| only in out:', ''.join(sorted(allowed.get('out', set()) - allowed.get('base', set()))) or '-')
    for k in [('strike', 'base'), ('strike', 'out'), ('other', 'base'), ('other', 'out')]:
        print(f'  n posts {k[0]:6} {k[1]:4}: {len(cells.get(k, []))}')
    res = {}
    for topic in ('strike', 'other'):
        a, b = cells.get((topic, 'out'), []), cells.get((topic, 'base'), [])
        enough = len(a) >= 10 and len(b) >= 20
        for key in list(BUCKETS) + ['per1k']:
            if not enough:
                continue
            diff, lo, hi = boot_diff(a, b, key)
            res[(topic, key)] = (diff, lo, hi)
            fmt = '{:+.3f}' if key != 'per1k' else '{:+.2f}'
            print(f'  {topic:6} {key:8} median out-base ' + fmt.format(diff) + ' [' + fmt.format(lo) + ', ' + fmt.format(hi) + ']',
                  f'(base median {st.median(x[key] for x in b):.3f})')
        if not enough:
            print(f'  {topic}: below minimum (need >=10 out, >=20 base) -> no claim')
    return res

if __name__ == '__main__':
    allres = {c: run(c) for c in (sys.argv[1:] or CASES)}
    print('== sign agreement across cases (CI excludes 0 counts as a sign):')
    for topic in ('strike', 'other'):
        for key in list(BUCKETS) + ['per1k']:
            signs = []
            for c, r in allres.items():
                if (topic, key) in r:
                    d, lo, hi = r[(topic, key)]
                    signs.append('+' if lo > 0 else '-' if hi < 0 else '0')
                else:
                    signs.append('n/a')
            print(f'  {topic:6} {key:8} ' + ' '.join(signs))
