# Dot-and-whisker: age-adjusted gap in support (users minus non-users of a news source), Chronicles wave 13.
# Numbers copied from research/mood-power/chronicles13_media.out (age-adjusted, se).
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows = {'"Withdraw troops without\nachieving the goals"': [('Television',-9.5,4.8),('YouTube channels',13.8,4.5),('Telegram channels',-3.8,4.5)],
        '"Withdraw troops and start\nceasefire talks"':      [('Television',3.0,4.8),('YouTube channels',-0.3,4.5),('Telegram channels',-1.8,4.7)]}
ink,mut,blue='#1f2328','#6e7781','#2a5b9e'
fig,axs=plt.subplots(1,2,figsize=(12,6.3),sharey=True,dpi=100)
for ax,(title,rs) in zip(axs,rows.items()):
    for i,(lab,g,se) in enumerate(rs):
        y=2-i; ax.plot([g-1.96*se,g+1.96*se],[y,y],color=blue,lw=2,solid_capstyle='round')
        ax.plot(g,y,'o',ms=10,color=blue,mec='white',mew=2,zorder=3)
        ax.annotate(f'{g:+.1f}',(g,y),xytext=(0,12),textcoords='offset points',ha='center',color=ink,fontsize=12,bbox=dict(fc='white',ec='none',pad=1))
    ax.axvline(0,color=mut,lw=1); ax.set_ylim(-.5,2.6); ax.set_xlim(-25,28); ax.set_title(title,fontsize=13,color=ink,loc='left')
    ax.set_yticks([2,1,0]); ax.set_yticklabels([r[0] for r in rs],fontsize=12,color=ink)
    ax.grid(axis='x',color='#d8dee4',lw=.8); ax.set_axisbelow(True)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.tick_params(colors=mut); ax.set_xlabel('gap in support vs non-users, points (age-adjusted, 95% CI)',color=mut)
fig.suptitle('News source matters only when the question says "without achieving the goals"',x=.03,ha='left',fontsize=15,color=ink)
fig.text(.03,.015,'Chronicles wave 13, Sep 2024, about 500 respondents per wording; gap averaged within five age bands. Correlation, not a media effect.\nSource: Chronicles open microdata; analysis errata.page',fontsize=10,color=mut)
fig.tight_layout(rect=(0,.07,1,.94)); fig.savefig('russia-war-news-source-withdrawal-gap.png')
