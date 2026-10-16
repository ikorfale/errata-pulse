"""Calibration of resolved Manifold war/geopolitics markets from markets.json (see PREREG.md).

Rows, in order: the pre-registered test as written (v1 grouping, T-30d before close, market bootstrap),
then the robustness rows from the method review (v2 grouping, liquidity filter, cluster bootstrap,
creation-anchored horizons)."""
import json, re, random, sys
from collections import defaultdict
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

src = sys.argv[1] if len(sys.argv) > 1 else 'markets.json'
rows = json.load(open(src))
out = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s); out.append(s)

# v1 rule, as pre-registered (end/deal as word-start matches: recorded deviation)
ESC = re.compile(r'attack|strike|invade|invasion|nuclear|declare war|mobili[sz]|missile|bomb|troops|clash|shoot down|assassinat|coup|blockade|war with|war between|war against', re.I)
PEACE1 = re.compile(r'\bend|ceasefire|cease-fire|peace|truce|\bdeal|agreement|negotiat|talks', re.I)
# v2 additions
DATED = re.compile(r'\b(by|before|until|at|in)\s+(the\s+)?(end|start|beginning)\s+of\s+\S+', re.I)
PEACE2 = re.compile(r'ceasefire|cease-fire|peace|truce|armistice|\bend\b.*\b(war|conflict|fighting|invasion)', re.I)
OFF = re.compile(r'nuclear (power|plant|energy|fusion|reactor)|fusion|heart attack|cyber ?attack|shark|box.office|clash of clans|trade war|star wars|culture war|console war|strike(s)? (by|at) .*(union|workers)|(union|workers|writers|actors|teachers|auto).{0,20}strike|hunger strike|strikeout|bowling|chess|bitcoin|crypto|elon|twitter|bomb(ed)? at the box|photobomb|bath ?bomb', re.I)
FLIP = re.compile(r'withdraw|pull out|retreat|halt|\bstop|suspend|collapse|hold\b|resume', re.I)

def grp1(q):
    return 'peace' if PEACE1.search(q) else ('escalation' if ESC.search(q) else 'other')
def grp2(q):
    if OFF.search(q):
        return 'offtopic'
    t = DATED.sub(' ', q)
    if PEACE2.search(t):
        return 'peace'
    if ESC.search(t):
        return 'escalation?' if FLIP.search(t) else 'escalation'
    return 'other'

