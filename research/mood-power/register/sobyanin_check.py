"""Completeness check: Sobyanin's own window summaries ("N беспилотников уничтожены на подлёте к Москве") vs the sum of
his per-post counts in the same window (Moscow time, post timestamp). Windows copied by hand from the summary posts."""
import json, datetime as dt
from sobyanin_daily import count
P = []
for l in open('sobyanin_2026.jsonl'):
    x = json.loads(l); c = count(x['text'])
    if c: P.append((dt.datetime.fromisoformat(x['dt']).replace(tzinfo=None) + dt.timedelta(hours=3), c, x['id']))
W = [(20974, '2026-07-18 08:30', '2026-07-25 08:30', 143), (21042, '2026-07-01 00:00', '2026-08-01 00:00', 780),
     (21069, '2026-08-04 08:30', '2026-08-04 22:00', 18), (21121, '2026-08-01 08:30', '2026-08-08 08:30', 82),
     (21141, '2026-08-10 20:30', '2026-08-11 08:30', 13), (21218, '2026-08-08 08:30', '2026-08-15 08:30', 123),
     (21350, '2026-08-15 08:30', '2026-08-22 08:30', 493), (21475, '2026-08-22 08:30', '2026-08-30 08:30', 50),
     (21544, '2026-08-01 08:30', '2026-09-01 08:30', 795), (21572, '2026-09-02 08:00', '2026-09-03 12:00', 143),
     (21832, '2026-09-12 08:30', '2026-09-19 08:30', 186), (21995, '2026-09-01 08:30', '2026-10-05 08:30', 862),
     (22006, '2026-10-05 20:30', '2026-10-06 05:00', 105), (22069, '2026-10-09 20:30', '2026-10-10 08:30', 25),
     (22107, '2026-10-12 20:30', '2026-10-13 07:00', 65), (22127, '2026-10-13 20:30', '2026-10-14 07:00', 180),
     (22171, '2026-10-10 08:30', '2026-10-17 08:30', 534), (22180, '2026-10-17 08:30', '2026-10-18 08:30', 127)]
f = lambda s: dt.datetime.fromisoformat(s)
print('summary_id\twindow\tsummary\tpost_sum\tposts\tratio')
for i, a, b, s in W:
    sel = [c for t, c, _ in P if f(a) <= t < f(b)]
    print(f'{i}\t{a}..{b[5:]}\t{s}\t{sum(sel)}\t{len(sel)}\t{sum(sel)/s:.2f}')
