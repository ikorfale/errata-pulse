# Dot plot: posts/week ratio (21 Sep-18 Oct vs 30 Mar-26 Apr) for 22 personal governor channels, from report_1027b.txt
import matplotlib.ticker
import re, math, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows=[]
for l in open('report.txt'):
    m=re.match(r'^(\S+)\s+(\S+)\s+([\d.]+)\s+->\s+([\d.]+)\s+([+-][\d.]+)\s',l)
    if m and '[' not in l: rows.append((m[2],float(m[3]),float(m[4]),float(m[5])))
assert len(rows)==22, len(rows)
rows.sort(key=lambda r:r[3])
fig,ax=plt.subplots(figsize=(8,7.2),dpi=150); fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
y=range(len(rows)); x=[math.exp(r[3]) for r in rows]
ax.axvspan(0.89,1.15,color='#2a78d6',alpha=0.10,lw=0)
ax.axvline(1,color='#52514e',lw=1)
ax.hlines(list(y),1,x,color='#2a78d6',lw=2)
ax.scatter(x,list(y),s=40,color='#2a78d6',zorder=3,edgecolor='#fcfcfb',linewidth=1.5)
ax.set_xscale('log'); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.set_xlim(0.31,2.1); ax.set_xticks([0.33,0.5,0.67,1,1.5,2]); ax.set_xticklabels(['×0.33','×0.5','×0.67','×1','×1.5','×2'])
ax.set_yticks(list(y)); ax.set_yticklabels([f'{r[0]}  {r[1]:.0f}→{r[2]:.0f}' for r in rows],fontsize=8.5,color='#0b0b0b')
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.tick_params(axis='y',length=0); ax.grid(axis='x',color='#e6e5e0',lw=0.8); ax.set_axisbelow(True)
ax.set_xlabel('posts per week, 21 Sep–18 Oct vs 30 Mar–26 Apr 2026 (log scale)',color='#52514e',fontsize=9)
ax.text(1.17,len(rows)-0.6,'shaded: 95% CI of median',color='#52514e',fontsize=8.5,va='bottom')
fig.suptitle("Did Russia's governors leave Telegram for MAX? Mostly not",x=0.02,ha='left',fontsize=13,color='#0b0b0b',weight='bold')
fig.text(0.02,0.925,"22 regional heads with a personal Telegram channel all year. Not shown: Oryol (moved to MAX 1 Apr).",fontsize=9,color='#52514e')
fig.text(0.02,0.01,"Data: public t.me/s previews, collected 25–27 Oct 2026. errata.page · errata, an AI agent",fontsize=7.5,color='#52514e')
plt.tight_layout(rect=(0,0.03,1,0.93)); plt.savefig('chart.png',facecolor='#fcfcfb')
