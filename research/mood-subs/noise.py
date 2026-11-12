#!/usr/bin/env python3
"""H5 baseline: per-channel noise and drift of exact subscriber counts, first 7 days of the census.
No strike data is read here (the prereg must be frozen before struck-vs-far is looked at).
Out: noise.json + printed summary. Unit: % change per 12 h step (log-diff * 100)."""
import json, collections, statistics as st, math, sys
import os
F = os.path.expanduser('~/work/pulse/mood/subs/census.jsonl')
rows = [json.loads(l) for l in open(F)]
ser = collections.defaultdict(list)
for r in rows:
    if r['subs']: ser[(r['region'], r['role'], r['handle'])].append((r['ts'], r['subs']))
out = []
for k, v in ser.items():
    v.sort()
    from datetime import datetime
    t = [datetime.fromisoformat(a.replace('Z', '+00:00')) for a, _ in v]; s = [b for _, b in v]
    steps = []
    for i in range(1, len(v)):
        h = (t[i] - t[i-1]).total_seconds() / 3600
        if h < 1: continue
        steps.append(100 * math.log(s[i] / s[i-1]) * 12 / h)   # normalised to a 12-h step
    if len(steps) < 6: continue
    med = st.median(steps); mad = st.median(abs(x - med) for x in steps) * 1.4826
    big = max(steps, key=lambda x: abs(x - med))
    out.append({'region': k[0], 'role': k[1], 'handle': k[2], 'n': len(steps), 'subs_last': s[-1],
                'drift_12h_pct': round(med, 4), 'noise_12h_pct': round(mad, 4),
                'max_step_pct': round(big, 4), 'max_z': round((big - med) / mad, 1) if mad else None,
                'week_pct': round(100 * math.log(s[-1] / s[0]), 3)})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noise.json'), 'w'), ensure_ascii=False, indent=0)
print(f'{len(out)} channels with >=6 steps (of {len(ser)})')
for role in ('governor', 'mchs'):
    o = [x for x in out if x['role'] == role]
    if not o: continue
    q = lambda key: [round(x, 3) for x in st.quantiles([x[key] for x in o], n=4)]
    print(f"{role}: n={len(o)} drift/12h quartiles {q('drift_12h_pct')} noise/12h quartiles {q('noise_12h_pct')} week% quartiles {q('week_pct')}")
    print(f"  channels with a step >= 5 robust SD: {sum(1 for x in o if x['max_z'] and abs(x['max_z']) >= 5)}; zero-noise (counter flat): {sum(1 for x in o if x['noise_12h_pct'] == 0)}")
small = [x for x in out if x['subs_last'] < 5000]
print(f'small channels (<5000 subs): {len(small)}, median noise {st.median([x["noise_12h_pct"] for x in small]) if small else None}')
print('largest jumps:'); [print(' ', x['role'], x['handle'], x['subs_last'], 'step', x['max_step_pct'], 'z', x['max_z']) for x in sorted(out, key=lambda x: -abs(x['max_z'] or 0))[:6]]
