"""How long has each flagged ladder pair already been incoherent? Rebuilt from Manifold bet history, no waiting.

python3 backhist.py HISTORY.jsonl [DAY] -> backhist.md + backhist.json next to this file.
For every binary or multiple-choice pair flagged on DAY (default: the last run), fetch every bet on the markets
(public /v0/bets, paged), rebuild each price as a step function (probAfter of the last bet), sample it at 00:00 UTC
each day from the day both rungs existed, and report: the current streak (days in a row, back from DAY, with the
earlier rung more than TOL above the later one), the share of all sampled days with such a gap, the largest gap ever,
and the last bet on either rung. A long streak with no bets = nobody has looked; a long streak with bets = traders saw
the prices and left them.
"""
import bisect, json, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

TOL = 0.03
API = 'https://api.manifold.markets/v0'
hist = [json.loads(l) for l in open(sys.argv[1])]
row = {h['day']: h for h in hist}[sys.argv[2]] if len(sys.argv) > 2 else hist[-1]
review = json.load(open(__file__.rsplit('/', 1)[0] + '/review.json'))
verdict = lambda k: (review.get(k) or review.get(k.split('|')[0]) or {}).get('verdict', 'unreviewed')


def get(path):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, headers={'User-Agent': 'errata-ladders'}), timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 * (i + 1))
    raise RuntimeError(path)


bets_cache = {}
def bets(cid):
    if cid not in bets_cache:
        out, before = [], None
        while True:
            page = get(f'/bets?contractId={cid}&limit=1000' + (f'&before={before}' if before else ''))
            out += page
            if len(page) < 1000:
                break
            before = page[-1]['id']; time.sleep(0.3)
        bets_cache[cid] = sorted((b for b in out if not b.get('isCancelled') and b.get('probAfter') is not None),
                                 key=lambda b: b['createdTime'])
        time.sleep(0.3)
    return bets_cache[cid]


def series(cid, answer_id=None):
    """[(ms, prob)] from the bets on this market (and answer)."""
    return [(b['createdTime'], b['probAfter']) for b in bets(cid) if answer_id is None or b.get('answerId') == answer_id]


def at(s, t):
    i = bisect.bisect_right([ts for ts, _ in s], t)
    return s[i - 1][1] if i else s[0][1]


def measure(se, sl):
    if not se or not sl:
        return None
    end = datetime.fromisoformat(row['day']).replace(tzinfo=timezone.utc)
    start = datetime.fromtimestamp(max(se[0][0], sl[0][0]) / 1000, timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    days, d = [], start
    while d <= end:
        t = d.timestamp() * 1000
        days.append((d.date().isoformat(), at(se, t) - at(sl, t)))
        d += timedelta(days=1)
    if not days:
        return None
    streak = 0
    for _, g in reversed(days):
        if g <= TOL:
            break
        streak += 1
    return {'days': len(days), 'streak': streak, 'share': sum(g > TOL for _, g in days) / len(days),
            'max_gap': max(g for _, g in days), 'since': days[-streak][0] if streak else None,
            'last_bet': datetime.fromtimestamp(max(se[-1][0], sl[-1][0]) / 1000, timezone.utc).date().isoformat(),
            'bets': len(se) + len(sl),
            'bets_during': sum(ts >= (end - timedelta(days=streak - 1)).timestamp() * 1000 for ts, _ in se + sl) if streak else 0}


res = []
for k, v in row['pairs'].items():
    if v['kind'] == 'binary':
        e, l = k.split('|')
        m = measure(series(e), series(l))
    elif v['kind'] == 'mc':
        mid, et, lt = k.split('|')
        ans = {a['text']: a['id'] for a in get(f'/market/{mid}')['answers']}
        m = measure(series(mid, ans.get(et)), series(mid, ans.get(lt)))
    else:
        continue
    res.append({'key': k, 'kind': v['kind'], 'what': v['what'], 'url': v['url'], 'gap_now': v['gap'], 'verdict': verdict(k), **(m or {})})
    print(k, m, flush=True)

json.dump({'day': row['day'], 'tol': TOL, 'pairs': res}, open(__file__.rsplit('/', 1)[0] + '/backhist.json', 'w'), indent=1)
L = [f"# How long flagged ladder pairs have been incoherent (rebuilt from bet history, run of {row['day']})", '',
     f'Daily price at 00:00 UTC from the last bet before it; a day counts when the earlier rung is more than {TOL * 100:.0f} '
     'points above the later one. Streak = days in a row up to the run day.', '',
     '| kind | review | gap now | streak (days) | since | bets during streak | share of days | max gap | sampled days | last bet | bets | pair |',
     '|---|---|---|---|---|---|---|---|---|---|---|---|']
for r in sorted(res, key=lambda r: -r.get('streak', 0)):
    if 'days' not in r:
        L.append(f"| {r['kind']} | {r['verdict']} | {r['gap_now'] * 100:.0f} | no bet history | | | | | | | | [{r['what'][:100]}]({r['url']}) |")
        continue
    L.append(f"| {r['kind']} | {r['verdict']} | {r['gap_now'] * 100:.0f} | {r['streak']} | {r['since'] or '-'} | {r['bets_during']} | {r['share'] * 100:.0f}% | "
             f"{r['max_gap'] * 100:.0f} | {r['days']} | {r['last_bet']} | {r['bets']} | [{r['what'][:100]}]({r['url']}) |")
open(__file__.rsplit('/', 1)[0] + '/backhist.md', 'w').write('\n'.join(L) + '\n')
