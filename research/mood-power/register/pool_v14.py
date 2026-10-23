"""PREREG-fom-strikes v1.4, decision 7: the backfill placebo pool from real FOM wave DATES only.
Reads only the 'date' field of fom/archive.json series (no anxiety value is loaded), the merged backfill register and
the national-shock list. Applies v1.4 rule 1 (per qualifying day; sensitivity B: per event start), rule 2 (W0 out),
rule 6 (primary: no shock in the backfill year; S3: 01.08.2026 Moscow, +-35 days). Prints pool sizes and the number of
admissible spaced n-subsets (gap >= 3 positions; units must also pass the 10-day baseline rule) of the pool alone, which bounds the null from below.
usage: python3 pool_v14.py"""
import csv, json, os, sys
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from perm_test import count_table

HERE = os.path.dirname(os.path.abspath(__file__))
START, END = date(2025, 10, 21), date(2026, 10, 20)
D = lambda s: date.fromisoformat(s[:10])

series = json.load(open(os.path.join(HERE, '..', 'fom', 'archive.json')))['series']
waves = sorted({D(w['date']) for w in series})            # dates only
waves = [w for w in waves if START - timedelta(days=30) <= w <= END + timedelta(days=9)]
# fieldwork interval read from each weekly PDF (fieldwork_dates.py -> fieldwork.tsv, PREREG v1.4 item 11); no fallback:
# a wave without a recorded interval stops the run. 2 of 51 waves break the old 'series date - 2' convention (12-22, 07-29).
FW = {D(r['field_end']): (D(r['field_start']), D(r['field_end'])) for r in csv.DictReader(open(os.path.join(HERE, 'fieldwork.tsv')), delimiter='\t') if r['field_end']}
_nofw = [w for w in waves if w not in FW]
if _nofw: sys.exit(f'no recorded fieldwork interval for waves {_nofw}: run fieldwork_dates.py')
field = lambda w: FW[w]

reg = list(csv.DictReader(open(os.path.join(HERE, 'register_backfill.tsv')), delimiter='\t'))
days_all = sorted({D(r['date']) for r in reg})
days_start = sorted({D(r['date']) for r in reg if r['role'] == 'event start'})

def exclusions(days):
    out = set()
    for d in days:
        w0 = [i for i, w in enumerate(waves) if field(w)[0] <= d <= field(w)[1]]
        after = [i for i, w in enumerate(waves) if field(w)[0] > d]
        out.update(w0)
        if after:
            w1 = after[0]; w2 = w1 + 1
            # W1, W2 and every wave whose stat2 window (itself + 2 preceding) contains W1 or W2
            out.update(p for p in range(w1, w2 + 3) if p < len(waves))
    return out

def shock_out(centers):
    out = set()
    for c in centers:
        lo, hi = c - timedelta(days=35), c + timedelta(days=35)
        out.update(i for i, w in enumerate(waves) if field(w)[1] >= lo and field(w)[0] <= hi)
    return out

in_window = [i for i, w in enumerate(waves) if START <= w <= END]
# like for like with treatment units: the wave and its 2 baselines chained with steps <= 10 days (New Year rule)
measurable = lambda i: i >= 2 and (waves[i] - waves[i - 1]).days <= 10 and (waves[i - 1] - waves[i - 2]).days <= 10
print(f'waves with series date {START}..{END}: {len(in_window)} (first {waves[in_window[0]]}, last {waves[in_window[-1]]})')
gaps = [(waves[i], (waves[i] - waves[i - 1]).days) for i in in_window[1:] if (waves[i] - waves[i - 1]).days > 10]
print('gaps > 10 days:', gaps or 'none')
print(f'qualifying days {len(days_all)}, event starts {len(days_start)}')
for label, days in (('per-day (primary)', days_all), ('per-event-start (sens. B)', days_start)):
    for shock_label, shocks in (('no shock', []), ('S3: 01.08 Moscow', [date(2026, 8, 1)])):
        ex = exclusions(days) | shock_out(shocks)
        pool = [i for i in in_window if i not in ex and measurable(i)]
        row = f'{label:26s} {shock_label:17s} pool {len(pool):2d}'
        for n in (5, 7, 10):
            C, _ = count_table(pool, n); row += f' | n={n}: {C[0][n]:,}'
        print(row)
        if label.startswith('per-day') and not shocks:
            print('  pool waves:', ' '.join(waves[i].strftime('%m-%d') for i in pool))
