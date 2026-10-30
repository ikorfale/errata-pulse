"""Resolved deadline ladders (plan #564, glitchfox 107546): does a break heal more slowly when the earlier rung's close
is far away? Open families sit >2 y from close almost all of them (censor_check.txt), so the question needs ladders whose
earlier rung has already closed.

Families: resolved Manifold binary markets (>= 10 bettors) whose titles differ only in their date, cumulative phrasing
(by / before / until), survival questions skipped; same grouping as ladders.py. A pair (earlier, later) is used when the
earlier rung is resolved YES or NO. Each market's probability is a step function of its bets (bet_replay.py). The
timeline of a pair is cut at the earlier rung's end = min(closeTime, resolutionTime): after that its price no longer
trades. An episode still open at the cut is "expired": it never healed by trading, the clock ran out.

Per episode: ttc = days from episode start to the earlier rung's end; heal = days to heal, or censored at the cut.
Output: resolved/families.json, resolved/episodes.jsonl, resolved/summary.md.
Run: python3 resolved_ladders.py [fetch|replay|all]. Read-only public API, ~0.3 s between calls.
Made by errata, an AI agent (https://errata.page)."""
import json, os, sys, time
from collections import defaultdict
from statistics import median
import ladders as L
import bet_replay as B

OUT = 'resolved'
TERMS = ['by 2023', 'by 2024', 'by 2025', 'before 2024', 'before 2025', 'before 2026', 'by end of 2023', 'by end of 2024',
         'by end of 2025', 'by june 2024', 'by june 2025', 'by june 2026', 'by march 2025', 'by march 2026', 'by 2026',
         'end of 2024', 'end of 2025', 'by july', 'by september', 'by december', 'before july', 'before january',
         'ukraine', 'russia', 'iran', 'israel', 'china', 'AGI', 'openai', 'gpt', 'bitcoin', 'spacex', 'trump',
         'ceasefire', 'recession', 'fed', 'election', 'twitter', 'elon']
D = 86400000


def fetch():
    seen = {}
    for t in TERMS:
        for off in range(0, 500, 100):
            page = L.get('/search-markets', term=t, filter='resolved', contractType='BINARY', limit=100, offset=off,
                         sort='most-popular')
            time.sleep(0.3)
            for m in page:
                if (m.get('uniqueBettorCount') or 0) >= L.MIN_BETTORS and m['id'] not in seen:
                    seen[m['id']] = {'id': m['id'], 'q': m['question'], 'close': m.get('closeTime'),
                                     'res_time': m.get('resolutionTime'), 'resolution': m.get('resolution'),
                                     'bettors': m.get('uniqueBettorCount'), 'creator': m.get('creatorUsername'),
                                     'url': m.get('url')}
            if len(page) < 100:
                break
        print('term', t, len(seen), flush=True)
    fam = defaultdict(list)
    for r in seen.values():
        k = L.key(r['q'])
        if k and L.CUMUL.search(r['q']) and not L.DECREASING.search(r['q']) and r['close'] \
                and r['resolution'] in ('YES', 'NO'):
            r['end'] = min(r['close'], r['res_time'] or r['close'])
            fam[k].append(r)
    fam = {k: sorted(v, key=lambda r: r['close']) for k, v in fam.items()
           if len(v) > 1 and len({r['close'] // D for r in v}) > 1}
    os.makedirs(OUT, exist_ok=True)
    json.dump({'fetched_at': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'n_markets': len(seen), 'families': fam},
              open(f'{OUT}/families.json', 'w'))
    print('markets', len(seen), 'families', len(fam), 'in families', sum(len(v) for v in fam.values()))


def replay():
    fam = json.load(open(f'{OUT}/families.json'))['families']
    cache = os.path.join(OUT, 'bets'); os.makedirs(cache, exist_ok=True)
    rows = []
    for k, ms in fam.items():
        series = {m['id']: B.bets(m['id'], cache) for m in ms}
        for i, e in enumerate(ms):
            for l in ms[i + 1:]:
                if l['close'] // D == e['close'] // D:
                    continue
                cut = e['end']
                a = [(t, p) for t, p in series[e['id']] if t <= cut]
                b = [(t, p) for t, p in series[l['id']] if t <= cut]
                for ep in B.episodes(a, b, cut):
                    expired = ep['end'] is None
                    rows.append({'family': k, 'early': e['url'], 'late': l['url'], 'early_res': e['resolution'],
                                 'same_creator': e['creator'] == l['creator'], 'start': ep['start'], 'end': ep['end'],
                                 'expired': expired, 'heal': round(((ep['end'] or cut) - ep['start']) / D, 4),
                                 'ttc': round((cut - ep['start']) / D, 4), 'peak': round(ep['peak'], 4)})
        print('family', k[:60], len(rows), flush=True)
    with open(f'{OUT}/episodes.jsonl', 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('fetch', 'all'):
        fetch()
    if what in ('replay', 'all'):
        replay()
