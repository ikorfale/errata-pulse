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
os.makedirs(out, exist_ok=True)
subprocess.run([sys.executable, os.path.join(HERE, 'ladders.py'), out] + sys.argv[2:], check=True)  # e.g. --from snapshot.json (test)
for f in ('snapshot.json', 'ladders.json'):
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
hist_path = os.path.join(runs, 'history.jsonl')
open(hist_path, 'a').write(json.dumps(row) + '\n')
hist = list({h['day']: h for h in map(json.loads, open(hist_path))}.values())  # a rerun on the same day replaces that day
days = sorted({h['day'] for h in hist})
seen = {}
for h in hist:
    for k, v in h['pairs'].items():
        s = seen.setdefault(k, {'first': h['day'], 'last': h['day'], 'runs': 0, **v})
        s['last'] = h['day']; s['runs'] += 1; s['gap'] = v['gap']
L = [f'# Ladder pairs over time ({days[0]} to {days[-1]}, {len(days)} daily runs)', '',
     'Review: ladder = same event and compatible criteria (incoherent prices); criteria-differ = the gap may be honest; '
     'state = not a cumulative event (matcher false positive); unreviewed = new, not read yet (review.json).', '',
     '| first seen | last seen | runs flagged | open now | last gap | review | pair |', '|---|---|---|---|---|---|---|']
for k, s in sorted(seen.items(), key=lambda kv: (kv[1]['last'] != day, kv[1]['first'])):
    L.append(f"| {s['first']} | {s['last']} | {s['runs']} | {'yes' if s['last'] == day else 'no'} | "
             f"{s['gap'] * 100:.0f} pts | {verdict(k)} | [{s['what'][:120]}]({s['url']}) ({s['kind']}) |")
open(os.path.join(runs, 'persistence.md'), 'w').write('\n'.join(L) + '\n')
print(f"{day}: {row['binary_pairs']} binary pairs, {row['mc_pairs']} mc pairs in {row['mc_markets_flagged']} markets, "
      f"{row['never_breaks']} never-breaks; verdicts {row['verdicts']}; "
      f"{len(seen)} pairs ever, {sum(s['last'] == day for s in seen.values())} open now")
