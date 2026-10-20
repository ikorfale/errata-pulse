"""Does the self-reported 'shelling, drone attacks' item (Q15_2) follow geography? Region names for Q3 taken from the
wave-9 SPSS value labels, ASSUMED to be the same coding in wave 15 (top codes agree: 17 Moscow, 18 Moscow oblast,
26 St Petersburg); not confirmed by Chronicles yet."""
import openpyxl, pyreadstat, collections
_, meta = pyreadstat.read_sav('data/chronicles/c9.sav', metadataonly=True, output_format='dict')
names = next(l for l in meta.value_labels.values() if len(l) > 60)
wb = openpyxl.load_workbook('data/chronicles/c15.xlsx', read_only=True)
rows = list(wb.worksheets[0].iter_rows(values_only=True)); h = rows[0]; d = rows[1:]; ix = {n: i for i, n in enumerate(h)}
by = collections.defaultdict(list)
for r in d: by[r[ix['Q3']]].append(r)
def ws(sub, col, val=1):
    w = sum(r[ix['вес']] for r in sub); return sum(r[ix['вес']] for r in sub if r[ix[col]] == val) / w
out = []
for code, sub in by.items():
    anx = [r for r in sub if r[ix['Q30']] in (1, 2)]
    out.append((ws(sub, 'Q15_2'), code, names.get(float(code), '?') if isinstance(code, (int, float)) else '?', len(sub), ws(anx, 'Q30', 2) if anx else float('nan')))
out.sort(reverse=True)
print('drone item share, code, region, n, anxious share   (n >= 15)')
for s, c, nm, n, a in out:
    if n >= 15: print(f'{s:.2f}  {c:>3}  {nm:28s} n={n:3d}  anxious {a:.2f}')
for c in (1, 2, 8):
    s = by.get(c, []); print('border', c, names.get(float(c)), 'n', len(s), f'drone {ws(s, "Q15_2"):.2f}' if s else '')

# Between regions: regional drone share vs regional anxious share (n >= 15). Within regions: drone item with region fixed effects.
import numpy as np, math
big = [(s, a, n) for s, c, nm, n, a in out if n >= 15]
S, A, N = map(np.array, zip(*big))
print(f'\nbetween regions ({len(big)}): corr(drone share, anxious) = {np.corrcoef(S, A)[0,1]:+.2f}; n-weighted slope = {np.polyfit(S, A, 1, w=np.sqrt(N))[0]:+.3f}')
s = [r for r in d if r[ix['Q30']] in (1, 2) and r[ix['Q2']] in (1, 2, 3, 4, 5)]
codes = sorted({r[ix['Q3']] for r in s}, key=str)
X = np.array([[float(r[ix[f'Q15_{k}']] == 1) for k in range(1, 7)] + [float(r[ix['Q2']] == g) for g in (2, 3, 4, 5)] + [float(r[ix['Q3']] == c) for c in codes] for r in s])
y = np.array([float(r[ix['Q30']] == 2) for r in s]); W = np.array([r[ix['вес']] for r in s]); W = W / W.mean()
XtWX = X.T @ (X * W[:, None]); b = np.linalg.lstsq(XtWX, X.T @ (W * y), rcond=None)[0]
e = y - X @ b; P = np.linalg.pinv(XtWX); Z = X * (W * e)[:, None]; V = P @ (Z.T @ Z) @ P
lab = ['rail', 'drones', 'internet', 'power', 'petrol', 'medicine']
print('within regions (region fixed effects, age, n=%d):' % len(s))
for i, nm in enumerate(lab): print(f'  {nm:9s} {b[i]:+.3f} (se {math.sqrt(V[i,i]):.3f})')
