"""chart.py: closed vs open ladder breaks per hand-reviewed ladder market, from backhist.json (3-point episodes)."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('backhist.json'))
NAMES = {'russian-attacks-or-invades-finland': 'Russia attacks Finland',
         'when-will-pete-buttigieg': 'Buttigieg 2028 run', 'by-when-will-the-boom-overture': 'Boom Overture flight',
         'when-will-josh-shapiro': 'Shapiro 2028 run', 'when-will-the-worlds-total-fertilit': 'World fertility below replacement',
         'will-donald-trump-carry-out-an-inva': 'US invades Greenland', 'will-china-invade-taiwan': 'China invades Taiwan'}
def name(url):
    for k, v in NAMES.items():
        if k in url: return v
rows = {}
for p in d['pairs']:
    if p['verdict'] != 'ladder': continue
    r = rows.setdefault(name(p['url']), {'closed': {}, 'open': set()})
    for e in p['tol3']['closed']:
        # a break opened by one bet and seen by several pairs sharing a rung counts once, at its longest
        r['closed'][e['start']] = max(r['closed'].get(e['start'], 0), (e['end'] - e['start']) / 864e5, 1 / 1440)
    if p['tol3'].get('open'):
        r['open'].add(round(p['tol3']['open']['days'], 1))
order = sorted(rows, key=lambda k: max(rows[k]['open'] or {0}))
INK, MUTED, GRID, CLOSED, OPEN = '#1f2328', '#59636e', '#e6e8eb', '#8c959f', '#c2410c'
fig, ax = plt.subplots(figsize=(11, 5.6), dpi=120)
for i, k in enumerate(order):
    c = list(rows[k]['closed'].values())
    ax.scatter(c, [i] * len(c), s=46, facecolors='none', edgecolors=CLOSED, linewidths=1.4, zorder=3,
               label='break that closed (length)' if i == 0 else None)
    o = sorted(rows[k]['open'])
    ax.scatter(o, [i] * len(o), s=80, color=OPEN, edgecolors='white', linewidths=2, zorder=4,
               label='break still open on 16 Oct (age)' if i == 0 else None)
    ax.annotate(f"{max(o):g} d", (max(o), i), xytext=(9, 0), textcoords='offset points', va='center', fontsize=9, color=INK)
ax.set_xscale('log'); ax.set_xlim(1 / 1440 * 0.7, 600)
ax.set_xticks([1 / 1440, 1 / 24, 1, 7, 30, 365]); ax.set_xticklabels(['1 min', '1 hour', '1 day', '1 week', '1 month', '1 year'])
ax.set_yticks(range(len(order))); ax.set_yticklabels([f"{k}  ({len(rows[k]['closed'])} closed)" for k in order], fontsize=10, color=INK)
ax.axvline(1, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
ax.grid(axis='x', color=GRID, lw=1); ax.set_axisbelow(True)
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(GRID); ax.tick_params(colors=MUTED, length=0)
fig.text(0.01, 0.965, 'Manifold ladder breaks: past ones closed within a day, the ones open today are weeks old',
         fontsize=12.5, color=INK)
ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9.5, labelcolor=INK)
fig.text(0.01, 0.01, 'Break = earlier deadline priced >3 points above a later one, rebuilt bet by bet. 7 hand-reviewed markets, '
         'a stretch seen by several pairs sharing a rung counted once;\nbreaks under a minute drawn at 1 min. Data: Manifold API, 16 Oct 2026. errata.page', fontsize=8, color=MUTED)
fig.tight_layout(rect=(0, 0.05, 1, 0.94))
fig.savefig('ladder-breaks.png')
for k in order: print(k, len(rows[k]['closed']), sorted(rows[k]['open']))
