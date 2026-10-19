import json, math, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
r = json.load(open('result.json'))
def wilson(k, n, z=1.96):
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return c-h, c+h
names = list(r); lab = [n.split(' ',1)[0]+'  '+n.split(' ',1)[1] for n in names]
fig, ax = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True, gridspec_kw={'width_ratios': [1.3, 1]})
ink, mute, acc = '#1f2328', '#8a8f98', '#2a6fdb'
for i, n in enumerate(names):
    y = len(names)-1-i; col = acc if n.startswith(('R0', 'R2')) else mute
    k, N = r[n]['sens']; lo, hi = wilson(k, N)
    ax[0].plot([lo*100, hi*100], [y, y], color=col, lw=2, solid_capstyle='round'); ax[0].plot(k/N*100, y, 'o', ms=9, color=col, mec='white', mew=2)
    ax[0].text(hi*100+1.5, y, f'{k}/{N}', va='center', fontsize=9, color=ink)
    k, N = r[n]['quiet']; lo, hi = wilson(k, N)
    ax[1].plot([lo*100, hi*100], [y, y], color=col, lw=2, solid_capstyle='round'); ax[1].plot(k/N*100, y, 'o', ms=9, color=col, mec='white', mew=2)
    ax[1].text(hi*100+0.6, y, f'{k}/{N}', va='center', fontsize=9, color=ink)
ax[0].set_yticks(range(len(names))); ax[0].set_yticklabels(lab[::-1], fontsize=9, color=ink)
ax[0].set_xlim(0, 100); ax[1].set_xlim(0, 32)
ax[0].set_title('Catches a confirmed fire (sensitivity, 45 strikes)', fontsize=10.5, loc='left', color=ink)
ax[1].set_title('Flags a quiet window (false-alarm upper bound)', fontsize=10.5, loc='left', color=ink)
ax[1].axvline(5, color='#c0392b', lw=1, ls='--'); ax[1].text(5.4, 0.35, 'pre-registered\nlimit 5%', fontsize=8.5, color='#c0392b')
for a in ax:
    a.set_xlabel('%', color=mute); a.grid(axis='x', color='#e6e8eb', lw=0.8); a.set_axisbelow(True)
    for s in ('top', 'right', 'left'): a.spines[s].set_visible(False)
    a.tick_params(colors=mute, length=0)
fig.suptitle('Can NASA FIRMS see a refinery strike? Six rules, scored against officially confirmed fires', x=0.01, ha='left', fontsize=12.5, color=ink, weight='bold')
fig.text(0.01, 0.005, 'VIIRS active fires, 59 strikes on Russian oil sites 2025-26 (45 fire confirmed by governor/officials/industry sources). Dots = rate, bars = Wilson 95%. Rules fixed before scoring. errata.page', fontsize=8, color=mute)
fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig('sensitivity.png', dpi=130)
