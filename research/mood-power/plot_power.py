"""Chart for the power check: FOM weekly 'anxious' share 2021-2026 with the pre-listed shocks marked."""
import json, datetime as dt, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S = json.load(open('fom/archive.json'))['series']
D = [dt.date.fromisoformat(r['date']) for r in S]; A = [r['anxious'] for r in S]
from power_check import SHOCKS
fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
ax.plot(D, A, color='#2a5d9f', lw=2)
for s, kind, name in SHOCKS:
    d = dt.date.fromisoformat(s); i = next(j for j, x in enumerate(D) if x >= d + dt.timedelta(days=2))
    big = kind == 'big'
    ax.plot(D[i], A[i], 'o', ms=9 if big else 7, mfc='#c0392b' if big else 'white', mec='#c0392b', mew=2, zorder=3)
    lab = {'partial mobilisation': 'mobilisation', 'invasion of Ukraine': 'invasion', 'Prigozhin mutiny': 'mutiny',
           'Crocus City Hall attack': 'Crocus', 'Ukrainian incursion into Kursk': 'Kursk'}.get(name, name.split(',')[0].replace('drone attack on Moscow (first on residential Moscow)', 'Moscow drones').replace('largest drone raid on Moscow to date (337 drones claimed)', 'Moscow raid').replace('Belgorod city centre shelling', 'Belgorod'))
    off = {'mutiny': (22, -20), 'Moscow drones': (-30, 12)}.get(lab, (0, 12 if big else -18))
    ax.annotate(lab, (D[i], A[i]), xytext=off, textcoords='offset points', ha='center', fontsize=10, color='#333', bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.grid(axis='y', color='#ddd', lw=0.8); ax.set_ylim(20, 80); ax.set_ylabel('% saying "anxious"', color='#333')
ax.set_title('FOM weekly poll: is the mood around you calm or anxious? (n≈1,500)', loc='left', fontsize=14, color='#111')
ax.text(0, -0.12, 'Filled: national shocks. Open: single strikes on Russian cities. Week-to-week noise: sd 3.9 pts.\n'
        'Source: FOM "Dominanty", 244 weekly waves Oct 2021 – Oct 2026, parsed from the charts. errata.page', transform=ax.transAxes, fontsize=9, color='#666', va='top')
plt.tight_layout(); plt.savefig('fom_power_check.png'); print('ok')
