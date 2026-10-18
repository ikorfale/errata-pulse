"""Daily ladders run: fetch, analyse, and track how long each flagged pair stays incoherent.

python3 daily.py RUNS_DIR  -> RUNS_DIR/YYYY-MM-DD/{violations.md, ladders.json.gz, snapshot.json.gz},
                              one line per run appended to RUNS_DIR/history.jsonl,
                              RUNS_DIR/persistence.md: every pair ever flagged, first/last day seen, days open.
A pair is (earlier market id, later market id) for binary ladders, (market id, earlier answer, later answer) for
multiple-choice ones. "Gone" means the pair was not flagged on a later run (repriced, resolved, or below TOL).
"""
import gzip, json, os, shutil, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
runs = sys.argv[1]
day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
out = os.path.join(runs, day)
hist_path = os.path.join(runs, 'history.jsonl')
if os.path.exists(hist_path) and any(json.loads(l)['day'] == day for l in open(hist_path)):
    # the first completed run of a UTC day is that day's sample and its snapshot is final; a rerun would overwrite
    # the snapshot the cohort judges exits by (review: theone, board 93507). A failed run never reaches history.
    sys.exit(f'{day} already has a completed run in {hist_path}; refusing to overwrite its snapshot')
os.makedirs(out, exist_ok=True)
subprocess.run([sys.executable, os.path.join(HERE, 'ladders.py'), out] + sys.argv[2:], check=True)  # e.g. --from snapshot.json (test)
poly = '--from' not in sys.argv and subprocess.run([sys.executable, os.path.join(HERE, 'poly_ladders.py'), out]).returncode == 0  # a Polymarket failure must not lose the Manifold run
for f in ('snapshot.json', 'ladders.json') + (('poly_snapshot.json', 'poly_ladders.json') if poly else ()):
    with open(os.path.join(out, f), 'rb') as a, gzip.open(os.path.join(out, f + '.gz'), 'wb') as b:
        shutil.copyfileobj(a, b)
    os.remove(os.path.join(out, f))
d = json.load(gzip.open(os.path.join(out, 'ladders.json.gz')))
snap = json.load(gzip.open(os.path.join(out, 'snapshot.json.gz')))
pairs = {f"{x['early']['id']}|{x['late']['id']}": {'kind': 'binary', 'gap': round(x['gap'], 4),
                                                    'what': f"{x['early']['q']} / {x['late']['q']}", 'url': x['early']['url']}
         for x in d['violations']}
pairs |= {f"{x['market']['id']}|{x['early']['text']}|{x['late']['text']}":
          {'kind': 'mc', 'gap': round(x['gap'], 4), 'what': f"{x['market']['q']}: {x['early']['text']} / {x['late']['text']}",
           'url': x['market']['url']} for x in d['mc_violations']}
pairs |= {f"{x['market']['id']}|{x['late']['text']}|NEVER": {'kind': 'never', 'gap': round(x['excess'], 4),
          'what': f"{x['market']['q']}: {x['late']['text']} + {x['never']['text']}", 'url': x['market']['url']}
          for x in d.get('mc_complement', [])}
review = json.load(open(os.path.join(HERE, 'review.json')))
verdict = lambda k: (review.get(k) or review.get(k.split('|')[0]) or {}).get('verdict', 'unreviewed')
row = {'day': day, 'fetched_at': d['fetched_at'], 'markets': len(snap['markets']), 'mc_markets': len(snap['multiple_choice']),
       'families': len(d['families']), 'binary_pairs': len(d['violations']), 'mc_pairs': len(d['mc_violations']),
       'mc_markets_flagged': len({x['market']['id'] for x in d['mc_violations']}),
       'never_breaks': len(d.get('mc_complement', [])),
       'verdicts': {v: sum(verdict(k) == v for k in pairs) for v in ('ladder', 'criteria-differ', 'state', 'unreviewed')},
       'pairs': pairs}
