#!/usr/bin/env python3
"""antigravity 125409: split Russian rows by city group x status x period (early = 39 weeks to 27 Sep, late = 8 weeks from 28 Sep).
Same data and filters as robust2.py. Tests whether 'claimed' rows in Zaporizhzhia/Dnipro carry the signal of subset (c)."""
import collections, robust2 as R  # reuses ALL, city(), wk(), CUT (robust2 prints its own output first)
t = collections.Counter((R.city(r), r['status'].strip(), 'late' if R.wk(r['date']) >= R.CUT else 'early') for r in R.ALL)
print("\nRussian rows by group, status and period (early 39 wk | late 8 wk):")
for g in ('Kyiv', 'Zaporizhzhia', 'Dnipro', 'other'):
    for s in ('confirmed', 'claimed'):
        print(f"   {g:13s} {s:9s} early {t[(g,s,'early')]:2d} | late {t[(g,s,'late')]:2d}")
