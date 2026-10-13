"""Map + monthly chart of merchant-ship strikes in the Black Sea from ledger.jsonl (errata, 13 Oct 2026).
Group: NATO EEZ (BG/RO/TR), Ukrainian ports/coast, Russian ports/coast, other/unknown. Points without coordinates
are counted in the chart but not drawn on the map (the map title says how many)."""
import json, collections
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = [r for r in (json.loads(l) for l in open('ledger.jsonl') if l.strip()) if not r.get('aggregate')]
def group(z):
    if z in ('BG-EEZ', 'RO-EEZ', 'TR-EEZ'): return 'NATO EEZ (BG/RO/TR)'
    if z.startswith('UA'): return 'Ukraine ports/coast'
    if z.startswith('RU'): return 'Russia ports/coast'
    return 'other / unknown'
G = ['NATO EEZ (BG/RO/TR)', 'Ukraine ports/coast', 'Russia ports/coast', 'other / unknown']
C = dict(zip(G, ['#2a78d6', '#eb6834', '#1baf7a', '#9a9a94'])); M = dict(zip(G, 'o^sD'))
INK, MUTED, GRID = '#1f1f1d', '#6b6b66', '#e4e4df'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': INK, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.edgecolor': GRID})

fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={'width_ratios': [1.45, 1]})
for run in json.load(open('coast_bs.json')):
    xs, ys = zip(*run); ax.plot(xs, ys, color='#8a8a84', lw=0.8)
drawn = 0
for g in G:
    pts = [r for r in R if group(r['zone']) == g and r.get('lat') is not None]
    drawn += len(pts)
    if pts:
        ax.scatter([r['lon'] for r in pts], [r['lat'] for r in pts], s=[90 if r.get('sunk') else 45 for r in pts],
                   c=C[g], marker=M[g], edgecolors='white', linewidths=1.2, label=g, zorder=3)
for r in R:
    if r['date_event'] >= '2026-10-01' and r.get('lat') is not None and group(r['zone']).startswith('NATO'):
        ax.annotate(r['date_event'][5:], (r['lon'], r['lat']), xytext=(5, 4), textcoords='offset points', fontsize=8, color=INK)
ax.set_xlim(27.3, 42); ax.set_ylim(40.7, 47.4); ax.set_aspect(1.35)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title('Merchant ships hit in the Black Sea, 1 Jun - 13 Oct 2026', fontsize=11.5, loc='left', pad=18)
ax.text(0, 1.015, f'{drawn} of {len(R)} named incidents placed; large marker = sunk; port-area positions approximate', transform=ax.transAxes, fontsize=8.5, color=MUTED)
ax.legend(loc='lower left', frameon=False, fontsize=8.5)

months = ['2026-06', '2026-07', '2026-08', '2026-09', '2026-10']
cnt = collections.Counter((r['date_event'][:7], group(r['zone'])) for r in R)
bottom = [0] * len(months)
for g in G:
    v = [cnt[(m, g)] for m in months]
    bx.bar(range(len(months)), v, bottom=bottom, color=C[g], width=0.62, edgecolor='white', linewidth=2, label=g)
    bottom = [b + x for b, x in zip(bottom, v)]
for i, b in enumerate(bottom): bx.text(i, b + 0.2, str(b), ha='center', fontsize=9, color=INK)
bx.set_ylim(0, max(bottom) * 1.15 + 0.5); bx.yaxis.get_major_locator().set_params(integer=True)
bx.set_xticks(range(len(months))); bx.set_xticklabels(['Jun', 'Jul', 'Aug', 'Sep', 'Oct\n(1-13)'])
bx.spines[['top', 'right']].set_visible(False); bx.yaxis.grid(color=GRID); bx.set_axisbelow(True)
bx.set_title('Named incidents per month, by where the ship was hit', fontsize=11.5, loc='left', pad=18)
bx.text(0, 1.015, 'colours as on the map; grey = location not reported', transform=bx.transAxes, fontsize=8.5, color=MUTED)
fig.text(0.01, 0.008, '\n'.join([
    'Data: errata ledger from press reports (Reuters, AP, BTA and others), 2 sources per incident where available. Attribution not shown: most strikes are unclaimed.',
    'Not shown: Ukraine claims ~300 unnamed vessels hit near Russian coasts and in the Sea of Azov since July, so the Russian side is undercounted.',
    'NATO-EEZ strikes are reported by Romania and Bulgaria and are likely complete.  errata.page']), fontsize=7.5, color=MUTED, linespacing=1.4)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig('blacksea_strikes.png', dpi=130)
print('drawn', drawn, 'of', len(R)); print({m: {g: cnt[(m, g)] for g in G if cnt[(m, g)]} for m in months})
