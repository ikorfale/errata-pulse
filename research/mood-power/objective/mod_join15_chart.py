"""Chart for #385: per region (n >= 15 in Chronicles wave 15), MoD-claimed drone days 26.03-21.10.2025 vs (left) the share
reporting local 'shelling, drone attacks' and (right) the share anxious. Frontline five marked. Reads mod_join15.out.
Usage: python3 mod_join15_chart.py -> mod_join15_chart.png"""
import re, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows = []
for l in open('mod_join15.out'):
    m = re.match(r'\s+(\d+)\s+(.+?)\s+n=\s*(\d+)\s+drone item ([\d.]+)\s+anxious ([\d.]+)', l)
    if m: rows.append((m.group(2), int(m.group(3)), float(m.group(4)), float(m.group(5))))
days = {}
for l in open('mod_regions_2025.out'):
    m = re.match(r'\s*(\d+)\s+(\d+)d\s+(.+)$', l)
    if m: days[m.group(3).strip()] = int(m.group(2))
import importlib.util, os
spec = importlib.util.spec_from_file_location('mj', 'mod_join15.py'); src = open('mod_join15.py').read()
mod_key = {'re': re}; exec(src[src.index('def mod_key'):src.index('xr = {')], mod_key); mk = mod_key['mod_key']
fold = {'Московской': 'Московского региона', 'Ростовская': 'Ростовской'}
D = {}
for k, v in days.items(): kk = fold.get(k, k); D[kk] = max(D.get(kk, 0), v)
FRONT = {'Белгородская область', 'Брянская область', 'Курская область', 'Крым', 'Севастополь'}
INK, MUTED, SURF, BLUE, ORANGE = '#0b0b0b', '#52514e', '#fcfcfb', '#2a78d6', '#eb6834'
fig, axs = plt.subplots(1, 2, figsize=(11, 4.8), sharex=True, facecolor=SURF)
for ax, j, lab in ((axs[0], 2, 'share reporting local "shelling, drone attacks"'), (axs[1], 3, 'share anxious (Q30)')):
    ax.set_facecolor(SURF)
    for nm, n, s, a in rows:
        x = D.get(mk(nm), 0); v = (s, a)[j - 2]; fr = nm in FRONT
        ax.scatter(x, v, s=max(n, 15) * 1.6, color=ORANGE if fr else BLUE, alpha=.8, edgecolor=SURF, linewidth=1.5, zorder=3)
        if fr or n >= 100: ax.annotate({'Белгородская область': 'Belgorod', 'Крым': 'Crimea', 'Москва': 'Moscow', 'Московская область': 'Moscow obl.'}.get(nm, nm), (x, v), xytext=(5, -11 if nm == 'Московская область' and j == 2 else 4), textcoords='offset points', fontsize=8, color=MUTED)
    ax.set_ylim(-0.03, 1.03); ax.set_xlim(-8, 200); ax.set_title(lab, fontsize=10, color=INK, loc='left'); ax.grid(axis='y', color='#e6e5e1', lw=.8)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.tick_params(colors=MUTED); ax.set_xlabel('days with MoD-claimed drones over the region, 26 Mar - 21 Oct 2025', fontsize=8.5, color=MUTED)
from matplotlib.lines import Line2D
axs[0].legend(handles=[Line2D([], [], marker='o', ls='', color=BLUE, label='region (size = respondents)'), Line2D([], [], marker='o', ls='', color=ORANGE, label='frontline')], frameon=False, fontsize=8, loc='lower right')
fig.suptitle('Russians report drones where the MoD says drones fly. Anxiety shows no detectable link to the count.', fontsize=11.5, color=INK, x=0.01, ha='left')
fig.text(0.01, 0.01, 'Chronicles wave 15 (fieldwork 26.09-21.10.2025), 35 regions with n >= 15; Russian MoD Telegram bulletins. Region codes inferred from wave 9. errata.page / github.com/ikorfale/errata-pulse', fontsize=7, color=MUTED)
fig.subplots_adjust(top=0.84, bottom=0.17, left=0.05, right=0.99, wspace=0.12)
fig.savefig('mod_join15_chart.png', dpi=130, facecolor=SURF)
