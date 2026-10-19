"""Chart: share of posts anchored >300 km from Ukraine's border, alerts (radarrussiia sample) vs strike reports
(Exilenova+), same days 8-14 of each month."""
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = json.load(open('exilenova/depth_monthly.json')); ms = sorted(d); x = range(len(ms))
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
lo = [d[m]['gt300'] - d[m]['band300'][0] for m in ms]; hi = [d[m]['band300'][1] - d[m]['gt300'] for m in ms]
ax.errorbar(x, [d[m]['gt300'] for m in ms], yerr=[lo, hi], fmt='o-', color='#b5452f', capsize=3, lw=1.5, label='strike reports (Exilenova+), 95% band over days')
ax.plot(x, [d[m]['alert_gt300'] for m in ms], 's-', color='#2f5fb5', lw=1.5, label='drone alerts (alert channel sample)')
ax.set_xticks(list(x)); ax.set_xticklabels([m[2:] for m in ms], fontsize=8)
ax.set_ylim(0, 1); ax.set_ylabel('share beyond 300 km'); ax.grid(alpha=.25)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.set_title('How deep: alerts vs strike reports, days 8-14 of each month', fontsize=11, loc='left')
for i, m in enumerate(ms): ax.annotate(str(d[m]['n']), (i, 0.02), ha='center', fontsize=7, color='#666')
ax.text(0, 0.07, 'n strike posts:', fontsize=7, color='#666')
ax.legend(fontsize=8, frameon=False, loc='upper left'); fig.tight_layout(); fig.savefig('exilenova/depth_vs_alerts.png')
