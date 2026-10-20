"""Chronicles wave 15 microdata (open, github.com/dorussianswantwar/research1): anxious mood (Q30) by
self-reported local events in the last six months (Q15_1..6). Weighted by 'вес'. Source: проект "Хроники" (www.chronicles.report)."""
import openpyxl, math, sys
wb = openpyxl.load_workbook(sys.argv[1] if len(sys.argv) > 1 else 'data/chronicles/c15.xlsx', read_only=True)
rows = list(wb.worksheets[0].iter_rows(values_only=True)); h = rows[0]; d = rows[1:]
ix = {n: i for i, n in enumerate(h)}
def share(sub):
    s = [r for r in sub if r[ix['Q30']] in (1, 2)]
    w = sum(r[ix['вес']] for r in s); a = sum(r[ix['вес']] for r in s if r[ix['Q30']] == 2)
    n = len(s); neff = w * w / sum(r[ix['вес']] ** 2 for r in s)
    p = a / w; se = math.sqrt(p * (1 - p) / neff)
    return n, p, se
print('n total', len(d), 'Q30 codes', sorted({r[ix['Q30']] for r in d}))
n, p, se = share(d); print(f'all: n={n} anxious={p:.3f} se={se:.3f}')
labels = {1: 'rail/airport disruptions', 2: 'shelling, drone attacks', 3: 'mobile internet outages', 4: 'power/water outages', 5: 'petrol shortages', 6: 'medicine shortages', 97: 'none of these'}
for k, lab in labels.items():
    col = f'Q15_{k}'
    if col not in ix: print('missing', col); continue
    yes = [r for r in d if r[ix[col]] == 1]; no = [r for r in d if r[ix[col]] == 0]
    n1, p1, s1 = share(yes); n0, p0, s0 = share(no)
    print(f'{lab:28s} yes n={n1:4d} {p1:.3f}  no n={n0:4d} {p0:.3f}  diff {p1-p0:+.3f} (se {math.hypot(s1,s0):.3f})')

# Each event adjusted for the others and age group: weighted linear probability model, robust (HC1) SE.
import numpy as np
s = [r for r in d if r[ix['Q30']] in (1, 2) and r[ix['Q2']] in (1, 2, 3, 4, 5)]
X = [[1.0] + [float(r[ix[f'Q15_{k}']] == 1) for k in range(1, 7)] + [float(r[ix['Q2']] == g) for g in (2, 3, 4, 5)] for r in s]
X = np.array(X); y = np.array([float(r[ix['Q30']] == 2) for r in s]); w = np.array([r[ix['вес']] for r in s])
W = w / w.mean(); XtWX = X.T @ (X * W[:, None]); b = np.linalg.solve(XtWX, X.T @ (W * y))
e = y - X @ b; meat = (X * (W * e)[:, None]).T @ (X * (W * e)[:, None]); n, k = X.shape
V = np.linalg.inv(XtWX) @ meat @ np.linalg.inv(XtWX) * n / (n - k)
names = ['const'] + [labels[k] for k in range(1, 7)] + ['age 30-39', 'age 40-49', 'age 50-59', 'age 60+']
print('\nadjusted (n=%d):' % n)
for nm, bi, vi in zip(names, b, np.diag(V)): print(f'  {nm:28s} {bi:+.3f} (se {math.sqrt(vi):.3f})')
cnt = [sum(r[ix[f'Q15_{k}']] == 1 for k in range(1, 7)) for r in s]
for c in range(0, 7):
    sub = [r for r, cc in zip(s, cnt) if cc == c]
    if len(sub) >= 30: nn, p, se = share(sub); print(f'  events reported = {c}: n={nn} anxious={p:.3f} (se {se:.3f})')
