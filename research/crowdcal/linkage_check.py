"""Follow-up to cluster_check.py after glitchfox (board 89787) and theone (board 89844).

1. Linkage: union-find on a cosine threshold is single linkage, and single linkage chains.
   On the real titles, compare single / average / complete linkage over a tau ladder
   (no close-month block, still blocked by v2 group, as any-mX in cluster_check.py):
   cluster count and largest-cluster share. A usable tau sits on a plateau, not on a cliff.
2. Estimator: for each grouping print three gaps with a cluster bootstrap (same draws for all three):
   equal-cluster (each cluster's mean residual counts once; cluster_check.py),
   equal-market (theone's pooled estimator: sampled residual totals / sampled market counts),
   earliest rung (one market per cluster: the one that closes first, as glitchfox suggested).
3. Sub-10% bin: if prices were calibrated and clusters independent, P(0 YES) = prod(1 - p_c)
   with p_c the cluster-level mean price of the bin's markets in that cluster (glitchfox's test).

Groupings never look at outcomes. Needs scipy (run with ~/venv/bin/python).
"""
import sys
from collections import defaultdict
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

sys.argv = sys.argv[:1]
import cluster_check as C  # prints its own tables first; ours follow the marker below

print('\n\n======== linkage_check.py ========')


def hier_groups(R, S, tau, method):
    """Clusters cut at distance 1 - tau, inside each v2 group block (no month block)."""
    lab = [None] * len(R)
    blk = defaultdict(list)
    for i, r in enumerate(R):
        blk[r['g2']].append(i)
    for b, idx in blk.items():
        if len(idx) == 1:
            lab[idx[0]] = (b, 0)
            continue
        D = np.clip(1 - S[np.ix_(idx, idx)], 0, None)
        np.fill_diagonal(D, 0)
        Z = linkage(squareform(D, checks=False), method=method)
        for i, c in zip(idx, fcluster(Z, t=1 - tau, criterion='distance')):
            lab[i] = (b, int(c))
    return lab


def groups_of(g):
    by = defaultdict(list)
    for i, k in enumerate(g):
        by[k].append(i)
    return [np.array(v) for v in by.values()]


def estimators(R, x, res, low, g, draws=2000):
    G = groups_of(g)
    cs = np.array([res[v].sum() for v in G]); cn = np.array([len(v) for v in G]); cm = cs / cn
    close = np.array([r['close'] for r in R])
    first = np.array([v[np.argmin(close[v])] for v in G])  # earliest-closing rung of each cluster
    er = res[first]
    rng = np.random.default_rng(7)
    bc, bm, be = [], [], []
    for _ in range(draws):
        j = rng.integers(0, len(G), len(G))
        bc.append(cm[j].mean()); bm.append(cs[j].sum() / cn[j].sum()); be.append(er[j].mean())
    out = {}
    for name, pt, bs in (('eq-cluster', cm.mean(), bc), ('eq-market', res.mean(), bm), ('earliest', er.mean(), be)):
        out[name] = (pt, *np.percentile(bs, [2.5, 97.5]))
    # sub-10% bin at cluster level
    lowG = [v[low[v]] for v in G]
    lowG = [v for v in lowG if len(v)]
    pc = np.array([x[v].mean() for v in lowG])
    yes = sum(int((x[v] - res[v] > 0.5).any()) for v in lowG)  # outcome = price - residual
    out['low'] = (len(lowG), pc.mean(), yes, float(np.prod(1 - pc)), float((1 - pc.mean()) ** len(pc)))
    return len(G), max(len(v) for v in G) / len(R), out


def run(R, h, label):
    x = np.array([r[h] for r in R]); y = np.array([r['res'] == 'YES' for r in R], float); res = x - y
    low = x < 0.10
    T = C.tfidf(R); S = T @ T.T
    print(f'\n# {label}: n={len(R)}')
    print('## 1. cluster count vs tau (largest cluster share in brackets), no close-month block')
    taus = (0.7, 0.6, 0.5, 0.4, 0.3, 0.2)
    print(f'{"method":<9}' + ''.join(f'{"tau=" + str(t):>16}' for t in taus))
    ladder = []
    for method in ('single', 'average', 'complete'):
        cells = []
        for t in taus:
            g = hier_groups(R, S, t, method)
            k, big, out = estimators(R, x, res, low, g)
            cells.append(f'{k:5d} ({100 * big:4.1f}%)')
            ladder.append((method, t, k, big, out))
        print(f'{method:<9}' + ''.join(f'{c:>16}' for c in cells))
    uf = C.tau_groups(R, 0.5, S, False)
    print(f'check: union-find any-m0.5 gives {len(set(uf))} clusters; single linkage tau=0.5 gives '
          f'{len(set(hier_groups(R, S, 0.5, "single")))}')
    print('\n## 2. gap (pp) under three estimators, cluster bootstrap 2000 draws, seed 7, same draws')
    print(f'{"method":<9} {"tau":>4} {"clusters":>8} {"eq-cluster":>26} {"eq-market":>26} {"earliest rung":>26}')
    for method, t, k, big, out in ladder:
        cells = [f'{100 * p:+5.2f} [{100 * a:+5.2f},{100 * b:+5.2f}]' for p, a, b in (out[n] for n in ('eq-cluster', 'eq-market', 'earliest'))]
        print(f'{method:<9} {t:4.1f} {k:8d} ' + ' '.join(f'{c:>26}' for c in cells))
    print('\n## 3. sub-10% bin: clusters, mean cluster price, clusters with a YES, P(0 YES | calibrated, independent)')
    print(f'{"method":<9} {"tau":>4} {"<10% cl":>8} {"mean p_c":>9} {"YES cl":>7} {"prod(1-p_c)":>12} {"(1-pbar)^n":>11}')
    for method, t, k, big, out in ladder:
        n, pb, yes, pr, jb = out['low']
        print(f'{method:<9} {t:4.1f} {n:8d} {pb:9.4f} {yes:7d} {pr:12.2e} {jb:11.2e}')


R = [r for r in C.rows if r['g2'] == 'escalation' and r.get('30d') is not None]
run(R, '30d', 'v2 escalation T-30d')
