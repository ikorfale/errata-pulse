"""Pooled share of strike posts >300 km, Nov-Mar vs Apr-Oct, with a bootstrap over days (one strike = many posts, so days are the unit)."""
import json, random, re, collections, runpy
g = runpy.run_path('exilenova_depth.py', run_name='halves')
by = g['by']; days = collections.defaultdict(list)
for mo, rows in by.items():
    for day, dep, s in rows: days[day].append(dep > 300)
early = [d for d in days if d < '2026-04']; late = [d for d in days if d >= '2026-04']
share = lambda ds: sum(sum(days[d]) for d in ds) / sum(len(days[d]) for d in ds)
random.seed(2); diffs = sorted(share(random.choices(late, k=len(late))) - share(random.choices(early, k=len(early))) for _ in range(4000))
print('days', len(early), len(late), 'early', round(share(early), 3), 'late', round(share(late), 3), 'diff', round(share(late) - share(early), 3), 'band95', round(diffs[100], 3), round(diffs[3899], 3))
