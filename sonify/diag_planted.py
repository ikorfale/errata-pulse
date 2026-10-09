"""Diagnostic for calib.py's low power: on a planted day (+3.5 SD in one series in each of 3 families), how often
does each planted family put that day in its own top 3, and how often is the day a chord day (>=3 families)?
Family voice and top-3 rule copied from chord_null.py (NOCLIP, CARRIED); panels from calib.py's generator."""
import sys, os, json, numpy as np
sys.argv = [sys.argv[0], sys.argv[1], '0']; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calib.py')).read().split('for scen in SCEN:')[0])
idx = {x: i for i, x in enumerate(days)}
def zser(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    for i in range(1, 30):
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med))
    if mad == 0: mad = np.std(v[ok]) or 1.0
    return np.nan_to_num((v - med) / mad)
def voices(dd):
    V = {}
    for f in FAMS:
        rows = [(s, z) for s in dd['signals'] if s['family'] == f and (z := zser(s.get('series') or [])) is not None]
        if not rows: continue
        m = np.abs(np.vstack([z for _, z in rows])).max(axis=0); mad = 1.4826 * np.median(np.abs(m - np.median(m))) or 1.0
        v = (m - np.median(m)) / mad
        meas = np.zeros(30, bool)
        for s, _ in rows:
            for t, x in s['series']:
                if t in idx and x is not None: meas[idx[t]] = True
        V[f] = np.where(meas, v, -np.inf)
    return V
hit = {f: [0, 0] for f in FAMS}; chord = 0; K = int(os.environ.get('K', 200))
for k in range(K):
    rng_state = rng.bit_generator.state
    p = panel('spike1')
    # recover the planted day and families: series whose value jumped are the ones panel() touched; re-derive by replaying
    rng.bit_generator.state = rng_state; ar1(30); [ar1(30) for _ in FAMS]
    dd0 = int(rng.integers(0, 20)); fams = list(rng.choice(FAMS, 3, replace=False))
    p = p; V = voices(p); n = 0
    for f in fams:
        top = V[f] >= np.sort(V[f])[-3]; hit[f][1] += 1; hit[f][0] += bool(top[dd0]); n += bool(top[dd0])
    # other families can also be in their top 3 on that day by chance
    n_all = sum(bool((V[f] >= np.sort(V[f])[-3])[dd0]) for f in V)
    chord += n_all >= 3
for f in FAMS:
    nser = sum(1 for s in d['signals'] if s['family'] == f)
    print(f'{f:13s} series {nser:3d}: planted day in family top 3 in {hit[f][0]}/{hit[f][1]} = {hit[f][0] / max(hit[f][1], 1):.2f}')
print(f'planted day is a chord day (>=3 families in top 3): {chord}/{K} = {chord / K:.2f}')
