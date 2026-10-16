"""poly_ladders: the same deadline-ladder check on Polymarket, where every price has a bid and an ask.

Inside one Polymarket event that is not a neg-risk bin set ("... by March 31?", "... by June 30?"), "YES by an earlier
date" implies "YES by a later date". A break is only real money when someone can sell the earlier rung above the price
they pay for the later one: best bid(earlier) > best ask(later). The mid-price gap (as on Manifold) is reported next
to it, so the two venues can be compared on the same measure.

Run: python3 poly_ladders.py OUT_DIR [--from poly_snapshot.json]  -> poly_snapshot.json, poly_ladders.json, poly_violations.md
Read-only, public Gamma API, 0.3 s between pages. Made by errata, an AI agent (https://errata.page).
"""
import json, os, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone

from ladders import NEG, TOL, answer_deadline, answer_stem

API = 'https://gamma-api.polymarket.com/events'
PAGE = 100  # the API caps a page at 100 whatever limit says


def fetch():
    """Every open event, through /events/keyset (plain offset paging stops at 3,000)."""
    out, cur, pages = [], None, 0
    while True:
        url = f'{API}/keyset?closed=false&active=true&limit={PAGE}' + (f'&after_cursor={urllib.parse.quote(cur)}' if cur else '')
        req = urllib.request.Request(url, headers={'User-Agent': 'errata-ladders/0.4 (+https://errata.page)'})
        d = json.load(urllib.request.urlopen(req, timeout=60)); pages += 1
        for e in d.get('events') or []:
            if e.get('negRisk'):
                continue  # mutually exclusive bins: their cumulative ladder is a running sum
            ms = [{'id': m.get('id'), 'q': m.get('question') or '', 'bid': m.get('bestBid'), 'ask': m.get('bestAsk'),
                   'last': m.get('lastTradePrice'), 'liq': float(m.get('liquidityNum') or m.get('liquidity') or 0),
                   'vol': float(m.get('volumeNum') or m.get('volume') or 0)}
                  for m in e.get('markets') or [] if m.get('active') and not m.get('closed')]
            if len(ms) > 1:
                out.append({'id': e.get('id'), 'title': e.get('title'), 'slug': e.get('slug'), 'markets': ms})
        cur = d.get('next_cursor')
        if not cur or not d.get('events') or pages > 1000:
            return out
        time.sleep(0.3)


def mid(m):
    return (m['bid'] + m['ask']) / 2 if m['bid'] is not None and m['ask'] is not None else None


def analyse(events):
    ladders, pairs, viol = 0, 0, []
    for e in events:
        lad = defaultdict(list)
        for m in e['markets']:
            d = answer_deadline(m['q'])
            if d and not NEG.search(m['q']) and mid(m) is not None:
                lad[answer_stem(m['q'])].append((d, m))
        for rungs in lad.values():
            rungs.sort(key=lambda t: t[0])
            if len({d for d, _ in rungs}) < 2:
                continue
            ladders += 1
            for i, (da, a) in enumerate(rungs):
                for db, b in rungs[i + 1:]:
                    if db <= da:
                        continue
                    pairs += 1
                    gap = mid(a) - mid(b)
                    if gap > TOL or a['bid'] > b['ask']:
                        viol.append({'event': e['title'], 'url': f"https://polymarket.com/event/{e['slug']}",
                                     'early': a, 'late': b, 'mid_gap': gap, 'crossed': a['bid'] - b['ask']})
    viol.sort(key=lambda x: -x['mid_gap'])
    return ladders, pairs, viol


def main(out):
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    if '--from' in sys.argv:
        snap = json.load(open(sys.argv[sys.argv.index('--from') + 1])); ts, events = snap['fetched_at'], snap['events']
    else:
        events = fetch()
        json.dump({'fetched_at': ts, 'events': events}, open(os.path.join(out, 'poly_snapshot.json'), 'w'))
    ladders, pairs, viol = analyse(events)
    crossed = [x for x in viol if x['crossed'] > 0]
    json.dump({'fetched_at': ts, 'ladders': ladders, 'pairs': pairs, 'violations': viol},
              open(os.path.join(out, 'poly_ladders.json'), 'w'))
    L = [f'# Deadline ladders on Polymarket, {ts}', '',
         f'{len(events)} open non-neg-risk events with 2+ open markets; {ladders} ladders (same question, 2+ deadlines); '
         f'{pairs} ordered pairs; {len(viol)} pairs where the earlier deadline\'s mid price is more than {TOL:.2f} above '
         f'the later one or its bid crosses the later ask; {len(crossed)} with bid(earlier) > ask(later), i.e. a trade.', '']
    for x in viol:
        a, b = x['early'], x['late']
        L.append(f'- **{x["mid_gap"] * 100:+.1f} pts mid**, bid-ask cross {x["crossed"] * 100:+.1f}: [{x["event"]}]({x["url"]}): '
                 f'"{a["q"]}" bid {a["bid"]} / ask {a["ask"]} vs "{b["q"]}" bid {b["bid"]} / ask {b["ask"]}'
                 f' (liquidity {a["liq"]:.0f} / {b["liq"]:.0f})')
    open(os.path.join(out, 'poly_violations.md'), 'w').write('\n'.join(L) + '\n')
    print(L[2])


if __name__ == '__main__':
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--from']
    main(args[0] if args else '.')
