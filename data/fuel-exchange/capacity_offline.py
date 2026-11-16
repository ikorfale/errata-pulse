#!/usr/bin/env python3
"""C(w) for PREREG-strikes-v2: primary capacity offline because of strikes, kt/d, per calendar week.

Input: halts.csv (one row per strike, coded from sources; see strikes_coding_notes.md, "C coding").
Output: capacity_weekly.csv  week_mon,week_sun,C_ktd,S_hit,rows
Trading week w (Mon-Fri) is paired with the calendar week before it (lag 1, PREREG v2).

Rules (amendment 3, written before any C value was computed):
- kt/d = capacity (Mt/yr) * 1000 / 365; a unit halt uses the unit capacity if reported, else the plant figure
  capped at the plant figure (never more than the plant).
- A halt runs from halt_start through restart_date - 1. With no reported restart it runs through the end of the
  calendar week of halt_start only (the minimum the sources support; silence is not a continued halt).
- Overlapping halts of the same refinery are merged (a strike on a plant already halted adds 0).
- Strikes with halt_scope 'none' count only in S_hit.
"""
import csv, sys, datetime as dt
from collections import defaultdict

D = dt.date.fromisoformat

def weeks(start, end):
    m = start - dt.timedelta(days=start.weekday())
    while m <= end:
        yield m
        m += dt.timedelta(days=7)

def main(src='halts.csv', out='capacity_weekly.csv', first='2026-08-31', last=None):
    rows = list(csv.DictReader(open(src)))
    first = D(first)
    last = D(last) if last else max(D(r['strike_date']) for r in rows)
    days = defaultdict(dict)              # refinery -> {date: ktd}
    hits = defaultdict(int)               # week monday -> S_hit
    for r in rows:
        sd = D(r['strike_date'])
        scope = r['halt_scope'].strip()
        if scope == 'none' or not r['halt_start']:
            hits[sd - dt.timedelta(days=sd.weekday())] += 1
            continue
        plant = float(r['capacity_mtpy'])
        cap = float(r['unit_capacity_mtpy']) if r.get('unit_capacity_mtpy') else plant
        ktd = min(cap, plant) * 1000 / 365
        a = D(r['halt_start'])
        b = D(r['restart_date']) - dt.timedelta(days=1) if r['restart_date'] else \
            a + dt.timedelta(days=6 - a.weekday())
        d = a
        while d <= b:
            days[r['refinery']][d] = max(days[r['refinery']].get(d, 0), ktd)
            d += dt.timedelta(days=1)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['week_mon', 'week_sun', 'C_ktd', 'S_hit'])
        for m in weeks(first, last):
            tot = sum(v for ref in days.values() for d, v in ref.items() if m <= d <= m + dt.timedelta(days=6))
            w.writerow([m, m + dt.timedelta(days=6), round(tot / 7, 1), hits.get(m, 0)])
    print(open(out).read())

if __name__ == '__main__':
    main(*sys.argv[1:])
