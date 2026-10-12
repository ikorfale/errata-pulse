# Recall of the four Chaos Pulse monitors under five denominators, Wilson 95% CI. Numbers from recall.out, recall2.out, ukmto_recall.md.
import math, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows = [("UKMTO attacks, 1-7 Oct\n(independent count)", 3, 9),
        ("UKMTO warnings, 1-11 Oct\n(list built from news)", 5, 8),
        ("Ledger, 8-11 Oct, events\nI did NOT find via a monitor", 11, 14),
        ("Ledger, 8-11 Oct,\nin scope of a query", 22, 25),
        ("Ledger, 5-7 Oct,\nin scope (old queries)", 13, 17)]
def wilson(k, n, z=1.96):
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return c-h, c+h
fig, ax = plt.subplots(figsize=(10, 5.6), dpi=120)
for i, (lab, k, n) in enumerate(rows):
    lo, hi = wilson(k, n); p = k/n
    col = '#b5523b' if i < 2 else '#2f5d7c'
    ax.plot([lo, hi], [i, i], color=col, lw=3, alpha=.35, solid_capstyle='round')
    ax.plot(p, i, 'o', color=col, ms=10)
    ax.text(hi+.02, i, f"{k}/{n} = {p:.0%}", va='center', fontsize=11)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=10)
ax.set_xlim(0, 1.12); ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.set_xlabel('share of real events the monitors caught (dot) with 95% Wilson interval (bar)')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.set_title('Same monitors, different ground truths: the more independent, the lower the recall', loc='left', fontsize=12)
fig.text(.01, .01, 'errata.page · four Parallel monitors, hourly, Oct 2026 · blue: my event ledger, red: shipping-incident count from UKMTO', fontsize=8, color='#666')
plt.tight_layout(rect=(0, .03, 1, 1)); plt.savefig('monitor-recall-denominators.png')
