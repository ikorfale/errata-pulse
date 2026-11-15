import csv, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows=[r for r in csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"series.csv"))) if r["kind"]=="week"]
lab={"2026-09-07..11":"7–11\nSep","2026-09-14..18":"14–18\nSep","2026-09-21..25":"21–25\nSep*",
     "2026-10-19..23":"19–23\nOct","2026-10-26..30":"26–30\nOct","2026-11-02..06":"2–6\nNov","2026-11-09..13":"9–13\nNov"}
x=[lab[r["period"]] for r in rows]; y=[float(r["total_t_per_session"])/1000 for r in rows]
ref=34.658  # Nov 2025 monthly average
INK="#1f2328"; MUTED="#6b7280"; BLUE="#3b6fb6"; DARK="#1d3f73"; GRID="#e5e7eb"
fig,(a,b)=plt.subplots(1,2,figsize=(12,5.2),gridspec_kw={"width_ratios":[1.35,1]})
for ax in (a,b):
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GRID); ax.spines["bottom"].set_color(GRID); ax.tick_params(colors=MUTED)
cols=[BLUE]*len(y); cols[-1]=DARK
bars=a.bar(range(len(y)),y,color=cols,width=0.7)
bars[2].set_hatch("///"); bars[2].set_facecolor("white"); bars[2].set_edgecolor(BLUE)
a.axhline(ref,color=MUTED,lw=1.2,ls="--"); a.text(len(y)-0.6,ref+0.8,"Nov 2025 average: 34.7",ha="right",color=MUTED,fontsize=9)
for i,v in enumerate(y): a.text(i,v+0.6,f"{v:.1f}",ha="center",fontsize=9,color=INK)
a.set_xticks(range(len(y))); a.set_xticklabels(x,fontsize=9); a.set_ylim(0,40)
a.yaxis.grid(True,color=GRID); a.set_axisbelow(True)
a.set_title("Exchange sales of AI-92 + AI-95,\nthousand tonnes per trading session",loc="left",fontsize=11,color=INK)
names=["Oil-company stations\n(OMT Consult)","National average\n(Rosstat, 9 Nov)","Independent stations\n(OMT Consult)"]
vals=[61.37,70.01,84.01]
b.barh(range(3),vals,color=[BLUE,MUTED,DARK],height=0.55)
for i,v in enumerate(vals): b.text(v+1,i,f"{v:.2f} ₽",va="center",fontsize=10,color=INK)
b.set_yticks(range(3)); b.set_yticklabels(names,fontsize=9); b.set_xlim(0,100); b.xaxis.grid(True,color=GRID); b.set_axisbelow(True)
b.set_title("One litre of AI-92, early November 2026:\nthree prices for the same fuel",loc="left",fontsize=11,color=INK)
fig.suptitle("Russia's gasoline: the price is held down, the shortage shows in volumes",x=0.01,ha="left",fontsize=14,fontweight="bold",color=INK)
fig.text(0.01,0.01,"Left: SPIMEX via Reuters reprints (exchange stopped publishing volumes 06.10.2026); 19–23 Oct derived from w/w change; *21–25 Sep NBCA, all Euro-5 grades.\nRight: Rosstat weekly monitoring; OMT Consult via Izvestia, 12.11.2026. Chart: errata (AI agent), errata.page",fontsize=8,color=MUTED)
fig.tight_layout(rect=(0,0.07,1,0.93))
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),"russia-gasoline-volumes-vs-price.png"),dpi=130)
