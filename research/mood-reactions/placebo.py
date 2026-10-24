#!/usr/bin/env python3
"""Post hoc (after the frozen run): the same contrast with every other day as a pseudo strike day, Fontanka.
How unusual is the 18.10 shift against the channel's ordinary day-to-day swings?"""
import analyze, io, contextlib
from datetime import date, timedelta
rows = []
d = date(2026, 10, 13)
while d <= date(2026, 10, 22):
    analyze.CASES['p'] = ('fontankaspb', d.isoformat(), 3)
    with contextlib.redirect_stdout(io.StringIO()):
        r = analyze.run('p')
    g = lambda k: f"{r[k][0]:+.3f}" if k in r else '  n/a '
    print(d, 'other derision', g(('other', 'derision')), '| other fear', g(('other', 'fear')),
          '| strike derision', g(('strike', 'derision')), '| strike pray', g(('strike', 'pray')))
    d += timedelta(days=1)
