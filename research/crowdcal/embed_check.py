"""Do synonyms TF-IDF cannot see hide more duplicate questions? (glitchfox, board 89787: "Kremlin" vs "Russia")

Embeds the 518 v2-escalation titles with OpenAI text-embedding-3-small (cached in embed_cache.npy, keyed by
title order), clusters with average linkage on 1 - cosine inside each group block (no close-month block, as
linkage_check.py), and prints for a tau ladder: clusters, largest share, the three gap estimators and the
zero-YES probability of the sub-10% bin. Then lists title pairs the embedding puts together (cosine >= 0.8)
that TF-IDF scores below 0.3, so a reader can judge by eye whether they are the same question.
Needs scipy (run with ~/venv/bin/python) and an OpenAI key in ~/.config/agent-accounts/openai.key.
"""
import json, os, sys, urllib.request
import numpy as np

sys.argv = sys.argv[:1]
import linkage_check as L  # runs cluster_check and linkage_check first; ours follow the marker below

C = L.C
print('\n\n======== embed_check.py ========')
R = [r for r in C.rows if r['g2'] == 'escalation' and r.get('30d') is not None]
titles = [r['q'] for r in R]
cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'embed_cache.json')
E = None
if os.path.exists(cache):
    c = json.load(open(cache))
    if c['titles'] == titles:
        E = np.array(c['emb'])
if E is None:
    key = open(os.path.expanduser('~/.config/agent-accounts/openai.key')).read().strip()
    out = []
    for i in range(0, len(titles), 200):
        req = urllib.request.Request('https://api.openai.com/v1/embeddings',
                                     data=json.dumps({'model': 'text-embedding-3-small', 'input': titles[i:i + 200]}).encode(),
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        out += [d['embedding'] for d in json.load(urllib.request.urlopen(req, timeout=60))['data']]
    E = np.array(out)
    json.dump({'model': 'text-embedding-3-small', 'titles': titles, 'emb': E.round(6).tolist()}, open(cache, 'w'))
E = E / np.linalg.norm(E, axis=1, keepdims=True)
SE = E @ E.T
T = C.tfidf(R); ST = T @ T.T

x = np.array([r['30d'] for r in R]); y = np.array([r['res'] == 'YES' for r in R], float); res = x - y
low = x < 0.10
iu = np.triu_indices(len(R), 1)
print(f'n={len(R)}; embedding cosine over all pairs: median {np.median(SE[iu]):.3f}, 99th pct {np.percentile(SE[iu], 99):.3f}')
print(f'{"tau":>4} {"clusters":>8} {"largest":>8} {"eq-cluster":>26} {"eq-market":>26} {"earliest rung":>26} {"<10% cl":>8} {"P(0 YES)":>10}')
for t in (0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6):
    g = L.hier_groups(R, SE, t, 'average')
    k, big, out = L.estimators(R, x, res, low, g)
    cells = [f'{100 * p:+5.2f} [{100 * a:+5.2f},{100 * b:+5.2f}]' for p, a, b in (out[n] for n in ('eq-cluster', 'eq-market', 'earliest'))]
    n, pb, yes, pr, jb = out['low']
    print(f'{t:4.2f} {k:8d} {100 * big:7.1f}% ' + ' '.join(f'{c:>26}' for c in cells) + f' {n:8d} {pr:10.2e}' + (f'  YES clusters {yes}' if yes else ''))

pairs = [(SE[i, j], ST[i, j], i, j) for i, j in zip(*iu) if SE[i, j] >= 0.8 and ST[i, j] < 0.3 and R[i]['g2'] == R[j]['g2']]
pairs.sort(reverse=True)
print(f'\npairs with embedding cosine >= 0.8 and TF-IDF cosine < 0.3: {len(pairs)} (top 25 by embedding cosine)')
for se, st, i, j in pairs[:25]:
    print(f'{se:.3f} {st:.3f} | {titles[i][:80]} || {titles[j][:80]}')
