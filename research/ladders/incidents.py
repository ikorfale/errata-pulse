#!/usr/bin/env python3
"""Incident cohort (#329, macsidekick on Moltbook, 17.10): how fast does a FRESH ladder break heal?

python3 incidents.py RUNS_DIR/history.jsonl -> incidents.json, incidents.md (rebuilt from all runs each time)

The 16.10 cohort (#320) is a one-day cross-section, so it over-samples long-lived breaks (length bias). Here the
entry is the break itself: a pair that was NOT flagged in run t, with both rungs open in run t's snapshot and a gap
within the 3-point threshold there, and IS flagged in run t+1. Excluded at entry, and counted:
  new-detector - run t had no detector for this kind (the 'never' check started on 17.10)
  born-broken  - a rung was not open in run t (a new market or answer, not a break of an existing order)
  no-snapshot  - run t kept no snapshot
Per incident, two clocks:
  order restored - the first later run where the pair is unflagged, judged from that run's snapshot exactly as in
                   cohort320 (repriced / left-other / resolved / closed-unknown / unavailable); censored if still
                   flagged. Daily runs bracket the moment: reported as (last flagged, first unflagged).
  next trade     - binary pairs only: from the bets API, the time from the last bet on either rung before run t+1
                   (the bet that left the pair broken) to the next bet on either rung. Censored at fetch time.
"""
import gzip, json, os, sys, time, urllib.request

import cohort320 as C

HERE = os.path.dirname(os.path.abspath(__file__))


def bets(cid, cache={}):
    if cid not in cache:
        try:
            req = urllib.request.Request(f'https://api.manifold.markets/v0/bets?contractId={cid}&limit=1000',
                                         headers={'User-Agent': 'errata-ladders (AI agent, errata.page)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                cache[cid] = sorted(b['createdTime'] for b in json.load(r) if not b.get('isRedemption'))
        except Exception as e:  # noqa: BLE001
            cache[cid] = None
    return cache[cid]


def next_trade(k, t1_ms, now_ms):
    ts = [bets(i) for i in k.split('|')[:2]]
    if any(t is None for t in ts):
        return {'status': 'unavailable'}
    allb = sorted(ts[0] + ts[1])
    before = [b for b in allb if b <= t1_ms]
    if not before:
        return {'status': 'unavailable'}
    after = [b for b in allb if b > before[-1]]
    if not after:
        return {'status': 'censored', 'hours': round((now_ms - before[-1]) / 3.6e6, 1)}
    return {'status': 'traded', 'hours': round((after[0] - before[-1]) / 3.6e6, 1)}


def build(hist_path):
    runs_dir = os.path.dirname(os.path.abspath(hist_path))
    runs = sorted(C.load(hist_path).items())
    now = int(time.time() * 1000)
    inc, excluded = {}, {'new-detector': 0, 'born-broken': 0, 'no-snapshot': 0, 'over-threshold-at-t': 0}
    for i in range(len(runs) - 1):
        (d0, h0), (d1, h1) = runs[i], runs[i + 1]
        for k, p in h1['pairs'].items():
            if k in h0['pairs']:
                continue
            if p['kind'] == 'never' and h0.get('never_breaks') is None:
                excluded['new-detector'] += 1; continue
            snap0 = C.snapshot(runs_dir, d0)
            if snap0 is None:
                excluded['no-snapshot'] += 1; continue
            g0 = C.gap_at(k, p['kind'], snap0)
            if g0 is None:
                excluded['born-broken'] += 1; continue
            if g0 > C.TOL:  # unflagged at t although over the threshold (filtered for another reason): not fresh
                excluded['over-threshold-at-t'] += 1; continue
            later = runs[i + 2:]
            gone = [j for j, (_, h) in enumerate(later) if k not in h['pairs']]
            r = {'kind': p['kind'], 'what': p['what'], 'url': p['url'], 'gap_before': round(g0, 4), 'gap_after': p['gap'],
                 'coherent_at': h0['fetched_at'], 'broken_at': h1['fetched_at']}
            if not gone:
                r['order'] = {'status': 'open', 'last_flagged': (later[-1][0] if later else d1)}
            else:
                d, h = later[gone[0]]
                snap = C.snapshot(runs_dir, d)
                g = C.gap_at(k, p['kind'], snap) if snap else None
                st = ('unavailable' if snap is None else 'repriced' if g is not None and g <= C.TOL
                      else 'left-other' if g is not None else 'rung-closed')
                r['order'] = {'status': st, 'last_flagged': (later[gone[0] - 1][0] if gone[0] else d1),
                              'first_unflagged': d, 'gap_at_exit': None if g is None else round(g, 4)}
            if p['kind'] == 'binary':
                r['next_trade'] = next_trade(k, C.ms(h1['fetched_at']), now)
            inc[f'{d1}|{k}'] = r
    json.dump({'built_at': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'runs': [d for d, _ in runs],
               'excluded': excluded, 'incidents': inc}, open(os.path.join(HERE, 'incidents.json'), 'w'), indent=1)
    S = ('open', 'repriced', 'left-other', 'rung-closed', 'unavailable')
    L = ['# Incident cohort (#329): fresh ladder breaks and how they heal', '',
         f"Runs: {len(runs)} ({runs[0][0]} .. {runs[-1][0]}). Consecutive run pairs: {max(len(runs) - 1, 0)}.",
         f"Excluded at entry: {excluded}.", '', '| kind | incidents | ' + ' | '.join(S) + ' |', '|' + '---|' * (2 + len(S))]
    for kind in ('binary', 'mc', 'never'):
        g = [r for r in inc.values() if r['kind'] == kind]
        L.append(f'| {kind} | {len(g)} | ' + ' | '.join(str(sum(r["order"]["status"] == s for r in g)) for s in S) + ' |')
    nt = [r['next_trade'] for r in inc.values() if 'next_trade' in r]
    L += ['', f"Binary next trade: traded {sum(x['status'] == 'traded' for x in nt)}, censored "
              f"{sum(x['status'] == 'censored' for x in nt)}, unavailable {sum(x['status'] == 'unavailable' for x in nt)}; "
              f"hours to next trade (traded): {sorted(x['hours'] for x in nt if x['status'] == 'traded')}", '',
          "'open' is censored, not healed. 'rung-closed' needs the market record to tell resolution from closing."]
    open(os.path.join(HERE, 'incidents.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    build(sys.argv[1])
