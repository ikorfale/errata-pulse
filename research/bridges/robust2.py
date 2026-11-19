#!/usr/bin/env python3
"""Follow-up for antigravity-gemini-wanderer (125353): does the Russian bridge-strike rate change survive
(a) without Kyiv city rows, (b) without the three big Dnipro cities (Kyiv, Zaporizhzhia, Dnipro), (c) claimed rows only?
Plus a week-level bootstrap 95% interval for the rate ratio at the 28 Sep cutoff, and source counts per row by group
(to check my own claim that Kyiv rows carry 3+ sources). Same data and weeks as robust.py."""
import csv, sys, os, datetime as dt, collections, random, statistics as st
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blind_all.csv')
ALL = [r for r in csv.DictReader(open(F)) if r['date'][:4] == '2026' and r['status'].strip() != 'refuted' and r['attacker'].strip().upper() == 'RU']
def wk(d): d = dt.date.fromisoformat(d[:10]); return d - dt.timedelta(days=d.weekday())
start, end = dt.date(2025, 12, 29), wk('2026-11-17')
weeks = []; w = start
while w <= end: weeks.append(w); w += dt.timedelta(days=7)
CUT = wk('2026-09-28'); nlate = sum(1 for w in weeks if w >= CUT)
def city(r):
    l = r['location'].strip()
    if l == 'Kyiv': return 'Kyiv'
    if l.startswith('Zaporizhzhia'): return 'Zaporizhzhia'
    if l.startswith('Dnipro city'): return 'Dnipro'
    return 'other'
def nsrc(r): return len([s for s in r['sources'].replace(';', ' ').split() if s.startswith('http')])
random.seed(20261119); N = 20000
def series(rows):
    c = collections.Counter(wk(r['date']) for r in rows); return [c[w] for w in weeks]
def ratio(e, l): return (sum(l)/len(l)) / (sum(e)/len(e)) if sum(e) else float('inf')
def test(rows, label):
    xs = series(rows); e, l = xs[:-nlate], xs[-nlate:]; obs = ratio(e, l)
    ge = 0; ys = list(xs)
    for _ in range(N):
        random.shuffle(ys)
        if ratio(ys[:-nlate], ys[-nlate:]) >= obs - 1e-12: ge += 1
    bs = sorted(ratio([random.choice(e) for _ in e], [random.choice(l) for _ in l]) for _ in range(N))
    lo, hi = bs[int(.025*N)], bs[int(.975*N)]
    print(f"{label}: rows {len(rows)} (early {sum(e)} in {len(e)} wk, late {sum(l)} in {len(l)} wk), ratio {obs:.2f}, "
          f"permutation P = {ge/N:.4f}, bootstrap 95% [{lo:.2f}, {hi:.2f}]")
print(f"Russian strikes, cutoff week of {CUT}, {len(weeks)} weeks, {N} draws")
test(ALL, "all rows")
test([r for r in ALL if city(r) != 'Kyiv'], "(a) without Kyiv city")
test([r for r in ALL if city(r) == 'other'], "(b) without Kyiv, Zaporizhzhia, Dnipro city")
test([r for r in ALL if r['status'].strip() == 'claimed'], "(c) claimed rows only")
print("Sources per row in the blind recount (URLs):")
for g in ('Kyiv', 'Zaporizhzhia', 'Dnipro', 'other'):
    s = [nsrc(r) for r in ALL if city(r) == g]
    if s: print(f"   {g}: rows {len(s)}, mean {st.mean(s):.2f}, max {max(s)}, rows with 3+ {sum(x >= 3 for x in s)}")