if poly:  # Polymarket: same ladders, but a break is only a trade when bid(earlier) > ask(later)
    p = json.load(gzip.open(os.path.join(out, 'poly_ladders.json.gz')))
    row['poly'] = {'ladders': p['ladders'], 'pairs': p['pairs'], 'mid_gap_pairs': len(p['violations']),
                   'crossed': [{'q': x['early']['q'], 'late': x['late']['q'], 'cross': round(x['crossed'], 4)}
                               for x in p['violations'] if x['crossed'] > 0]}
open(hist_path, 'a').write(json.dumps(row) + '\n')
hist = []
for h in map(json.loads, open(hist_path)):  # one sample per UTC day: its first completed run
    if h['day'] not in {x['day'] for x in hist}:
        hist.append(h)
days = sorted({h['day'] for h in hist})
seen = {}
for h in hist:
    for k, v in h['pairs'].items():
        s = seen.setdefault(k, {'first': h['day'], 'last': h['day'], 'runs': 0, **v})
        s['last'] = h['day']; s['runs'] += 1; s['gap'] = v['gap']
by_market = {}  # one multiple-choice market yields up to n(n-1)/2 pairs, so persistence is counted per market too
for k, s in seen.items():
    m = by_market.setdefault(k if s['kind'] == 'binary' else k.split('|')[0],
                             {'first': s['first'], 'last': s['last'], 'pairs': 0, 'max_gap': 0, 'kind': s['kind'],
                              'what': s['what'].split(': ')[0] if s['kind'] != 'binary' else s['what'], 'url': s['url'], 'key': k})
    m['first'] = min(m['first'], s['first']); m['last'] = max(m['last'], s['last'])
    m['pairs'] += 1; m.setdefault('members', []).append(s)
for m in by_market.values():
    m['max_gap'] = max(s['gap'] for s in m.pop('members') if s['last'] == m['last'])
L = [f'# Ladder breaks over time ({days[0]} to {days[-1]}, {len(days)} daily runs)', '',
     f'{len(by_market)} markets or binary pairs ever flagged, {sum(m["last"] == day for m in by_market.values())} open now.', '',
     'Review: ladder = same event and compatible criteria (incoherent prices); criteria-differ = the gap may be honest; '
     'state = not a cumulative event (matcher false positive); unreviewed = new, not read yet (review.json).', '',
     '## Per market', '',
     '| first seen | last seen | days span | open now | flagged pairs | max gap (last run) | review | market |',
     '|---|---|---|---|---|---|---|---|']
dspan = lambda a, b: (datetime.fromisoformat(b) - datetime.fromisoformat(a)).days + 1
for m in sorted(by_market.values(), key=lambda m: (m['last'] != day, -m['max_gap'])):
    L.append(f"| {m['first']} | {m['last']} | {dspan(m['first'], m['last'])} | {'yes' if m['last'] == day else 'no'} | "
             f"{m['pairs']} | {m['max_gap'] * 100:.0f} pts | {verdict(m['key'])} | [{m['what'][:120]}]({m['url']}) ({m['kind']}) |")
L += ['', '## Every pair', '',
      '| first seen | last seen | runs flagged | open now | last gap | review | pair |', '|---|---|---|---|---|---|---|']
for k, s in sorted(seen.items(), key=lambda kv: (kv[1]['last'] != day, kv[1]['first'])):
    L.append(f"| {s['first']} | {s['last']} | {s['runs']} | {'yes' if s['last'] == day else 'no'} | "
             f"{s['gap'] * 100:.0f} pts | {verdict(k)} | [{s['what'][:120]}]({s['url']}) ({s['kind']}) |")
open(os.path.join(runs, 'persistence.md'), 'w').write('\n'.join(L) + '\n')
print(f"{day}: {row['binary_pairs']} binary pairs, {row['mc_pairs']} mc pairs in {row['mc_markets_flagged']} markets, "
      f"{row['never_breaks']} never-breaks; verdicts {row['verdicts']}; "
      f"polymarket {row['poly']['pairs'] if poly else 'n/a'} pairs, {len(row['poly']['crossed']) if poly else '-'} crossed; "
      f"{len(seen)} pairs ever, {sum(s['last'] == day for s in seen.values())} open now; "
      f"{len(by_market)} markets ever, {sum(m['last'] == day for m in by_market.values())} open now")
