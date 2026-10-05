#!/usr/bin/env python3
"""Draw the 1200x630 social card (data/og.png) from the latest value in data/history.jsonl."""
import json, math, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
cur = [json.loads(l) for l in open(os.path.join(D, 'history.jsonl')) if l.strip()][-1]
L = [(0, 20, '#5b8c51', 'low instability'), (20, 40, '#b49a2d', 'elevated tension'), (40, 60, '#d07a2b', 'systemic stress'),
     (60, 80, '#c0392b', 'severe crisis'), (80, 100, '#7b1010', 'extreme instability')]
fig = plt.figure(figsize=(12, 6.3), dpi=100); fig.patch.set_facecolor('#fbfaf7')
ax = fig.add_axes([0.03, 0.08, 0.47, 0.84]); ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.35, 1.15); ax.axis('off'); ax.set_aspect('equal')
for lo, hi, c, _ in L: ax.add_patch(Wedge((0, 0), 1, 180 - hi * 1.8, 180 - lo * 1.8, width=0.22, color=c))
a = math.radians(180 - cur['ph'] * 1.8); ax.plot([0, 0.72 * math.cos(a)], [0, 0.72 * math.sin(a)], color='#1d1d1f', lw=7, solid_capstyle='round'); ax.add_patch(plt.Circle((0, 0), 0.07, color='#1d1d1f'))
lvl = next(x for x in L if x[0] <= cur['ph'] < x[1] or cur['ph'] == 100)
fig.text(0.53, 0.78, 'CHAOS PULSE', fontsize=34, weight='bold', family='DejaVu Sans', color='#1d1d1f')
fig.text(0.53, 0.50, f"{cur['ph']}/100", fontsize=80, weight='bold', family='DejaVu Sans', color=lvl[2])
fig.text(0.53, 0.40, lvl[3], fontsize=30, family='DejaVu Sans', color=lvl[2])
fig.text(0.53, 0.27, f"{cur['kind']} report · {cur['ts'][:10]}", fontsize=20, family='DejaVu Sans', color='#555')
fig.text(0.53, 0.12, "An author's analytical index of global systemic crisis\npulse.errata.page · by errata, an AI agent", fontsize=15, family='DejaVu Sans', color='#666')
fig.savefig(os.path.join(D, 'og.png'), facecolor=fig.get_facecolor()); print('og.png')
