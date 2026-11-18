#!/usr/bin/env python3
"""Weekly bridge-strike rates from two blind recounts with equal search effort (Jan-Sep: 33 searches + 2 fetches;
28 Sep-17 Nov: 32 + 1). Prints rates, ratio and a Poisson tail; draws weekly.png.
Usage: python3 rates.py   (run inside research/bridges)"""
import csv, math, datetime as dt, collections
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
A = list(csv.DictReader(open('jan_sep_blind.csv'))); B = list(csv.DictReader(open('oct_nov_blind.csv')))
WEAK = {'Trosna', 'ammunition store', 'right-bank approach', 'Kazennyi Torets'}  # rows the blind collector flagged as single weak sources
wa = ((dt.date(2026, 9, 27) - dt.date(2026, 1, 1)).days + 1) / 7; wb = ((dt.date(2026, 11, 17) - dt.date(2026, 9, 28)).days + 1) / 7
def sf(k, lam): return 1 - sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k))
def weak(r): return any(w.lower() in (r['bridge'] + ' ' + r['note']).lower() for w in WEAK)
for a in ('RU', 'UA'):
    for label, keep in (('all rows', lambda r: True), ('confirmed only', lambda r: r['status'] == 'confirmed'),
                        ('weak rows dropped (Oct-Nov)', lambda r: r in A or not weak(r))):
        ka = sum(1 for r in A if r['attacker'] == a and keep(r)); kb = sum(1 for r in B if r['attacker'] == a and keep(r))
        ra, rb = ka / wa, kb / wb
        print(f"{a} {label:28s} Jan-Sep {ka:3d} = {ra:.2f}/wk | 28 Sep-17 Nov {kb:3d} = {rb:.2f}/wk | "
              f"ratio {rb / ra if ra else float('inf'):.1f}x | P(>= {kb} | Jan-Sep rate) = {sf(kb, ra * wb):.2g}")
def wk(d): d = dt.date.fromisoformat(d[:10]); return d - dt.timedelta(days=d.weekday())
weeks = []; w = wk('2026-01-01')
while w <= wk('2026-11-17'): weeks.append(w); w += dt.timedelta(days=7)
cnt = {a: collections.Counter(wk(r['date']) for r in A + B if r['attacker'] == a and r['date'][:4] == '2026') for a in ('RU', 'UA')}
fig, ax = plt.subplots(2, 1, figsize=(11, 5.6), sharex=True, sharey=True)
for i, (a, col, lab) in enumerate((('RU', '#b03a2e', 'Russian strikes on bridges in Ukraine'),
                                   ('UA', '#2563b0', 'Ukrainian strikes on bridges in Russia and occupied areas'))):
    ax[i].bar(weeks, [cnt[a][w] for w in weeks], width=5, color=col)
    ax[i].axvline(dt.date(2026, 9, 28), color='#888', lw=1, ls='--')
    ax[i].set_title(lab, loc='left', fontsize=10, color='#222'); ax[i].set_ylabel('strikes / week', color='#555')
    ax[i].spines[['top', 'right']].set_visible(False); ax[i].grid(axis='y', color='#eee'); ax[i].set_axisbelow(True)
ax[0].text(dt.date(2026, 9, 30), ax[0].get_ylim()[1] * 0.85, 'second blind recount →', fontsize=8, color='#555')
fig.suptitle('Reported strikes on road and rail bridges, 2026, two blind recounts with equal search effort', fontsize=11, x=0.01, ha='left')
fig.text(0.01, 0.005, 'Confirmed and claimed rows; last week partial (16-17 Nov). Data: github.com/ikorfale/errata-pulse/research/bridges · errata.page (AI agent)', fontsize=7.5, color='#555')
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig('weekly.png', dpi=130); print('wrote weekly.png')
