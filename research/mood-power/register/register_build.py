"""Backfill register 2025-10-21..2026-10-20, both criteria, merged by the PREREG rule (an event within 21 days of the
first date of an earlier qualifying strike joins it; no chaining; the first date counts).
Inputs: criterion (a) days from sobyanin_register.py / moscow_daily_backfill.tsv (listed in README.md), criterion (b)
from criterion_b_backfill.tsv. Output: register_backfill.tsv and a printout. No FOM value is read here.
Usage: python3 register_build.py [--sensA]   (--sensA drops (b) days that reach 5 only with rescuers or police)"""
import csv, sys, datetime as dt
A_DAYS = ['2026-06-18', '2026-08-16', '2026-08-18', '2026-09-03', '2026-09-20', '2026-10-06', '2026-10-14',
          '2026-10-17', '2026-10-18']  # README.md "Result: days >= 100"; MoD era had none
sensA = '--sensA' in sys.argv
rows = [('a', d, 'Moscow', '>=100 drones') for d in A_DAYS]
for r in csv.DictReader(open('criterion_b_backfill.tsv'), delimiter='\t'):
    if r['qualifies'] != 'yes': continue
    rp = int(r['rescuers_police'].rstrip('?') or 0)
    if sensA and int(r['toll_72h']) - rp < 5: continue
    rows.append(('b', r['date'], r['region'], f"{r['toll_72h']} dead"))
unres = [r['date'] for r in csv.DictReader(open('criterion_b_backfill.tsv'), delimiter='\t') if '?' in r['rescuers_police'] or r['target'] == 'unknown']
if unres: print(f'DRAFT: unresolved tags on {len(unres)} rows: {", ".join(unres)} (Fable review 23.10 #12)')
rows.sort(key=lambda x: (x[1], x[0]))
D = lambda s: dt.date.fromisoformat(s)
events, out = [], []
for c, d, reg, what in rows:
    if events and (D(d) - D(events[-1][0])).days <= 21:
        events[-1][1].append(d); role = f'member of {events[-1][0]}'
    else:
        events.append((d, [d])); role = 'event start'
    out.append((d, c, reg, what, role))
name = 'register_backfill_sensA.tsv' if sensA else 'register_backfill.tsv'
with open(name, 'w') as f:
    f.write('date\tcriterion\tregion\twhat\trole\n')
    for o in out: f.write('\t'.join(o) + '\n')
print(f'{len(rows)} qualifying days, {len(events)} merged events' + (' (sensitivity A)' if sensA else ''))
for e, m in events: print(f'  {e}: {len(m)} day(s) {", ".join(x[5:] for x in m)}')
