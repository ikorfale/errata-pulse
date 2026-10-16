"""Ladder breaks in bet history: every episode, how it started, how long it lasted, how it ended. No waiting for runs.

python3 backhist.py HISTORY.jsonl [DAY] -> backhist.md + backhist.json next to this file.
For every binary or multiple-choice pair flagged on DAY (default: the last run), fetch every bet on the markets (public
/v0/bets, paged), keep the rows that moved a price (no redemptions, no unfilled limit orders, no cancelled bets), and
walk both rungs' prices bet by bet from the moment both existed. An *episode* starts when the earlier rung goes more
than TOL above the later one and ends when it comes back. For each episode: what started it (born broken, a bet
raising the earlier rung, a bet lowering the later one), how it ended (which rung moved), its length, its largest gap;
for the episode open on the run day, the fills on the two rungs and on the whole market after it started, and the
number of distinct bettors. v2 after a review by a second model (Claude Fable 5.1): v1 sampled at 00:00, counted
non-trades and only looked at the open break, which is biased toward quiet markets.
"""
import json, os, statistics, sys, time, urllib.request
from datetime import datetime, timezone

TOLS = (0.03, 0.05)
API = 'https://api.manifold.markets/v0'
HERE = os.path.dirname(os.path.abspath(__file__))
hist = [json.loads(l) for l in open(sys.argv[1])]
row = {h['day']: h for h in hist}[sys.argv[2]] if len(sys.argv) > 2 else hist[-1]
now_ms = datetime.fromisoformat(row['fetched_at'].replace('Z', '+00:00')).timestamp() * 1000
review = json.load(open(os.path.join(HERE, 'review.json')))
verdict = lambda k: (review.get(k) or review.get(k.split('|')[0]) or {}).get('verdict', 'unreviewed')
DAY = 86400000


def get(path):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, headers={'User-Agent': 'errata-ladders'}), timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 * (i + 1))
    raise RuntimeError(path)


cache = {}
def bets(cid):
    """Rows that moved a price on this market, oldest first."""
    if cid not in cache:
        out, before = [], None
        while True:
            page = get(f'/bets?contractId={cid}&limit=1000' + (f'&before={before}' if before else ''))
            out += page
            if len(page) < 1000:
                break
            before = page[-1]['id']; time.sleep(0.3)
        ids = [b['id'] for b in out]
        assert len(ids) == len(set(ids)), f'paging repeated bets on {cid}'
        cache[cid] = sorted((b for b in out if not b.get('isCancelled') and not b.get('isRedemption')
                             and b.get('probAfter') is not None and b.get('probBefore') is not None
                             and abs(b['probAfter'] - b['probBefore']) > 1e-9), key=lambda b: b['createdTime'])
        time.sleep(0.3)
    return cache[cid]


def walk(rungs, tol):
    """rungs = {'early': (market id, answer id or None), 'late': (...)}."""
    ev = []
    for side, (mkt, aid) in rungs.items():
        ev += [(b['createdTime'], side, b['probAfter'], b['userId']) for b in bets(mkt) if aid is None or b.get('answerId') == aid]
    ev.sort()
    first = {s: min((t for t, side, *_ in ev if side == s), default=None) for s in rungs}
    if None in first.values():
        return None
    t0, p, eps, cur = max(first.values()), {}, [], None
    for t, side, prob, _ in ev:
        p[side] = prob
        if t < t0:
            continue
        gap = round(p['early'] - p['late'], 4)
        if cur is None and gap > tol:
            cur = {'start': t, 'cause': 'born' if t == t0 else ('earlier rung up' if side == 'early' else 'later rung down'), 'max_gap': gap}
        elif cur is not None and gap > tol:
            cur['max_gap'] = max(cur['max_gap'], gap)
        elif cur is not None:
            cur.update(end=t, ended_by='earlier rung down' if side == 'early' else 'later rung up'); eps.append(cur); cur = None
    if cur is not None:
        cur['end'] = None; eps.append(cur)
    for e in eps:
        e['days'] = round(((e['end'] or now_ms) - e['start']) / DAY, 1)
    return {'episodes': eps, 'events': ev}


