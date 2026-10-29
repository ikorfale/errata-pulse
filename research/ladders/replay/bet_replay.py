"""Bet-level replay of deadline ladders (plan #475). The daily snapshot sees a price once a day, so a break that opens
and heals within a day is invisible to it. Here every bet of every market in the ladder families is fetched, each
market's probability becomes a step function (probAfter at each bet's createdTime), and for every ordered pair
(earlier deadline, later deadline) of a family the replay finds every episode where the earlier market is priced more
than TOL above the later one, with its start, end (or "open") and peak gap.

Run: python3 bet_replay.py ladders.json out_dir  -> out_dir/bets/<id>.json.gz (cache), episodes.jsonl, summary.md
Read-only, public API, ~0.3 s between calls. Made by errata, an AI agent (https://errata.page)."""
import gzip, json, os, sys, time, urllib.parse, urllib.request
from statistics import median

API = 'https://api.manifold.markets/v0'
TOL = 0.03
DAY = 86400000


def get(path, **q):
    url = API + path + '?' + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'errata-ladders (errata.page; AI agent research)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print('retry', url, e, flush=True); time.sleep(5 * (i + 1))
    raise RuntimeError('failed ' + url)


def bets(cid, cache):
    f = os.path.join(cache, cid + '.json.gz')
    if os.path.exists(f):
        return json.load(gzip.open(f))
    out, before = [], None
    while True:
        q = {'contractId': cid, 'limit': 1000}
        if before: q['before'] = before
        page = get('/bets', **q); time.sleep(0.3)
        out += [(b['createdTime'], b['probAfter']) for b in page if b.get('probAfter') is not None]
        if len(page) < 1000: break
        before = page[-1]['id']
    out.sort()
    json.dump(out, gzip.open(f, 'wt'))
    return out


def episodes(a, b, now):
    """a, b: sorted (t, p) steps. Episodes where p_a - p_b > TOL, on the merged timeline after both have a price."""
    ev = sorted([(t, 0, p) for t, p in a] + [(t, 1, p) for t, p in b])
    pa = pb = None; cur = None; eps = []
    for t, k, p in ev:
        if k == 0: pa = p
        else: pb = p
        if pa is None or pb is None: continue
        g = pa - pb
        if g > TOL:
            if cur is None: cur = {'start': t, 'peak': g}
            else: cur['peak'] = max(cur['peak'], g)
        elif cur is not None:
            cur['end'] = t; eps.append(cur); cur = None
    if cur is not None:
        cur['end'] = None; eps.append(cur)
    return eps


def main():
    src, out = sys.argv[1], sys.argv[2]
    cache = os.path.join(out, 'bets'); os.makedirs(cache, exist_ok=True)
    fam = json.load(open(src))['families']
    now = int(time.time() * 1000)
    rows, pairs = [], 0
    for key, ms in fam.items():
        ms = sorted(ms, key=lambda m: m['close'])
        series = {m['id']: bets(m['id'], cache) for m in ms}
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                e, l = ms[i], ms[j]
                if e['close'] == l['close']: continue
                pairs += 1
                for ep in episodes(series[e['id']], series[l['id']], now):
                    dur = ((ep['end'] or now) - ep['start']) / DAY
                    rows.append({'family': key, 'early': e['url'], 'late': l['url'], 'same_creator': e['creator'] == l['creator'],
                                 'start': ep['start'], 'end': ep['end'], 'days': round(dur, 4), 'peak': round(ep['peak'], 4)})
        print('family done', key[:60], len(rows), flush=True)
    with open(os.path.join(out, 'episodes.jsonl'), 'w') as f:
        for r in rows: f.write(json.dumps(r) + '\n')
    closed = [r for r in rows if r['end'] is not None]; opened = [r for r in rows if r['end'] is None]
    short = [r for r in closed if r['days'] < 1]
    ever = {(r['early'], r['late']) for r in rows}
    s = [f'# Bet-level ladder replay, {time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())}', '',
         f'Families {len(fam)}, ordered pairs with different close dates {pairs}, pairs ever broken by more than {TOL:.2f}: {len(ever)}.',
         f'Episodes {len(rows)}: closed {len(closed)}, still open {len(opened)}.']
    if closed:
        d = sorted(r['days'] for r in closed)
        s.append(f'Closed episodes: median {median(d):.2f} days, q75 {d[3 * len(d) // 4]:.2f}, max {d[-1]:.1f}; '
                 f'shorter than 1 day (invisible to a daily snapshot unless it lands inside): {len(short)} ({len(short) / len(closed):.0%}).')
        s.append(f'Peak gap of closed episodes: median {median(r["peak"] for r in closed):.3f}.')
    if opened:
        s.append(f'Open episodes: median age {median(r["days"] for r in opened):.1f} days, same creator {sum(r["same_creator"] for r in opened)}.')
    open(os.path.join(out, 'summary.md'), 'w').write('\n'.join(s) + '\n')
    print('\n'.join(s))


if __name__ == '__main__':
    main()
