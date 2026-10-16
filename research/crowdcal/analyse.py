"""Calibration tables and chart from markets.json (see PREREG.md)."""
import json, random, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows = json.load(open('markets.json'))
import re
ESC = re.compile(r'attack|strike|invade|invasion|nuclear|declare war|mobili[sz]|missile|bomb|troops|clash|shoot down|assassinat|coup|blockade|war with|war between|war against', re.I)
PEACE = re.compile(r'\bend|ceasefire|cease-fire|peace|truce|\bdeal|agreement|negotiat|talks', re.I)
for r in rows:
    r['grp'] = 'peace' if PEACE.search(r['q']) else ('escalation' if ESC.search(r['q']) else 'other')
ALL = rows
out = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)
p(f'markets: {len(rows)}; YES {sum(r["res"]=="YES" for r in rows)}')
BINS = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0001]
random.seed(1)
for grp, h in [(g, h) for g in ('escalation', 'peace', 'other', 'all') for h in ('30d', '7d')]:
    R = [r for r in ALL if r.get(h) is not None and grp in ('all', r['grp'])]
    if len(R) < 5: p(f'\n== {grp} T-{h}: n={len(R)} too few'); continue
    x = np.array([r[h] for r in R]); y = np.array([r['res'] == 'YES' for r in R], float)
    gap = x.mean() - y.mean()
    bs = [] 
    for _ in range(2000):
        i = np.random.default_rng(len(bs)).integers(0, len(R), len(R))
        bs.append(x[i].mean() - y[i].mean())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    brier = ((x - y) ** 2).mean(); base = ((y.mean() - y) ** 2).mean()
    p(f'\n== {grp} T-{h}: n={len(R)}  mean crowd p={x.mean():.3f}  YES rate={y.mean():.3f}  gap={gap:+.3f} (95% bootstrap {lo:+.3f}..{hi:+.3f})')
    p(f'   Brier crowd {brier:.4f}  vs constant(YES rate) {base:.4f}  skill {1-brier/base:+.3f}')
    p('   bin        n   mean p  YES rate')
    for a, b in zip(BINS[:-1], BINS[1:]):
        m = (x >= a) & (x < b)
        if m.sum():
            p(f'   {a:.1f}-{min(b,1):.1f}  {m.sum():4d}   {x[m].mean():.3f}   {y[m].mean():.3f}')
    if grp == 'escalation': globals()['cal_' + h] = (x, y)
fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150)
for h, c in (('30d', '#c0392b'), ('7d', '#2c3e50')):
    x, y = globals()['cal_' + h]
    xs, ys, ns = [], [], []
    for a, b in zip(BINS[:-1], BINS[1:]):
        m = (x >= a) & (x < b)
        if m.sum() >= 5:
            xs.append(x[m].mean()); ys.append(y[m].mean()); ns.append(m.sum())
    ax.plot(xs, ys, 'o-', color=c, label=f'T-{h} (n={len(x)})')
    for a, b, n in zip(xs, ys, ns):
        ax.annotate(str(n), (a, b), textcoords='offset points', xytext=(5, -10), fontsize=7, color=c)
ax.plot([0, 1], [0, 1], ':', color='grey', label='perfect calibration')
ax.set_xlabel('crowd probability before close'); ax.set_ylabel('share that resolved YES')
ax.set_title('Manifold escalation markets: calibration\n(bins with ≥5 markets; numbers = markets per bin)', fontsize=10)
ax.legend(frameon=False); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
fig.tight_layout(); fig.savefig('calibration.png')
p('\nrandom escalation titles (rule check):')
for r in random.sample([r for r in ALL if r['grp']=='escalation'], min(20, sum(r['grp']=='escalation' for r in ALL))):
    p('  ', r['res'], r['q'][:110])
open('result.txt', 'w').write('\n'.join(out) + '\n')
