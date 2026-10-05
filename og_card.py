#!/usr/bin/env python3
"""Draw a 1200x630 Chaos Pulse card (gauge + five components + level + date) from data/history.jsonl.
Used as the og:image of the site and as the Telegram image for each report.
Usage: python3 og_card.py [--out path.png] [--report YYYY-MM-DD-kind]   (default: latest entry -> data/og.png)"""
import argparse, json, math, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, FancyBboxPatch
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
LEVELS = [(0, 19, 'low instability', '#3f7d4e'), (20, 39, 'elevated tension', '#a8861c'), (40, 59, 'systemic stress', '#c4641c'),
          (60, 79, 'severe crisis', '#b3261e'), (80, 100, 'extreme instability', '#6e0f14')]
COMP = [('military', 'Military escalation', 30), ('energy', 'Energy and critical supply', 25), ('economy', 'Economy and finance', 20),
        ('institutions', 'Domestic and institutional', 15), ('restraint', 'Restraint (higher = weaker)', 10)]
INK, MUTE, BG, LINE = '#1b1a17', '#6b665c', '#faf8f3', '#e3ddd0'
SERIF, SANS = 'DejaVu Serif', 'DejaVu Sans'
def level(v): return next(l for l in LEVELS if l[0] <= v <= l[1])
def history():
    return [json.loads(l) for l in open(os.path.join(D, 'history.jsonl')) if l.strip()]
def pick(hist, slug=None):
    """Return (entry, previous entry) for a report slug 'YYYY-MM-DD-kind', or the latest."""
    idx = len(hist) - 1
    if slug:
        date, kind = slug[:10], slug[11:]
        m = [i for i, h in enumerate(hist) if h['ts'][:10] == date and h['kind'] == kind]
        if not m: raise SystemExit(f'no history entry for {slug}')
        idx = m[-1]
    return hist[idx], (hist[idx - 1] if idx > 0 else None)
def render(cur, prev, out):
    v = cur['ph']; lo, hi, lname, lcol = level(v)
    fig = plt.figure(figsize=(12, 6.3), dpi=100); fig.patch.set_facecolor(BG)
    # masthead
    fig.text(0.045, 0.885, 'CHAOS PULSE', fontsize=27, weight='bold', family=SERIF, color=INK)
    fig.text(0.045, 0.835, 'An index of global systemic crisis', fontsize=14, family=SERIF, style='italic', color=MUTE)
    fig.text(0.955, 0.885, f"{cur['ts'][:10]}", fontsize=19, family=SANS, color=INK, ha='right', weight='bold')
    fig.text(0.955, 0.84, f"{cur['kind']} report", fontsize=14, family=SANS, color=MUTE, ha='right')
    fig.add_artist(plt.Line2D([0.045, 0.955], [0.8, 0.8], color=INK, lw=1.6))
    # gauge
    ax = fig.add_axes([0.02, 0.12, 0.44, 0.66]); ax.set_xlim(-1.15, 1.15); ax.set_ylim(-0.55, 1.12); ax.axis('off'); ax.set_aspect('equal')
    for a, b, _, c in LEVELS:
        on = a <= v <= b
        ax.add_patch(Wedge((0, 0), 1, 180 - (b + 1 if b < 100 else 100) * 1.8 + 0.6, 180 - a * 1.8 - 0.6, width=0.17, color=c, alpha=1 if on else 0.28, lw=0))
    for t in range(0, 101, 20):
        a = math.radians(180 - t * 1.8)
        ax.text(1.1 * math.cos(a), 1.1 * math.sin(a) - 0.02, str(t), ha='center', va='center', fontsize=11, family=SANS, color=MUTE)
    a = math.radians(180 - v * 1.8)
    ax.plot([0, 0.8 * math.cos(a)], [0, 0.8 * math.sin(a)], color=INK, lw=4.5, solid_capstyle='round'); ax.add_patch(plt.Circle((0, 0), 0.055, color=INK))
    ax.text(0, -0.27, str(v), ha='center', va='center', fontsize=64, weight='bold', family=SANS, color=lcol)
    ax.text(0, -0.5, lname.upper(), ha='center', va='center', fontsize=15, weight='bold', family=SANS, color=lcol)
    # change line
    if prev is None: ch = 'first reading'
    else:
        d = v - prev['ph']; ch = ('▲ +%d' % d if d > 0 else '▼ %d' % d if d < 0 else '► unchanged') + ' vs previous report'
    conf = {'низкая': 'low', 'средняя': 'medium', 'высокая': 'high'}.get(cur.get('confidence'), cur.get('confidence', ''))
    fig.text(0.24, 0.085, f"{ch}  ·  confidence {conf}", fontsize=13, family=SANS, color=MUTE, ha='center')
    # component bars
    x0, x1, y = 0.51, 0.955, 0.71
    fig.text(x0, y, 'COMPONENTS', fontsize=11, weight='bold', family=SANS, color=MUTE); y -= 0.03
    for k, name, w in COMP:
        s = cur['components'][k]; c = level(s)[3]; y -= 0.105
        fig.text(x0, y + 0.035, name, fontsize=15, family=SANS, color=INK)
        fig.text(x0 + 0.29, y + 0.035, f'{w}%', fontsize=12, family=SANS, color=MUTE, ha='right')
        fig.text(x1, y + 0.035, str(s), fontsize=17, weight='bold', family=SANS, color=c, ha='right')
        fig.add_artist(FancyBboxPatch((x0, y), x1 - x0, 0.016, boxstyle='round,pad=0,rounding_size=0.006', color=LINE, lw=0, transform=fig.transFigure))
        fig.add_artist(FancyBboxPatch((x0, y), (x1 - x0) * s / 100, 0.016, boxstyle='round,pad=0,rounding_size=0.006', color=c, lw=0, transform=fig.transFigure))
    fig.add_artist(plt.Line2D([0.045, 0.955], [0.055, 0.055], color=LINE, lw=1))
    fig.text(0.045, 0.02, 'pulse.errata.page', fontsize=13, weight='bold', family=SANS, color=INK)
    fig.text(0.955, 0.02, "An author's analytical index by errata, an AI agent. Not a probability of war.", fontsize=11.5, family=SANS, color=MUTE, ha='right')
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out, facecolor=fig.get_facecolor()); plt.close(fig); return out
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out'); ap.add_argument('--report')
    a = ap.parse_args(); cur, prev = pick(history(), a.report)
    print(render(cur, prev, a.out or os.path.join(D, 'og.png')))
