#!/usr/bin/env python3
"""Frozen cohort for check #320: do flagged ladder breaks close by repricing or only by resolution?

python3 cohort320.py freeze RUNS_DIR/history.jsonl DAY  -> cohort-320.json (refuses to overwrite)
python3 cohort320.py follow RUNS_DIR/history.jsonl [CUTOFF_DAY] -> cohort-320-status.md, cohort-320-status.json

The cohort is the pairs flagged on DAY with their hand verdict and the 3-point threshold, frozen once (design from
theone, board 91647). A pair keeps its id after it leaves the daily table: leaving the table is not an outcome.
Per pair, from later daily runs plus the Manifold market record:
  open       - still flagged on the last run up to the cutoff (censored, not healed)
  repriced   - left the table while both markets were still open (gap fell under 3 points)
  resolved   - left the table because a market resolved; first outcome = its resolution time
  unavailable- a market could not be fetched, so the reason it left is unknown
Daily runs only bracket the moment a pair left the table (last seen flagged, first run without it); the
resolution time, when there is one, comes from the market record. Binary pairs and multiple-choice pairs are
reported separately, because one multiple-choice market gives many overlapping pairs.
"""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
COHORT = os.path.join(HERE, 'cohort-320.json')
TOL = 0.03


def load(hist_path):
    return {h['day']: h for h in map(json.loads, open(hist_path))}  # a rerun on the same day replaces that day


def verdict(review, k):
    return (review.get(k) or review.get(k.split('|')[0]) or {}).get('verdict', 'unreviewed')


def freeze(hist_path, day):
    if os.path.exists(COHORT):
        sys.exit(f'{COHORT} exists: the cohort is frozen once')
    row = load(hist_path)[day]
    review = json.load(open(os.path.join(HERE, 'review.json')))
    pairs = {k: {**v, 'verdict': verdict(review, k)} for k, v in row['pairs'].items()}
    json.dump({'frozen_at': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'day': day, 'threshold': TOL,
               'entry_rule': 'every Manifold pair flagged by daily.py on this day (earlier rung > later rung + 3 pt)',
               'pairs': pairs}, open(COHORT, 'w'), indent=1, ensure_ascii=False)
    print(len(pairs), 'pairs frozen;', {v: sum(p['verdict'] == v for p in pairs.values())
                                        for v in ('ladder', 'criteria-differ', 'state', 'unreviewed')})


def market(mid, cache={}):
    if mid not in cache:
        try:
            with urllib.request.urlopen(f'https://api.manifold.markets/v0/market/{mid}', timeout=30) as r:
                cache[mid] = json.load(r)
        except Exception as e:  # noqa: BLE001 - any failure means "unavailable", recorded as such
            cache[mid] = {'_error': str(e)[:80]}
    return cache[mid]


def follow(hist_path, cutoff=None):
    c = json.load(open(COHORT))
    runs = sorted((d, h) for d, h in load(hist_path).items() if d > c['day'] and (cutoff is None or d <= cutoff))
    out = {}
    for k, p in c['pairs'].items():
        seen = [d for d, h in runs if k in h['pairs']]
        last_seen = seen[-1] if seen else c['day']
        after = [d for d, _ in runs if d > last_seen]
        r = {'kind': p['kind'], 'verdict': p['verdict'], 'gap0': p['gap'], 'last_flagged': last_seen,
             'first_unflagged': after[0] if after else None}
        if not runs:
            r['status'] = 'no-follow-up-run'
        elif not after:
            r['status'] = 'open'
        else:
            ids = [k.split('|')[0]] if p['kind'] != 'binary' else k.split('|')[:2]
            ms = [market(i) for i in ids]
            if any('_error' in m for m in ms):
                r['status'] = 'unavailable'
            elif any(m.get('isResolved') for m in ms):
                t = min(m.get('resolutionTime') or 9e15 for m in ms if m.get('isResolved'))
                r['status'] = 'resolved'
                r['resolved_at'] = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(t / 1000))
            else:
                r['status'] = 'repriced'
        out[k] = r
    json.dump({'cohort_day': c['day'], 'cutoff': runs[-1][0] if runs else None, 'pairs': out},
              open(os.path.join(HERE, 'cohort-320-status.json'), 'w'), indent=1)
    S = ('open', 'repriced', 'resolved', 'unavailable', 'no-follow-up-run')
    L = [f"# Check #320: the cohort flagged on {c['day']} (frozen {c['frozen_at']})", '',
         f"Follow-up runs: {len(runs)}, last {runs[-1][0] if runs else '-'}. 'open' is censored, not healed.", '',
         '| kind | verdict | pairs | ' + ' | '.join(S) + ' |', '|' + '---|' * (3 + len(S))]
    for kind in ('binary', 'mc', 'never'):
        for v in ('ladder', 'criteria-differ', 'state', 'unreviewed'):
            g = [r for r in out.values() if r['kind'] == kind and r['verdict'] == v]
            if g:
                L.append(f'| {kind} | {v} | {len(g)} | ' + ' | '.join(str(sum(r["status"] == s for r in g)) for s in S) + ' |')
    open(os.path.join(HERE, 'cohort-320-status.md'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    {'freeze': freeze, 'follow': follow}[sys.argv[1]](*sys.argv[2:])
