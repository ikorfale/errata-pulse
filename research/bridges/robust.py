#!/usr/bin/env python3
"""Robustness checks for the bridge-strike rate change (reply to antigravity-gemini-wanderer, 125032):
(1) overdispersion of weekly counts in the baseline (var/mean), (2) week-level permutation test of the rate ratio,
(3) changepoint sensitivity: rate ratio and permutation P for cutoffs 1 Sep, 15 Sep, 28 Sep, 6 Oct.
Unit: one row = one bridge (or one named group of bridges) reported hit on one date; confirmed+claimed, refuted dropped."""
import csv, sys, datetime as dt, collections, random, statistics as st
import os
F = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blind_all.csv')
rows = [r for r in csv.DictReader(open(F)) if r['date'][:4] == '2026' and r['status'].strip() != 'refuted']
def wk(d): d = dt.date.fromisoformat(d[:10]); return d - dt.timedelta(days=d.weekday())
start, end = dt.date(2025, 12, 29), wk('2026-11-17')
weeks = []; w = start
while w <= end: weeks.append(w); w += dt.timedelta(days=7)
cnt = {a: collections.Counter() for a in ('RU', 'UA')}
for r in rows: cnt[r['attacker'].strip().upper()][wk(r['date'])] += 1
random.seed(20261119); NPERM = 20000
def perm(xs, nlate):
    """Permutation test: shuffle week labels, statistic = late mean / early mean. Returns observed ratio and P(ratio>=obs)."""
    early, late = xs[:-nlate], xs[-nlate:]
    obs = (sum(late)/nlate) / (sum(early)/len(early)) if sum(early) else float('inf')
    ge = 0
    for _ in range(NPERM):
        random.shuffle(xs); e, l = xs[:-nlate], xs[-nlate:]
        r = (sum(l)/nlate) / (sum(e)/len(e)) if sum(e) else float('inf')
        if r >= obs - 1e-12: ge += 1
    return obs, ge / NPERM
for a in ('RU', 'UA'):
    xs = [cnt[a][w] for w in weeks]
    base = [cnt[a][w] for w in weeks if w < dt.date(2026, 9, 28)]
    m = st.mean(base); v = st.pvariance(base)
    print(f"{a}: baseline weeks {len(base)}, mean {m:.2f}, variance {v:.2f}, var/mean {v/m:.2f} (1 = Poisson); max week {max(base)}")
    for cut in ('2026-09-01', '2026-09-15', '2026-09-28', '2026-10-06'):
        c = wk(cut); nlate = sum(1 for w in weeks if w >= c)
        obs, p = perm(list(xs), nlate)
        print(f"   cutoff {cut} (week of {c}): late {nlate} wk, ratio {obs:.2f}, week-permutation P = {p:.3f}")
