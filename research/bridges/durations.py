#!/usr/bin/env python3
"""Closure durations from strikes.csv: days from strike to first partial reopening (any traffic).
Closures <=14 days old without a reopening are counted to AS_OF and marked; older ones are "unknown", since a later strike or silence does not tell when traffic came back. Marked '>'. Usage: durations.py [strikes.csv] [AS_OF]"""
import csv, sys, datetime as dt
F = sys.argv[1] if len(sys.argv) > 1 else 'strikes.csv'
AS_OF = dt.date.fromisoformat(sys.argv[2] if len(sys.argv) > 2 else '2026-11-18')
rows = [r for r in csv.DictReader(open(F)) if r['closed'].strip().lower() in ('yes', 'partial')]
out = []
for r in rows:
    d0 = dt.date.fromisoformat(r['date'])
    if r['reopened'].strip():
        n = (dt.date.fromisoformat(r['reopened']) - d0).days; s = f"{n}"
    else:
        n = (AS_OF - d0).days
        s = f">{n}, still closed per last source" if n <= 14 else "unknown (no reopening report found)"
    out.append((r['attacker'], r['date'], r['bridge'][:60], r['closed'], s))
print(f"| side | strike | bridge | closed | days to first partial reopening (as of {AS_OF}) |\n|---|---|---|---|---|")
for o in out: print('| ' + ' | '.join(o) + ' |')
