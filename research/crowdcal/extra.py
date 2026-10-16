"""Post-hoc (not pre-registered) checks after analyse.py: escalation vs other gap difference,
where the gap comes from (price bins), and a gap-by-anchor chart for the three groups."""
import re
src_text = open('analyse.py').read()
exec(src_text[:src_text.index("p(f'source")])
import matplotlib.pyplot as plt
out.clear()
H = ('7d', '30d', 'c30', 'c14')
HL = {'7d': '7 days before close', '30d': '30 days before close', 'c30': '30 days after creation', 'c14': '14 days after creation'}
G = ('escalation', 'peace', 'other')
rng = np.random.default_rng(11)
def boot_gap(R, h, B=2000):
    by = defaultdict(list)
    for r in R: by[r['cl']].append(r[h] - (r['res'] == 'YES'))
    gs = list(by.values()); sums = np.array([sum(g) for g in gs]); ns = np.array([len(g) for g in gs])
    k = rng.integers(0, len(gs), (B, len(gs)))
    return sums[k].sum(1) / ns[k].sum(1), sums.sum() / ns.sum()
res = {}
for h in H:
    for g in G:
        R = [r for r in rows if r['g2'] == g and r.get(h) is not None]
        bs, gap = boot_gap(R, h); res[g, h] = (gap, *np.percentile(bs, [2.5, 97.5]), len(R), bs)
p('# escalation minus other, cluster bootstrap within each group (post hoc)')
for h in H:
    d = res['escalation', h][4] - res['other', h][4]
    p(f'{h:4s} esc {res["escalation", h][0]:+.3f}  other {res["other", h][0]:+.3f}  diff {res["escalation", h][0] - res["other", h][0]:+.3f} [{np.percentile(d, 2.5):+.3f},{np.percentile(d, 97.5):+.3f}]')
p('\n# where the escalation T-30d gap comes from: price bins (sum of crowd-YES over all markets / n)')
R = [r for r in rows if r['g2'] == 'escalation' and r.get('30d') is not None]
tot = sum(r['30d'] - (r['res'] == 'YES') for r in R)
for a, b in ((0, .1), (.1, .3), (.3, .7), (.7, 1.01)):
    S = [r for r in R if a <= r['30d'] < b]
    c = sum(r['30d'] - (r['res'] == 'YES') for r in S)
    p(f'price [{a:.1f},{b:.1f})  n={len(S):4d}  mean price {np.mean([r["30d"] for r in S]):.3f}  YES {np.mean([r["res"] == "YES" for r in S]):.3f}  share of total gap {c / tot:.2f}')
open('extra.txt', 'w').write('\n'.join(out) + '\n')

COL = {'escalation': '#e34948', 'peace': '#2a78d6', 'other': '#52514e'}
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
for j, g in enumerate(G):
    for i, h in enumerate(H):
        gap, lo, hi, n, _ = res[g, h]
        y = i + (j - 1) * 0.22
        ax.plot([lo * 100, hi * 100], [y, y], color=COL[g], lw=2, solid_capstyle='round')
        ax.plot(gap * 100, y, 'o', ms=8, color=COL[g], mec='#fcfcfb', mew=2, label=g if i == 0 else None)
ax.axvline(0, color='#0b0b0b', lw=1)
ax.axvline(5, color='#52514e', lw=1, ls=':')
ax.text(5.3, -0.62, 'my pre-registered threshold (+5)', fontsize=7, color='#52514e', va='center')
ax.set_yticks(range(len(H)), [HL[h] for h in H], fontsize=8)
ax.set_xlabel('crowd price minus share resolved YES, percentage points (95% cluster bootstrap)', fontsize=8)
ax.set_title('Manifold war & geopolitics markets (2,812 resolved): YES is overpriced early,\nfor every kind of question, and the gap is gone a week before close', fontsize=9, loc='left')
for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
ax.tick_params(axis='y', length=0); ax.grid(axis='x', color='#e6e5e0', lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8, loc='lower right', title='question type', title_fontsize=7)
ax.set_facecolor('#fcfcfb'); fig.patch.set_facecolor('#fcfcfb')
fig.tight_layout(); fig.savefig('gap_by_anchor.png')