STOP = {'Will', 'The', 'A', 'In', 'By', 'Before', 'Of', 'On', 'At', 'And', 'Or', 'To', 'Be', 'Is', 'Does', 'Do', 'If', 'What', 'Which', 'Who', 'How'}
MONTHS = re.compile(r'January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|Q[1-4]')
def cluster(r):
    toks = sorted({w for w in re.findall(r"\b[A-Z][\w'-]+", r['q']) if w not in STOP and not MONTHS.fullmatch(w)})
    qtr = (r['close'] // (86400000 * 91))
    return ' '.join(toks) + f'|{qtr}'

for r in rows:
    r['g1'], r['g2'], r['cl'] = grp1(r['q']), grp2(r['q']), cluster(r)

def stats(R, h, boot='market', label=''):
    x = np.array([r[h] for r in R]); y = np.array([r['res'] == 'YES' for r in R], float)
    gap = x.mean() - y.mean()
    rng = np.random.default_rng(7)
    if boot == 'cluster':
        by = defaultdict(list)
        for i, r in enumerate(R):
            by[r['cl']].append(i)
        groups = list(by.values())
        bs = []
        for _ in range(2000):
            idx = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
            bs.append(x[idx].mean() - y[idx].mean())
        neff = len(groups)
    else:
        bs = [(lambda i: x[i].mean() - y[i].mean())(rng.integers(0, len(R), len(R))) for _ in range(2000)]
        neff = len(R)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    brier = ((x - y) ** 2).mean(); base = ((y.mean() - y) ** 2).mean() or float('nan')
    p(f'{label:<44} n={len(R):4d} eff={neff:4d}  crowd {x.mean():.3f}  YES {y.mean():.3f}  gap {gap:+.3f} [{lo:+.3f},{hi:+.3f}]  '
      f'Brier {brier:.3f} vs const {base:.3f}')
    return x, y

def liquid(r, h):
    return (r.get(h + '_n') or 0) >= 10 and (r.get(h + '_users') or 0) >= 5

p(f'source {src}: {len(rows)} markets, YES {sum(r["res"] == "YES" for r in rows)}')
p('groups v1:', dict(sorted(defaultdict(int, {g: sum(r['g1'] == g for r in rows) for g in {r['g1'] for r in rows}}).items())))
p('groups v2:', dict(sorted({g: sum(r['g2'] == g for r in rows) for g in {r['g2'] for r in rows}}.items())))
p('\n# PRE-REGISTERED TEST: v1 escalation, T-30d before close, market bootstrap; prediction gap >= +0.05')
R = [r for r in rows if r['g1'] == 'escalation' and r.get('30d') is not None]
stats(R, '30d', label='v1 escalation T-30d')
p('\n# Context and robustness')
for h in ('30d', '7d', 'c14', 'c30'):
    for g in ('escalation', 'peace', 'other'):
        R = [r for r in rows if r['g2'] == g and r.get(h) is not None]
        if len(R) >= 10:
            stats(R, h, 'cluster', f'v2 {g} {h} cluster-boot')
        RL = [r for r in R if liquid(r, h)]
        if len(RL) >= 10:
            stats(RL, h, 'cluster', f'v2 {g} {h} liquid cluster-boot')
    if h.startswith('c'):
        R = [r for r in rows if r['g2'] == 'escalation' and r.get(h) is not None and r['close'] > r['created'] + int(h[1:]) * 86400000]
        if len(R) >= 10:
            stats(R, h, 'cluster', f'v2 escalation {h} open-at-anchor only')
R = [r for r in rows if r['g2'] == 'escalation' and r.get('30d') is not None]
if R:
    p('\n# one random market per cluster, v2 escalation T-30d')
    random.seed(3); pick = {}
    for r in random.sample(R, len(R)):
        pick.setdefault(r['cl'], r)
    stats(list(pick.values()), '30d', label='v2 escalation T-30d one-per-cluster')
    p('\n# liquidity terciles (bettors before anchor), v2 escalation T-30d')
    R2 = sorted(R, key=lambda r: r.get('30d_users') or 0)
    for k in range(3):
        part = R2[k * len(R2) // 3:(k + 1) * len(R2) // 3]
        if len(part) >= 10:
            stats(part, '30d', label=f'tercile {k + 1} (users {part[0].get("30d_users")}..{part[-1].get("30d_users")})')
    p('\n# 25 random v2 escalation titles for a hand check of direction (YES = more violence?)')
    random.seed(5)
    for r in random.sample(R, min(25, len(R))):
        p('  ', r['res'], f"{r['30d']:.2f}", r['q'][:120])

fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150)
BINS = np.linspace(0, 1.0001, 11)
for h, c, lab in (('30d', '#c0392b', '30 days before close'), ('c14', '#2c3e50', '14 days after creation')):
    R = [r for r in rows if r['g2'] == 'escalation' and r.get(h) is not None and liquid(r, h)]
    if not R:
        continue
    x = np.array([r[h] for r in R]); y = np.array([r['res'] == 'YES' for r in R], float)
    xs, ys, ns = [], [], []
    for a, b in zip(BINS[:-1], BINS[1:]):
        m = (x >= a) & (x < b)
        if m.sum() >= 5:
            xs.append(x[m].mean()); ys.append(y[m].mean()); ns.append(int(m.sum()))
    ax.plot(xs, ys, 'o-', color=c, label=f'{lab} (n={len(R)})')
    for a, b, n in zip(xs, ys, ns):
        ax.annotate(str(n), (a, b), textcoords='offset points', xytext=(5, -10), fontsize=7, color=c)
ax.plot([0, 1], [0, 1], ':', color='grey', label='perfect calibration')
ax.set_xlabel('crowd probability'); ax.set_ylabel('share that resolved YES')
ax.set_title('Manifold escalation markets (≥10 bets, ≥5 bettors before the anchor)\nnumbers = markets per bin; bins with ≥5 markets', fontsize=9)
ax.legend(frameon=False, fontsize=8); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
fig.tight_layout(); fig.savefig('calibration.png')
open('result.txt', 'w').write('\n'.join(out) + '\n')
