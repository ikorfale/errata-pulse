"""Moscow daily drone count from Sobyanin's channel for PREREG criterion (a), with his own sub-daily summaries.
Finding (20.10, sobyanin_check.py): on raid nights he stops posting every downing and later gives one summary, so the
sum of single reports undercounts (ratio 0.39-1.00 against his own weekly/monthly totals). Rule: each summary window
(<=36 h) gets max(singles posted inside it, summary), attributed to the summary's posting date (Moscow time), like the
MoD rule "a night raid counts on the date of the morning bulletin"; singles outside every summary window count by day.
Summaries copied by hand from the posts (id, posted MSK, window start MSK, number, scope)."""
import json, collections, datetime as dt, sys
from sobyanin_daily import count
F = dt.datetime.fromisoformat
S = [(20349, '2026-06-17 18:00', 180, 'city'), (20420, '2026-06-21 11:23', 84, 'city'), (20654, '2026-07-03 11:05', 62, 'city'), (20781, '2026-07-11 17:45', 45, 'city'),
     (20791, '2026-07-12 20:30', 50, 'city'), (21069, '2026-08-04 08:30', 18, 'city'), (21141, '2026-08-10 20:30', 13, 'city'),
     (21234, '2026-08-15 18:00', 201, 'region'), (21261, '2026-08-17 18:00', 180, 'region'), (21301, '2026-08-19 20:30', 28, 'region'),
     (21572, '2026-09-02 08:00', 143, 'city'), (21814, '2026-09-17 20:00', 64, 'city'), (21849, '2026-09-19 07:51', 450, 'city'),
     (22006, '2026-10-05 20:30', 105, 'city'), (22069, '2026-10-09 20:30', 25, 'city'), (22107, '2026-10-12 20:30', 65, 'city'),
     (22127, '2026-10-13 20:30', 180, 'city'), (22180, '2026-10-17 08:30', 127, 'city')]
posts = {}
for l in open('sobyanin_2026.jsonl'):
    x = json.loads(l); posts[x['id']] = (F(x['dt']).replace(tzinfo=None) + dt.timedelta(hours=3), x['text'])
singles = [(t, c, i) for i, (t, tx) in posts.items() if (c := count(tx))]
used, day, how = set(), collections.Counter(), collections.defaultdict(list)
for sid, start, n, scope in S:
    end = posts[sid][0]
    inside = [(t, c, i) for t, c, i in singles if F(start) <= t <= end]
    used |= {i for _, _, i in inside}
    v = max(n, sum(c for _, c, _ in inside)); d = end.date().isoformat()
    day[d] += v; how[d].append(f'summary {sid} {scope} {n} vs singles {sum(c for _, c, _ in inside)}')
for t, c, i in singles:
    if i not in used: day[t.date().isoformat()] += c
if __name__ == '__main__':
    print('date\tmoscow_count\tsource')
    for d in sorted(day): print(f'{d}\t{day[d]}\t{"; ".join(how[d]) or "singles"}')
