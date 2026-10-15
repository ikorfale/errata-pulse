#!/usr/bin/env python3
"""coincide: is a spike that "lines up with" an event more than chance?

Finds spikes in daily Wikipedia pageviews (views / trailing 14-day median >= RATIO),
then counts how many spikes have an event from a ledger within +-K days, and compares
with a null where the event dates are shifted circularly by every offset inside the
window (keeps how events cluster, breaks their link to the spikes).

v0.2 (16 Oct, after theone's review on the board, post 89199):
- range dates ("2026-09-03/10") are no longer read as their first day: --ranges skip (default),
  first (the v0.1 behaviour), or all (every day of the range counts as an event day);
- "within +-k days" is calendar proximity: no wrap from the last day of the window to the first
  (v0.1 wrapped; --wrap restores it). The null still rotates event dates, then tests linearly;
- --split DATE: a stratified null. Event dates rotate only inside their own period (before /
  from DATE), every combination of the two rotations is scored, and coverage and hits are
  printed per period. For a ledger that records sparsely in one period and densely in another;
- --cache FILE: pageviews are saved/reused, so a rerun reads the same numbers.

  coincide.py --events FILE.jsonl --field date_event --from 2026-09-01 --to 2026-10-14 \
              --k 1 --ratio 3 en:World_War_III zh:第三次世界大戰 ...
Prints one line per article and a JSON summary to stdout.
"""
import argparse, datetime as dt, json, statistics, sys, urllib.parse, urllib.request

UA = {'User-Agent': 'errata-coincide/0.1 (https://errata.page; errata@agentmail.to)'}


def views(lang, title, start, end):
    url = ('https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/'
           f'{lang}.wikipedia/all-access/user/{urllib.parse.quote(title, safe="")}/daily/'
           f'{start:%Y%m%d}00/{end:%Y%m%d}00')
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        items = json.load(r)['items']
    return {dt.datetime.strptime(i['timestamp'][:8], '%Y%m%d').date(): i['views'] for i in items}


def spikes(series, days, ratio, floor):
    out = []
    for i, d in enumerate(days):
        if i < 14 or d not in series:
            continue
        base = statistics.median(series.get(x, 0) for x in days[i - 14:i])
        if series[d] >= floor and base > 0 and series[d] / base >= ratio:
            out.append((d, series[d], series[d] / base))
    return out


def near(i, ev, k, n, wrap):
    if wrap:
        return any((i + j) % n in ev for j in range(-k, k + 1))
    return any(0 <= i + j < n and i + j in ev for j in range(-k, k + 1))


def hits(spike_days, ev, k, n, wrap):
    return sum(near(s, ev, k, n, wrap) for s in spike_days)


def rotate(ev, lo, hi, sh):
    """rotate event indices in [lo, hi) by sh inside that block"""
    m = hi - lo
    return {lo + (e - lo + sh) % m for e in ev if lo <= e < hi}


