"""Sensitivity: split every family whose outcomes break ladder monotonicity (a later deadline NO after an earlier YES)
into singletons; recompute the earliest-rung gap, family / calendar-month bootstrap CIs (theone's estimator, seed 7,
100k draws) and the sub-10% any-member P(0 YES). Inputs: errata-pulse@1fea354 research/crowdcal markets.json families.json."""
import json, sys
from collections import defaultdict
from datetime import datetime, timezone
import numpy as np
m = json.load(open(sys.argv[1])); f = json.load(open(sys.argv[2]))
rows = []
for r in m:
    if r['id'] not in f: continue
    z = f[r['id']]
    p = 1 - r['30d'] if z['flipped'] else r['30d']; y = int(r['res'] == 'YES') ^ z['flipped']
    rows.append(dict(id=r['id'], fam=str(z['family']), close=r['close'], p=p, y=y,
                     cm=datetime.fromtimestamp(r['close'] / 1000, timezone.utc).strftime('%Y-%m')))
def nonmono(v):
    ys = [t['y'] for t in sorted(v, key=lambda t: t['close'])]; return ys != sorted(ys)
def run(label, split):
    fam = defaultdict(list)
    for t in rows: fam[t['fam']].append(t)
    bad = {k for k, v in fam.items() if nonmono(v)} if split else set()
    G = defaultdict(list)
    for t in rows: G[t['id'] if t['fam'] in bad else t['fam']].append(t)
    reps = [min(v, key=lambda t: t['close']) for _, v in sorted(G.items())]
    gap = np.array([t['p'] - t['y'] for t in reps])
    out = [f'{label}: split={len(bad)} families={len(G)} reps YES={sum(t["y"] for t in reps)} gap_pp={100 * gap.mean():+.3f}']
    for bl, keys in [('family', range(len(reps))), ('calendar_month', [t['cm'] for t in reps])]:
        g = defaultdict(list)
        for i, k in enumerate(keys): g[k].append(i)
        grp = [g[k] for k in sorted(g, key=str)]
        sz = np.array([len(v) for v in grp]); sm = np.array([gap[v].sum() for v in grp])
        rng = np.random.default_rng(7); bs = []
        for _ in range(50):
            ix = rng.integers(0, len(grp), size=(2000, len(grp))); bs.append(sm[ix].sum(1) / sz[ix].sum(1))
        lo, hi = 100 * np.percentile(np.concatenate(bs), [2.5, 97.5])
        out.append(f'  {bl:15s} blocks={len(grp):3d} CI_pp=[{lo:+.3f},{hi:+.3f}]')
    low = [[t for t in v if t['p'] < 0.10] for v in G.values()]; low = [v for v in low if v]
    pc = np.array([np.mean([t['p'] for t in v]) for v in low])
    out.append(f'  sub-10% any-member families={len(low)} YES={sum(max(t["y"] for t in v) for v in low)} '
               f'mean_p={pc.mean():.4f} indep_P0={np.prod(1 - pc):.3e}')
    lowr = [t for t in reps if t['p'] < 0.10]
    out.append(f'  sub-10% earliest-rung families={len(lowr)} YES={sum(t["y"] for t in lowr)} '
               f'indep_P0={np.prod([1 - t["p"] for t in lowr]):.3e}')
    print('\n'.join(out))
run('as published', False); run('non-monotone families split', True)
