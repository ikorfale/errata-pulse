"""How much does event-level clustering change the crowdcal result? (glitchfox's proposal, board 89729)

For v2-escalation markets at T-30d (and the pre-registered v1 sample) and for a ladder of groupings
from fine to coarse, print: number of clusters, the 1/k-weighted gap (each cluster counts once), a
cluster-bootstrap 95% CI, the intraclass correlation of the residual (price - outcome), and, for the
sub-10% price bin, how many clusters the 299 markets fall into and the rule-of-three bound 3/clusters.

Groupings never look at outcomes:
  tau=X     union-find merge of titles whose TF-IDF cosine >= X inside a block (v2 group, close month)
  any-mX    the same without the close-month block: 'by 2024' and 'by 2025' versions of one question can merge
  v2-cl     the capitalised-token + close-quarter key used in analyse.py
  term      the search term the market was found by (18 terms)
"""
import json, re, sys
from collections import defaultdict, Counter
import numpy as np
sys.argv = sys.argv[:1]
import analyse as A  # re-runs analyse.py quietly enough; gives grp1/grp2/cluster and rows

rows = A.rows
STOPW = set('will the a an in by before of on at and or to be is does do if what which who how for with any its it this that than more less after during from as end 2022 2023 2024 2025 2026 2027 year'.split())

def toks(q):
    return [w for w in re.findall(r"[a-z][a-z'-]+", q.lower()) if w not in STOPW]

def month(r):
    return r['close'] // (86400000 * 30)

def tfidf(R):
    docs = [Counter(toks(r['q'])) for r in R]
    df = Counter(w for d in docs for w in d)
    vocab = {w: i for i, w in enumerate(df)}
    M = np.zeros((len(R), len(vocab)))
    for i, d in enumerate(docs):
        for w, c in d.items():
            M[i, vocab[w]] = (1 + np.log(c)) * np.log((1 + len(R)) / (1 + df[w]))
    n = np.linalg.norm(M, axis=1, keepdims=True); n[n == 0] = 1
    return M / n

def tau_groups(R, tau, S, by_month=True):
    par = list(range(len(R)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    blk = defaultdict(list)
    for i, r in enumerate(R):
        blk[(r['g2'], month(r) if by_month else 0)].append(i)
    for idx in blk.values():
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                if S[idx[a], idx[b]] >= tau:
                    par[f(idx[a])] = f(idx[b])
    return [f(i) for i in range(len(R))]

def icc(res, g):
    by = defaultdict(list)
    for v, k in zip(res, g):
        by[k].append(v)
    G = list(by.values()); N = len(res); K = len(G)
    if K < 2 or K == N:
        return float('nan')
    m = res.mean()
    ssb = sum(len(x) * (np.mean(x) - m) ** 2 for x in G); ssw = sum(((np.array(x) - np.mean(x)) ** 2).sum() for x in G)
    msb = ssb / (K - 1); msw = ssw / (N - K)
    k0 = (N - sum(len(x) ** 2 for x in G) / N) / (K - 1)
    return (msb - msw) / (msb + (k0 - 1) * msw)

def report(R, h, label):
    x = np.array([r[h] for r in R]); y = np.array([r['res'] == 'YES' for r in R], float); res = x - y
    S = tfidf(R) @ tfidf(R).T
    ladder = [(f'tau={t}', tau_groups(R, t, S)) for t in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3)]
    ladder += [(f'any-m{t}', tau_groups(R, t, S, False)) for t in (0.5, 0.3)]
    ladder += [('v2-cl', [r['cl'] for r in R]), ('term', [r['term'] for r in R]), ('market', list(range(len(R))))]
    low = x < 0.10
    print(f'\n# {label}: n={len(R)}, raw gap {res.mean():+.4f}; sub-10% bin n={int(low.sum())}, YES={int(y[low].sum())}, mean price {x[low].mean():.4f}')
    print(f'{"grouping":<9} {"clusters":>8} {"w-gap(1/k)":>10} {"95% cluster CI":>18} {"width":>6} {"ICC":>6} {"<10% clusters":>13} {"3/clusters":>10}')
    for name, g in ladder:
        rng = np.random.default_rng(7)  # per row, so adding a row does not move the others
        by = defaultdict(list)
        for i, k in enumerate(g):
            by[k].append(i)
        G = [np.array(v) for v in by.values()]
        cm = np.array([res[v].mean() for v in G])  # cluster means: each cluster weight 1
        bs = [cm[rng.integers(0, len(G), len(G))].mean() for _ in range(2000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        lowc = len({g[i] for i in np.where(low)[0]})
        print(f'{name:<9} {len(G):8d} {cm.mean():+10.4f} [{lo:+.4f},{hi:+.4f}] {hi - lo:6.4f} {icc(res, g):6.3f} {lowc:13d} {3 / lowc:10.4f}')

R = [r for r in rows if r['g2'] == 'escalation' and r.get('30d') is not None]
report(R, '30d', 'v2 escalation T-30d')
R = [r for r in rows if r['g1'] == 'escalation' and r.get('30d') is not None]
report(R, '30d', 'v1 escalation T-30d (pre-registered sample)')
