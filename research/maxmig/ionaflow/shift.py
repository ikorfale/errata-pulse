#!/usr/bin/env python3
"""Per-governor Max vs Telegram balance across the three IONAFLOW weeks.
Population: heads of regions listed on both platforms by IONAFLOW, minus Leningrad (IONAFLOW's Telegram
count is 0 while my own t.me/s collection has 33 and 26 posts in the April and July weeks)."""
import csv, statistics, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'per_governor.csv'), encoding='utf-8')))
P = ['2026-04-06_2026-04-12', '2026-07-15_2026-07-21', '2026-10-24_2026-10-30']
EXCL = {'Александр Дрозденко'}
def g(r, p, t):
    if r['governor_key'] == 'Вячеслав Федорищев' and p == P[2] and t == 'telegram':
        return None  # IONAFLOW 07.11: Telegram not monitored in October -> missing
    v = r[f'{p}_{t}']
    return None if v == '' else int(v)
both = [r for r in rows if g(r, P[0], 'max') is not None and g(r, P[0], 'telegram') is not None and r['governor_key'] not in EXCL]
print('governors listed on both, after exclusion:', len(both))
for p in P:
    ok = [r for r in both if g(r, p, 'telegram') is not None]
    m = sum(g(r, p, 'max') for r in ok); t = sum(g(r, p, 'telegram') for r in ok)
    act = [r for r in both if g(r, p, 'telegram') is not None and g(r, p, 'max') + g(r, p, 'telegram') >= 5]
    mx = [r['governor_key'] for r in act if g(r, p, 'max') >= 1.5 * g(r, p, 'telegram')]
    tg = [r['governor_key'] for r in act if g(r, p, 'telegram') >= 1.5 * g(r, p, 'max')]
    eq = [r for r in act if g(r, p, 'max') == g(r, p, 'telegram')]
    print(p, f'max={m} tg={t} ratio={m/t:.2f} | active(>=5 posts)={len(act)} equal_week_totals={len(eq)} max>=1.5tg={len(mx)} tg>=1.5max={len(tg)}')
    print('   max-heavy:', ', '.join(sorted(mx)))
    print('   tg-heavy :', ', '.join(sorted(tg)))
# paired: same governors active in April and October
pair = [r for r in both if all(g(r, p, 'telegram') is not None and g(r, p, 'max') + g(r, p, 'telegram') >= 5 and g(r, p, 'telegram') > 0 for p in (P[0], P[2]))]
d = [g(r, P[2], 'max') / g(r, P[2], 'telegram') - g(r, P[0], 'max') / g(r, P[0], 'telegram') for r in pair]
print('paired Apr->Oct, n=', len(pair), 'median change in Max/TG ratio', round(statistics.median(d), 3),
      'up', sum(x > 0.05 for x in d), 'down', sum(x < -0.05 for x in d), 'flat', sum(abs(x) <= 0.05 for x in d))
