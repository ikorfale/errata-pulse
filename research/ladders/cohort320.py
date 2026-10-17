#!/usr/bin/env python3
"""Frozen cohort for check #320: do flagged ladder breaks close by repricing or only by resolution?

python3 cohort320.py freeze RUNS_DIR/history.jsonl DAY  -> cohort-320.json (refuses to overwrite)
python3 cohort320.py follow RUNS_DIR/history.jsonl [CUTOFF_DAY] -> cohort-320-status.md, cohort-320-status.json

The cohort is the pairs flagged on DAY with their hand verdict and the 3-point threshold, frozen once (design from
theone, board 91647). A pair keeps its id after it leaves the daily table: leaving the table is not an outcome.
Per pair, its FIRST exit (the first daily run without it), judged from that run's own snapshot of open markets:
  open          - flagged on every run up to the cutoff (censored, not healed)
  repriced      - both rungs still open at the exit run and their gap there is within the frozen 3-point threshold
  left-other    - both rungs still open and the gap still above the threshold (left the table for another reason)
  resolved      - a rung left the open set and its market resolved before that run's fetch time
  closed-unknown- a rung left the open set with no resolution before that run (closed, or an answer resolved)
  unavailable   - no snapshot for the exit run, or a market could not be fetched
A later re-flag does not undo the first exit (it is recorded as reflagged_later); a later resolution cannot
relabel an earlier exit (review: theone, board 91764).
Daily runs only bracket the moment a pair left the table (last seen flagged, first run without it); the
resolution time, when there is one, comes from the market record. Binary pairs and multiple-choice pairs are
reported separately, because one multiple-choice market gives many overlapping pairs.
"""
import calendar, gzip, json, os, sys, time, urllib.request

import ladders as L

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


def ms(stamp):
    return calendar.timegm(time.strptime(stamp, '%Y-%m-%dT%H:%MZ')) * 1000


def gap_at(k, kind, snap):
    """The pair's gap in one run's snapshot of open markets, or None when a rung is no longer open there."""
    if kind == 'binary':
        e, l = (snap['markets'].get(i) for i in k.split('|')[:2])
        return e['p'] - l['p'] if e and l else None
    mid, a, b = k.split('|')
    m = snap['mc'].get(mid)
    ans = {x['text']: x for x in (m or {}).get('answers', []) if x['p'] is not None and not x['resolved']}
    if kind == 'mc':
        return ans[a]['p'] - ans[b]['p'] if a in ans and b in ans else None
    nev = [x for x in ans.values() if L.NEVER.search(x['text'] or '') and not L.ANS_DATE.search(x['text'] or '')]
    return ans[a]['p'] + nev[0]['p'] - 1 if a in ans and len(nev) == 1 else None


def snapshot(runs_dir, day, cache={}):
    if day not in cache:
        f = os.path.join(runs_dir, day, 'snapshot.json.gz')
        s = json.load(gzip.open(f)) if os.path.exists(f) else None
        cache[day] = s and {'markets': {m['id']: m for m in s['markets']}, 'mc': {m['id']: m for m in s['multiple_choice']}}
    return cache[day]


def follow(hist_path, cutoff=None):
    """First exit only (theone, board 91764): the outcome is fixed at the first run without the pair, from that run's
    own snapshot, so a later re-flag or a later resolution cannot relabel it."""
    c = json.load(open(COHORT))
    runs_dir = os.path.dirname(os.path.abspath(hist_path))
    runs = sorted((d, h) for d, h in load(hist_path).items() if d > c['day'] and (cutoff is None or d <= cutoff))
    out = {}
    for k, p in c['pairs'].items():
        gone = [i for i, (d, h) in enumerate(runs) if k not in h['pairs']]
        x = gone[0] if gone else None
        before = runs[:x] if x is not None else runs
        r = {'kind': p['kind'], 'verdict': p['verdict'], 'gap0': p['gap'],
             'last_flagged': before[-1][0] if before else c['day'], 'first_unflagged': runs[x][0] if x is not None else None}
        if not runs:
            r['status'] = 'no-follow-up-run'
        elif x is None:
            r['status'] = 'open'
        else:
            day, h = runs[x]
            r['observed_at'] = h['fetched_at']
            r['reflagged_later'] = any(k in hh['pairs'] for _, hh in runs[x + 1:])
            snap = snapshot(runs_dir, day)
            g = gap_at(k, p['kind'], snap) if snap else None
            if snap is None:
                r['status'] = 'unavailable'  # no snapshot kept for that run: the reason it left is unknown
            elif g is not None:
                r['gap_at_exit'] = round(g, 4)
                r['status'] = 'repriced' if g <= c['threshold'] else 'left-other'  # left-other: still broken, not flagged
            else:  # a rung left the open set: resolved before that observation, or reason unknown
                ids = k.split('|')[:2] if p['kind'] == 'binary' else [k.split('|')[0]]
                mk = [market(i) for i in ids]
                t = [m['resolutionTime'] for m in mk if m.get('isResolved') and m.get('resolutionTime')]
                if any('_error' in m for m in mk):
                    r['status'] = 'unavailable'
                elif t and min(t) <= ms(h['fetched_at']):
                    r['status'] = 'resolved'
                    r['resolved_at'] = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(min(t) / 1000))
                else:
                    r['status'] = 'closed-unknown'  # closed or an answer resolved, no resolution time before the run
        out[k] = r
    json.dump({'cohort_day': c['day'], 'cutoff': runs[-1][0] if runs else None, 'pairs': out},
              open(os.path.join(HERE, 'cohort-320-status.json'), 'w'), indent=1)
    S = ('open', 'repriced', 'resolved', 'left-other', 'closed-unknown', 'unavailable', 'no-follow-up-run')
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
