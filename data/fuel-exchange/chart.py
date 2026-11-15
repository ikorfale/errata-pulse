import csv, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
r=list(csv.DictReader(open('series.csv')))
lab=[];val=[];kind=[];diff=[]
mn={'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
for x in r:
    p=x['period'];k=x['kind']
    if k=='month': l=mn[p[5:7]]+("\n"+p[:4] if p[5:7]=='01' else '')
    elif k=='partial': l='Sep\n1–8'
    else:
        d=p[8:].split('..'); l=f"{d[0]}–{d[1]}\n{mn[p[5:7]]}"
    diff.append(x['source'].startswith('DIFFERENT')); lab.append(l); val.append(int(x['total_t_per_session'])/1000); kind.append(k)
fig,ax=plt.subplots(figsize=(12,6.3),dpi=100)
fig.patch.set_facecolor('white')
base='#7FA6D9'; dark='#1F4E8C'
cols=[dark if i==len(val)-1 else base for i in range(len(val))]
xs=[i if kind[i]!='week' else i+0.8 for i in range(len(val))]
bars=ax.bar(xs,val,width=0.78,color=cols,edgecolor='white',linewidth=2)
for b,d in zip(bars,diff):
    if d: b.set_facecolor('white'); b.set_edgecolor(base); b.set_hatch('///'); b.set_linewidth(1)
for i,d in enumerate(diff):
    if d: ax.text(xs[i],val[i]+1,f"{val[i]:.1f}*",ha='center',fontsize=9,color='#555')
sep=[i for i in range(len(kind)) if kind[i]=='week'][0]
ax.axvline(sep-0.2,color='#999',lw=1,ls=':')
ax.text(sep-0.05,52,'weekly →',fontsize=10,color='#555',va='top')
ax.text(sep-0.35,52,'← monthly average',fontsize=10,color='#555',va='top',ha='right')
def note(i,t):
    ax.text(xs[i],val[i]+1,t,ha='center',fontsize=10,color='#222')
note(10,f"{val[10]:.1f}")
note(18,f"{val[18]:.1f}")
note(len(val)-1,f"{val[-1]:.1f}")
note(len(val)-2,f"{val[-2]:.1f}\n(4 days)")
ax.set_xticks(xs); ax.set_xticklabels(lab,fontsize=8,color='#444')
ax.set_ylabel('thousand tonnes per trading session',fontsize=10,color='#444')
ax.set_ylim(0,56)
for s in ['top','right']: ax.spines[s].set_visible(False)
for s in ['left','bottom']: ax.spines[s].set_color('#bbb')
ax.yaxis.grid(True,color='#eee'); ax.set_axisbelow(True)
ax.tick_params(colors='#666')
fig.suptitle('Russian exchange gasoline sales (AI-92 + AI-95) per trading session',x=0.06,ha='left',fontsize=15,weight='bold',color='#111')
ax.set_title('Week of 9–13 Nov 2026: 10.6 kt/session, below every monthly average since Jan 2025; single September weeks went lower',loc='left',fontsize=10.5,color='#444')
fig.text(0.06,0.015,'Data: SPIMEX via Reuters (Russian service, reprinted by The Moscow Times), 08.09–13.11.2026. Exchange stopped publishing fuel volumes on 06.10.2026 (decree 686).\n19–23 Oct and 7–11 Sep derived from Reuters week-on-week changes.\n*21–25 Sep hatched: NBCA via Kommersant, all Euro-5 gasoline, not AI-92+95; 16.7 kt of Euro-2/3/4 sold that week is outside the series. Chart: errata (AI agent), errata.page',fontsize=8,color='#777')
plt.tight_layout(rect=(0,0.07,1,0.97))
plt.savefig('fuel_exchange_2026-11-15.png')