res = []
for k, v in row['pairs'].items():
    if v['kind'] == 'binary':
        e, l = k.split('|')
        rungs, mids = {'early': (e, None), 'late': (l, None)}, [e, l]
    elif v['kind'] == 'mc':
        mid, et, lt = k.split('|')
        m = get(f'/market/{mid}')
        assert m.get('shouldAnswersSumToOne') is False, f'{mid}: answers sum to one, other answers move these prices'
        ans = {a['text']: a['id'] for a in m['answers']}
        rungs, mids = {'early': (mid, ans[et]), 'late': (mid, ans[lt])}, [mid]
    else:
        continue
    r = {'key': k, 'kind': v['kind'], 'what': v['what'], 'url': v['url'], 'gap_now': v['gap'], 'verdict': verdict(k),
         'market': k if v['kind'] == 'binary' else k.split('|')[0]}
    for tol in TOLS:
        w = walk(rungs, tol)
        if w is None:
            r['no_history'] = True; break
        eps = w['episodes']; op = eps[-1] if eps and eps[-1]['end'] is None else None
        s = {'episodes': len(eps), 'closed': [e for e in eps if e['end']], 'open': op}
        if op:
            after = [x for x in w['events'] if x[0] > op['start']]
            s['rung_fills_after'] = len(after)
            s['market_fills_after'] = sum(1 for mk in mids for b in bets(mk) if b['createdTime'] > op['start'])
            s['bettors_after'] = len({x[3] for x in after})
        r[f'tol{int(round(tol * 100))}'] = s
    res.append(r)
    print(k, {t: (x['episodes'], x['open'] and x['open']['days']) for t, x in r.items() if t.startswith('tol')}, flush=True)

json.dump({'day': row['day'], 'pairs': res}, open(os.path.join(HERE, 'backhist.json'), 'w'), indent=1)

# per market: the unit that counts (one multiple-choice market gives many overlapping pairs)
mk = {}
for r in res:
    if not r.get('no_history'):
        mk.setdefault(r['market'], []).append(r)
iso = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d')
oldest = lambda rs: max((r['tol3']['open']['days'] for r in rs if r['tol3']['open']), default=0)
L = [f"# Ladder breaks in bet history (pairs flagged on {row['day']})", '',
     'Prices rebuilt bet by bet (price-moving fills only). An episode = the earlier rung more than 3 points above the later '
     'one. "Open" = still running at the run. Fills after = price-moving bets after the open episode began, on the two '
     'rungs / on the whole market (a bet on any answer means someone had the whole ladder on screen).', '',
     '## Per market', '',
     '| review | pairs | open (3 pt) | open (5 pt) | oldest open break | how it began | fills after (rungs / market) | bettors after | closed episodes | median closed length (days) | closed by | market |',
     '|---|---|---|---|---|---|---|---|---|---|---|---|']
for m, rs in sorted(mk.items(), key=lambda kv: -oldest(kv[1])):
    opens = [r for r in rs if r['tol3']['open']]
    o = max(opens, key=lambda r: r['tol3']['open']['days']) if opens else None
    closed = [e for r in rs for e in r['tol3']['closed']]
    by = {}
    for e in closed:
        by[e['ended_by']] = by.get(e['ended_by'], 0) + 1
    L.append(f"| {rs[0]['verdict']} | {len(rs)} | {len(opens)} | {sum(1 for r in rs if r['tol5']['open'])} | "
             + (f"{o['tol3']['open']['days']} d (since {iso(o['tol3']['open']['start'])}) | {o['tol3']['open']['cause']} | "
                f"{max(r['tol3']['rung_fills_after'] for r in opens)} / {max(r['tol3']['market_fills_after'] for r in opens)} | "
                f"{max(r['tol3']['bettors_after'] for r in opens)} | " if o else '- | - | - | - | ')
             + f"{len(closed)} | {statistics.median(e['days'] for e in closed) if closed else '-'} | "
             f"{', '.join(f'{a}: {n}' for a, n in by.items()) or '-'} | [{rs[0]['what'].split(': ')[0][:90]}]({rs[0]['url']}) |")
L += ['', '## Every pair (3 pt)', '', '| review | gap now | open break (days) | began | rung fills after | market fills after | closed episodes | pair |',
      '|---|---|---|---|---|---|---|---|']
for r in sorted(res, key=lambda r: -(((r.get('tol3') or {}).get('open') or {}).get('days', 0))):
    if r.get('no_history'):
        L.append(f"| {r['verdict']} | {r['gap_now'] * 100:.1f} | no bet history | | | | | [{r['what'][:100]}]({r['url']}) |"); continue
    s = r['tol3']; o = s['open']
    L.append(f"| {r['verdict']} | {r['gap_now'] * 100:.1f} | {o['days'] if o else 'closed'} | {o['cause'] if o else '-'} | "
             f"{s.get('rung_fills_after', '-')} | {s.get('market_fills_after', '-')} | {len(s['closed'])} | [{r['what'][:100]}]({r['url']}) |")
open(os.path.join(HERE, 'backhist.md'), 'w').write('\n'.join(L) + '\n')
