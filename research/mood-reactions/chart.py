import json, statistics as st, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from analyze import BUCKETS
msk = timezone(timedelta(hours=3)); days = {}
for l in open('data/fontankaspb.jsonl'):
    p = json.loads(l); n = sum(p['reacts'].values())
    if n < 30: continue
    d = datetime.fromisoformat(p['time']).astimezone(msk).date()
    if not (datetime(2026,10,4).date() <= d <= datetime(2026,10,23).date()): continue
    days.setdefault(d, []).append({b: sum(v for e, v in p['reacts'].items() if e in s) / n for b, s in BUCKETS.items()})
xs = sorted(days)
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=120)
for key, col, lab in [('derision', '#b8572a', 'derision 🤡😁🤣😂💩'), ('pray', '#3a6ea5', 'pray 🙏'), ('fear', '#6b4c9a', 'fear 😱😨😢😭')]:
    ys = [st.median(r[key] for r in days[d]) for d in xs]
    ax.plot(xs, ys, color=col, lw=2.2, marker='o', ms=4)
    ax.annotate(lab.split()[0], (xs[-1], ys[-1]), xytext=(6, 0), textcoords='offset points', color=col, va='center', fontsize=11)
ax.axvline(datetime(2026,10,18).date(), color='#999', ls='--', lw=1)
ax.text(datetime(2026,10,18).date(), ax.get_ylim()[1]*0.97, ' 18.10 strike on St Petersburg', color='#555', fontsize=10, va='top')
ax.set_ylabel('daily median share of reactions per post'); ax.spines[['top','right']].set_visible(False)
ax.set_title('Fontanka (St Petersburg news channel): reader emoji reactions, posts with ≥30 reactions', fontsize=11.5, loc='left')
fig.text(0.01, 0.01, 'Data: public t.me/s previews, counts fetched 24.10. One channel; Omsk and Ryazan below the frozen minimum. errata.page', fontsize=8.5, color='#666')
fig.autofmt_xdate(); fig.tight_layout(rect=(0, 0.03, 0.97, 1)); fig.savefig('fontanka-reactions-1024.png')
