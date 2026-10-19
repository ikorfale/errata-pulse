"""Monthly share of drone-alert posts >300 / >600 km from Ukraine's border, all regions vs a fixed region set,
with 90% intervals from a bootstrap that resamples whole days (posts within one raid are not independent)."""
import sys, json, random, collections
sys.argv = ['depth.py', 'events_sample.jsonl']
import depth
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R, miss, occ = depth.rows('events_sample.jsonl')
mon = collections.defaultdict(set)
for ts, d, reg in R: mon[ts[:7]].add(reg)
cnt = collections.Counter(r for v in mon.values() for r in v)
keep = {r for r, c in cnt.items() if c >= 0.8 * len(mon)}
pres = collections.defaultdict(set)
for ts, d, reg in R: pres[reg].add(ts[:7])
early = {r for r, v in pres.items() if r is not None and min(v) <= '2025-12'}   # fixed by entry, not persistence (see RESULT.md, correction)
def series(rows, thr, B=1000, seed=1):
    rng = random.Random(seed); bym = collections.defaultdict(lambda: collections.defaultdict(list))
    for ts, d, reg in rows: bym[ts[:7]][ts[:10]].append(d > thr)
    out = []
    for m in sorted(bym):
        days = list(bym[m].values()); flat = [x for v in days for x in v]; p = sum(flat) / len(flat)
        bs = []
        for _ in range(B):
            s = [x for _ in days for x in rng.choice(days)]; bs.append(sum(s) / len(s))
        bs.sort(); out.append((m, p, bs[int(.05 * B)], bs[int(.95 * B)], len(flat), len(days)))
    return out
res = {}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=False)
for ax, thr in zip(axes, (300, 600)):
    for lab, rows, c in ((f'all regions ({len(cnt)})', R, '#b5452b'), (f'fixed set ({len(keep)} regions in >=80% of months)', [x for x in R if x[2] in keep], '#2b6cb5'),
                       (f'regions seen by Dec 2025 ({len(early)})', [x for x in R if x[2] in early], '#2b9b5b')):
        s = series(rows, thr); res[f'{thr}|{lab}'] = s
        xs = range(len(s)); ax.plot(xs, [x[1] for x in s], 'o-', color=c, label=lab, lw=2)
        ax.fill_between(xs, [x[2] for x in s], [x[3] for x in s], color=c, alpha=.15)
    ax.set_xticks(range(len(s))); ax.set_xticklabels([x[0][2:] for x in s], rotation=45, fontsize=8)
    ax.set_title(f'share of alert posts > {thr} km from the border'); ax.grid(alpha=.3); ax.set_ylim(0, None)
axes[0].legend(fontsize=8, loc='lower right')
fig.suptitle('How deep into Russia do drone alerts reach? (sampled posts, 90% day-bootstrap bands; Oct 2026 = to 18.10)', fontsize=10)
fig.tight_layout(); fig.savefig('depth_monthly.png', dpi=130)
json.dump(res, open('depth_monthly.json', 'w'), indent=0)
for k, s in res.items():
    print(k); [print(f'  {m} {p:.2f} [{lo:.2f},{hi:.2f}] n={n} days={d}') for m, p, lo, hi, n, d in s]
