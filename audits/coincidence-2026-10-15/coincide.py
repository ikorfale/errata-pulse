#!/usr/bin/env python3
"""coincide: is a spike that "lines up with" an event more than chance?

Finds spikes in daily Wikipedia pageviews (views / trailing 14-day median >= RATIO),
then counts how many spikes have an event from a ledger within +-K days, and compares
with a null where the event dates are shifted circularly by every offset inside the
window (keeps how events cluster, breaks their link to the spikes).

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


def hits(spike_days, event_idx, k, n, shift=0):
    ev = {(e + shift) % n for e in event_idx}
    return sum(any((s + j) % n in ev for j in range(-k, k + 1)) for s in spike_days)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--events', required=True)
    ap.add_argument('--field', default='date_event')
    ap.add_argument('--from', dest='start', required=True)
    ap.add_argument('--to', dest='end', required=True)
    ap.add_argument('--k', type=int, default=1)
    ap.add_argument('--ratio', type=float, default=3.0)
    ap.add_argument('--floor', type=int, default=30, help='ignore spikes under this many views/day')
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
        v = json.loads(line).get(a.field)
        try:
            d = dt.date.fromisoformat(str(v)[:10])
        except ValueError:  # month-only or range dates cannot be placed on one day
            continue
        if d in pos:
            ev.add(pos[d])
    covered = sum(any((i + j) % n in ev for j in range(-a.k, a.k + 1)) for i in range(n))
    print(f'window {start}..{end}: {n} days, {len(ev)} days with >=1 event, '
          f'{covered}/{n} days within +-{a.k} of an event')
    all_sp, rows = [], []
    for art in a.articles:
        lang, title = art.split(':', 1)
        s = views(lang, title, fetch_from, end)
        sp = [x for x in spikes(s, days, a.ratio, a.floor) if x[0] in pos]
        all_sp += [pos[x[0]] for x in sp]
        rows.append({'article': art, 'spikes': [[str(d), v, round(r, 1)] for d, v, r in sp]})
        print(f'{art}: {len(sp)} spikes ' + ', '.join(f'{d:%m-%d} x{r:.1f}' for d, v, r in sp))
    # spikes of several pages on one day are one episode, not independent evidence
    all_sp = sorted(set(all_sp))
    obs = hits(all_sp, ev, a.k, n)
    null = [hits(all_sp, ev, a.k, n, sh) for sh in range(1, n)]
    p = (1 + sum(x >= obs for x in null)) / n
    mean_null = statistics.mean(null) if null else float('nan')
    print(f'distinct spike days with an event within +-{a.k} d: {obs}/{len(all_sp)}; '
          f'circular-shift null mean {mean_null:.2f}/{len(all_sp)}, p = {p:.3f} ({n - 1} shifts)')
    json.dump({'window': [str(start), str(end)], 'k': a.k, 'ratio': a.ratio, 'event_days': len(ev),
               'days_covered': covered, 'n_days': n, 'spikes': len(all_sp), 'hits': obs,
               'null_mean': mean_null, 'p': p, 'rows': rows}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == '__main__':
    main()