def parse_days(v, mode):
    """event days for one ledger value; [] if it cannot be placed"""
    v = str(v)
    try:
        d = dt.date.fromisoformat(v[:10])
    except ValueError:  # month-only dates cannot be placed on a day
        return []
    if v[10:11] != '/':
        return [d]
    if mode == 'skip':
        return []
    if mode == 'first':
        return [d]
    tail = v[11:].split()[0]  # "10", "10-05": end of the range in the same year
    try:
        e = dt.date.fromisoformat(v[:8] + tail) if len(tail) == 2 else dt.date.fromisoformat(v[:5] + tail)
    except ValueError:
        return [d]
    return [d + dt.timedelta(days=i) for i in range((e - d).days + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--events', required=True)
    ap.add_argument('--field', default='date_event')
    ap.add_argument('--from', dest='start', required=True)
    ap.add_argument('--to', dest='end', required=True)
    ap.add_argument('--k', type=int, default=1)
    ap.add_argument('--ratio', type=float, default=3.0)
    ap.add_argument('--floor', type=int, default=30, help='ignore spikes under this many views/day')
    ap.add_argument('--ranges', choices=['skip', 'first', 'all'], default='skip')
    ap.add_argument('--wrap', action='store_true', help='v0.1 geometry: +-k wraps around the window')
    ap.add_argument('--split', help='date that starts the second period of a stratified null')
    ap.add_argument('--cache', help='json file to save/reuse pageviews')
    ap.add_argument('articles', nargs='+', help='lang:Title')
    a = ap.parse_args()
    start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    fetch_from = start - dt.timedelta(days=14)
    days = [fetch_from + dt.timedelta(days=i) for i in range((end - fetch_from).days + 1)]
    window = [d for d in days if d >= start]
    n = len(window)
    pos = {d: i for i, d in enumerate(window)}
    ev = set()
    for line in open(a.events):
        for d in parse_days(json.loads(line).get(a.field), a.ranges):
            if d in pos:
                ev.add(pos[d])
    covered = sum(near(i, ev, a.k, n, a.wrap) for i in range(n))
    print(f'window {start}..{end}: {n} days, {len(ev)} days with >=1 event (ranges={a.ranges}), '
          f'{covered}/{n} days within +-{a.k} of an event ({"wrapped" if a.wrap else "calendar"})')
    cache = {}
    if a.cache:
        try:
            cache = json.load(open(a.cache))
        except FileNotFoundError:
            pass
    all_sp, rows = [], []
    for art in a.articles:
        lang, title = art.split(':', 1)
        if art not in cache:
            cache[art] = {str(d): v for d, v in views(lang, title, fetch_from, end).items()}
        s = {dt.date.fromisoformat(d): v for d, v in cache[art].items()}
        sp = [x for x in spikes(s, days, a.ratio, a.floor) if x[0] in pos]
        all_sp += [pos[x[0]] for x in sp]
        rows.append({'article': art, 'spikes': [[str(d), v, round(r, 1)] for d, v, r in sp]})
        print(f'{art}: {len(sp)} spikes ' + ', '.join(f'{d:%m-%d} x{r:.1f}' for d, v, r in sp))
    # spikes of several pages on one day are one episode, not independent evidence
    all_sp = sorted(set(all_sp))
    if a.cache:
        json.dump(cache, open(a.cache, 'w'), ensure_ascii=False, indent=0)
    obs = hits(all_sp, ev, a.k, n, a.wrap)
    if a.split:
        c = pos[dt.date.fromisoformat(a.split)]
        blocks = [(0, c), (c, n)]
        for lo, hi in blocks:
            e_in = {e for e in ev if lo <= e < hi}
            sp_in = [x for x in all_sp if lo <= x < hi]
            cov = sum(near(i, ev, a.k, n, a.wrap) for i in range(lo, hi))
            print(f'  period {window[lo]}..{window[hi - 1]}: {hi - lo} days, {len(e_in)} event days, '
                  f'{cov}/{hi - lo} days near an event, spike days near an event '
                  f'{hits(sp_in, ev, a.k, n, a.wrap)}/{len(sp_in)}')
        null = [hits(all_sp, rotate(ev, 0, c, s1) | rotate(ev, c, n, s2), a.k, n, a.wrap)
                for s1 in range(c) for s2 in range(n - c)]
        label = f'stratified null at {a.split} ({len(null)} rotation pairs, incl. identity)'
        p = sum(x >= obs for x in null) / len(null)
    else:
        null = [hits(all_sp, rotate(ev, 0, n, sh), a.k, n, a.wrap) for sh in range(1, n)]
        label = f'circular-shift null ({n - 1} shifts)'
        p = (1 + sum(x >= obs for x in null)) / n
    mean_null = statistics.mean(null) if null else float('nan')
    print(f'distinct spike days with an event within +-{a.k} d: {obs}/{len(all_sp)}; '
          f'{label} mean {mean_null:.2f}/{len(all_sp)}, p = {p:.3f}')
    json.dump({'window': [str(start), str(end)], 'k': a.k, 'ratio': a.ratio, 'ranges': a.ranges, 'wrap': a.wrap, 'split': a.split, 'event_days': len(ev),
               'days_covered': covered, 'n_days': n, 'spikes': len(all_sp), 'hits': obs,
               'null_mean': mean_null, 'p': p, 'rows': rows}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == '__main__':
    main()
