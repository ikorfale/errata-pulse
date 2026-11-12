"""Chronicles wave 13 (Sep 2024, open microdata, n=999): does support for withdrawing troops differ between people who
get war news from TV (Q20_2) vs YouTube (Q20_5), and does the gap survive holding age band (Q2) fixed?
Q20 = 'From what sources do you get information about the conflict' (read out one by one, 1=yes 0=no).
Q121 (half A): withdraw troops and start talks without achieving the goals; Q122 (half B): withdraw + ceasefire talks.
Support = code 1, weighted by weight_full; se from unweighted n. Age-adjusted gap = inverse-variance average of
within-age-band gaps (bands with n<10 on either side skipped). Q20_11 is a second 'YouTube channels' in the English
questionnaire (translation duplicate?) and is NOT used. Q14 goal today printed for the page.
Run: ~/venv/bin/python3 -I lab/mood/chronicles13_media.py > lab/mood/chronicles13_media.out"""
import sys, math, collections, openpyxl
path = sys.argv[1] if len(sys.argv) > 1 else 'lab/mood/data/chronicles13/c13_en.xlsx'
ws = openpyxl.load_workbook(path, read_only=True)['Sample A for publ']; rows = ws.iter_rows(values_only=True)
hdr = [str(h) for h in next(rows)]; ix = {h: i for i, h in enumerate(hdr)}
data = [r for r in rows if r[0] is not None]; W = ix['weight_full']

def share(rs, q):
    w = sum(float(r[W]) for r in rs); s = sum(float(r[W]) for r in rs if r[ix[q]] == 1); n = len(rs)
    p = s / w if w else float('nan'); return p, (math.sqrt(p * (1 - p) / n) if n else float('nan')), n

print('n total', len(data))
for q in ('Q121', 'Q122'):
    sub = [r for r in data if r[ix[q]] in (1, 2, 98, 99)]
    print(f'\n{q}: n {len(sub)} support {share(sub, q)[0]:.3f}')
    for item, name in (('Q20_2', 'TV'), ('Q20_5', 'YouTube'), ('Q20_6', 'Telegram')):
        y = share([r for r in sub if r[ix[item]] == 1], q); n0 = share([r for r in sub if r[ix[item]] == 0], q)
        raw = y[0] - n0[0]; se = math.sqrt(y[1] ** 2 + n0[1] ** 2)
        num = den = 0.0; bands = []
        for a in sorted(set(r[ix['Q2']] for r in sub), key=str):
            ra = [r for r in sub if r[ix['Q2']] == a]
            ya = [r for r in ra if r[ix[item]] == 1]; na = [r for r in ra if r[ix[item]] == 0]
            if len(ya) < 10 or len(na) < 10: bands.append(f'{a}:skip({len(ya)}/{len(na)})'); continue
            p1, s1, _ = share(ya, q); p0, s0, _ = share(na, q); v = s1 ** 2 + s0 ** 2
            if v == 0: continue
            num += (p1 - p0) / v; den += 1 / v; bands.append(f'{a}:{p1 - p0:+.2f}(n{len(ya)}/{len(na)})')
        adj = num / den; ase = math.sqrt(1 / den)
        print(f'  {name:8s} users {y[0]:.3f} (n {y[2]}) non-users {n0[0]:.3f} (n {n0[2]})  raw {raw:+.3f} se {se:.3f}'
              f' | age-adjusted {adj:+.3f} se {ase:.3f}  [{" ".join(bands)}]')
# share of TV / YouTube users by age band
print('\nsource use by age band (Q2), weighted share:')
for a in sorted(set(r[ix['Q2']] for r in data), key=str):
    ra = [r for r in data if r[ix['Q2']] == a]; w = sum(float(r[W]) for r in ra)
    f = lambda it: sum(float(r[W]) for r in ra if r[ix[it]] == 1) / w
    print(f'  band {a}: n {len(ra)} TV {f("Q20_2"):.2f} YouTube {f("Q20_5"):.2f} Telegram {f("Q20_6"):.2f}')
d = collections.Counter(); w = collections.Counter()
for r in data: d[r[ix['Q14']]] += 1; w[r[ix['Q14']]] += float(r[W])
tot = sum(w.values())
print('\nQ14 goal today (1 Kursk, 2 DNR advance, 3 knows nothing of Kursk, 99 hard to say):',
      {k: (d[k], round(100 * w[k] / tot, 1)) for k in sorted(d, key=str)})
