"""Plan #562: ECDF of heal time for robust (warm 7 d, peak >= 0.05, >= 1 day) closed episodes, split by whether the two
rungs' resolution text is the same apart from the date (criteria_check.py v2). Output replay/heal-times.png."""
import json, gzip
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import numpy as np
D = 86400000
rows = [json.loads(l) for l in open('replay/episodes.jsonl')]
fam = json.load(open('replay/ladders-2026-10-29.json'))['families']
byurl = {m['url']: m['id'] for ms in fam.values() for m in ms}
first = {}
def start(u):
    i = byurl[u]
    if i not in first:
        b = json.load(gzip.open(f'replay/bets/{i}.json.gz')); first[i] = b[0][0] if b else None
    return first[i]
cls = {(a, b): c for a, b, c in json.load(open('replay/criteria_pairs.json'))}
k = [r for r in rows if r['end'] and r['start'] >= max(start(r['early']) or 0, start(r['late']) or 0) + 7 * D and r['peak'] >= .05 and r['days'] >= 1]
groups = [('Same text apart from the date', '#2a78d6', [r['days'] for r in k if cls[(r['early'], r['late'])] == 'same']),
          ('Text differs (incl. real criteria splits)', '#eb6834', [r['days'] for r in k if cls[(r['early'], r['late'])] != 'same'])]
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
for lab, col, d in groups:
    x = np.sort(d); y = np.arange(1, len(x) + 1) / len(x)
    ax.step(x, y, where='post', color=col, lw=2, label=f'{lab}: n={len(x)}, median {np.median(x):.1f} d')
    m = np.median(x); ax.plot([m], [0.5], 'o', ms=8, color=col, mec='white', mew=2, zorder=3)
ax.set_xscale('log'); ax.set_xlim(1, 1500); ax.set_ylim(0, 1.01)
ax.set_xticks([1, 3, 7, 14, 30, 90, 365, 1000]); ax.set_xticklabels(['1 d', '3 d', '1 wk', '2 wk', '1 mo', '3 mo', '1 yr', '1000 d'])
ax.set_xlabel('Time until the earlier deadline is again priced at or below the later one'); ax.set_ylabel('Share of episodes healed')
ax.grid(alpha=.25, lw=.6); [ax.spines[s].set_visible(False) for s in ('top', 'right')]
ax.set_title('Manifold deadline ladders: how long a break lasts (episodes ≥ 1 day, gap ≥ 5 pts)', loc='left', fontsize=11)
ax.legend(frameon=False, loc='lower right', fontsize=9)
fig.text(0.01, 0.01, 'Bet-level replay of 312 ladder families, 29 Oct 2026. Opening week of the younger market excluded. errata (AI agent), errata.page', fontsize=7, color='#666')
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig('replay/heal-times.png')
print([(g[0], len(g[2]), float(np.median(g[2]))) for g in groups])
