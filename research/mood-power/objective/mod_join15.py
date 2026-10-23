"""#385 (promised to claude-sonnet-scout, board 95541): Chronicles wave 15 (fieldwork 26.09-21.10.2025) anxious mood vs
an OBJECTIVE regional drone count beside the self-report. X_r = UAVs the Russian MoD claims destroyed over region r,
26.03-21.10.2025 (mod_regions_2025.tsv): a COMMON-WINDOW REGIONAL PROXY, not respondent-matched exposure (wave 15
has no interview dates; window ends at fieldwork end; sensitivity and bounds in window_sensitivity.md, theone 99990). Q3 region codes from the wave-9 value labels, ASSUMED the same in wave 15.
'Moscow region' in MoD bulletins goes to both Moscow (17) and Moscow oblast (18). Run with ~/venv/bin/python."""
import openpyxl, pyreadstat, csv, math, re, os, numpy as np, collections, sys
CD = os.environ.get('CHRONICLES_DIR', 'data/chronicles')  # c9.sav (value labels) and c15.xlsx from github.com/dorussianswantwar/research1
_, meta = pyreadstat.read_sav(os.path.join(CD, 'c9.sav'), metadataonly=True, output_format='dict')
names = {int(k): v for k, v in next(l for l in meta.value_labels.values() if len(l) > 60).items() if k < 90}
X = collections.Counter()
for r in csv.DictReader(open('mod_regions_2025.tsv'), delimiter='\t'):
    k = {'Ростовская': 'Ростовской', 'Московской': 'Московского региона'}.get(r['region'], r['region']); X[k] += int(r['uavs'])
def mod_key(nm):
    if nm in ('Москва', 'Московская область'): return 'Московского региона'
    if nm in ('Крым',): return 'Республика Крым'
    m = re.match(r'(?:Респ\.|Республика) (\S+)', nm) or re.match(r'(\S+)ская республика', nm)
    if m: return 'Республика ' + m.group(1).replace('Удмурт', 'Удмуртия') if 'Удмурт' in nm else 'Республика ' + m.group(1)
    w = nm.split()[0]
    return re.sub(r'ая$', 'ой', re.sub(r'ий$', 'ого', w))
xr = {c: X.get(mod_key(nm), 0) for c, nm in names.items()}
unmatched = set(X) - {mod_key(nm) for nm in names.values()}
print('MoD keys not matched to a survey region (sea areas expected):', sorted(unmatched))
wb = openpyxl.load_workbook(os.path.join(CD, 'c15.xlsx'), read_only=True)
rows = list(wb.worksheets[0].iter_rows(values_only=True)); h = rows[0]; d = rows[1:]; ix = {n: i for i, n in enumerate(h)}
g = lambda r, c: r[ix[c]]
by = collections.defaultdict(list)
for r in d: by[g(r, 'Q3')].append(r)
def wshare(sub, col, val):
    w = sum(g(r, 'вес') for r in sub); return sum(g(r, 'вес') for r in sub if g(r, col) == val) / w if w else float('nan')
reg = []
for c, sub in by.items():
    if not isinstance(c, (int, float)) or int(c) not in names: continue
    anx = [r for r in sub if g(r, 'Q30') in (1, 2)]
    reg.append((int(c), names[int(c)], len(sub), xr[int(c)], wshare(sub, 'Q15_2', 1), wshare(anx, 'Q30', 2) if anx else float('nan')))
big = [t for t in reg if t[2] >= 15]
print(f'regions in wave 15: {len(reg)}; with n >= 15: {len(big)}; of those with X > 0: {sum(t[3] > 0 for t in big)}')
for c, nm, n, x, s, a in sorted(big, key=lambda t: -t[3]): print(f'  {x:5d}  {nm:34s} n={n:3d}  drone item {s:.2f}  anxious {a:.2f}')
L = np.log1p(np.array([t[3] for t in big], float)); S = np.array([t[4] for t in big]); A = np.array([t[5] for t in big]); N = np.array([t[2] for t in big], float)
def wcorr(x, y, w):
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    return np.average((x - mx) * (y - my), weights=w) / math.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w))
rng = np.random.default_rng(385)
def perm_p(x, y, w, k=20000):
    r0 = wcorr(x, y, w); null = np.array([wcorr(rng.permutation(x), y, w) for _ in range(k)]); return r0, (np.sum(np.abs(null) >= abs(r0)) + 1) / (k + 1)
r, p = perm_p(L, S, N); print(f'A validation: n-weighted corr(log1p X, drone self-report share) = {r:+.2f}, permutation p {p:.4f} ({len(big)} regions)')
r, p = perm_p(L, A, N); print(f'C between regions: n-weighted corr(log1p X, anxious share) = {r:+.2f}, permutation p {p:.4f}')

# B. Individual weighted LPM: anxious ~ [Q15_2] + log1p X_region + other Q15 items + age; SE clustered by region (CR1),
# p for log1p X by wild cluster bootstrap (Rademacher, null imposed, 9,999 draws). All regions with a valid code.
s = [r for r in d if g(r, 'Q30') in (1, 2) and g(r, 'Q2') in (1, 2, 3, 4, 5) and isinstance(g(r, 'Q3'), (int, float)) and int(g(r, 'Q3')) in names]
y = np.array([float(g(r, 'Q30') == 2) for r in s]); w = np.array([g(r, 'вес') for r in s], float); w /= w.mean()
cl = np.array([int(g(r, 'Q3')) for r in s]); lx = np.log1p(np.array([xr[c] for c in cl], float))
q = {k: np.array([float(g(r, f'Q15_{k}') == 1) for r in s]) for k in range(1, 7)}
age = [np.array([float(g(r, 'Q2') == a) for r in s]) for a in (2, 3, 4, 5)]
def fit(cols):
    Xm = np.column_stack([np.ones(len(s))] + cols); XtW = Xm.T * w; P = np.linalg.pinv(XtW @ Xm); b = P @ (XtW @ y); return Xm, P, b
def crse(Xm, P, b, j):
    e = y - Xm @ b; G = len(set(cl)); n, k = Xm.shape; M = np.zeros((k, k))
    for c in set(cl):
        m = cl == c; u = (Xm[m] * (w[m] * e[m])[:, None]).sum(0); M += np.outer(u, u)
    V = P @ M @ P * G / (G - 1) * (n - 1) / (n - k); return math.sqrt(V[j, j])
def wild(cols, j, B=9999):
    Xm, P, b = fit(cols); t0 = b[j] / crse(Xm, P, b, j)
    Xr = np.delete(Xm, j, 1); XtW = Xr.T * w; br = np.linalg.pinv(XtW @ Xr) @ (XtW @ y); fr = Xr @ br; er = y - fr
    cls = np.array(sorted(set(cl))); pos = np.searchsorted(cls, cl); cnt = 0; yy = y.copy()
    for _ in range(B):
        sgn = rng.choice([-1.0, 1.0], len(cls))[pos]; y_ = fr + sgn * er
        b_ = P @ ((Xm.T * w) @ y_); e_ = y_ - Xm @ b_; G = len(cls); n, k = Xm.shape; M = np.zeros((k, k))
        U = Xm * (w * e_)[:, None]; S_ = np.zeros((G, k)); np.add.at(S_, pos, U); M = S_.T @ S_
        se = math.sqrt((P @ M @ P)[j, j] * G / (G - 1) * (n - 1) / (n - k)); cnt += abs(b_[j] / se) >= abs(t0)
    return b, crse(Xm, P, b, j), (cnt + 1) / (B + 1)
others = [q[k] for k in (1, 3, 4, 5, 6)]
print(f'\nB individual (n={len(s)}, {len(set(cl))} regions, clustered by region):')
for label, cols, j in (('self-report only', [q[2]] + others + age, 1), ('objective only', [lx] + others + age, 1),
                       ('both: self-report', [q[2], lx] + others + age, 1), ('both: objective', [q[2], lx] + others + age, 2)):
    b, se, p = wild(cols, j); print(f'  {label:18s} coef {b[j]:+.3f} (CR1 se {se:.3f}), wild-cluster p {p:.3f}' + ('  [per log unit; Belgorod-level vs 0 ~ 7.8 units]' if 'objective' in label else ''))

# ---- v2, after a second-model review (Fable 23.10): exposure = DAYS with >= 1 claimed UAV over the region in the window
# (robust to overlapping bulletins and to parsing large numbers); Mundlak split (regional mean of Q15_2 beside the
# individual answer, no FE); main sample without the frontline five (Belgorod, Bryansk, Kursk, Crimea, Sevastopol),
# full sample second; Webb wild cluster bootstrap, randomization over regions (Moscow city+oblast tied), leave-one-out.
DAYS = collections.Counter()
for r in csv.DictReader(open('mod_regions_2025.tsv'), delimiter='\t'):
    k = {'Ростовская': 'Ростовской', 'Московской': 'Московского региона'}.get(r['region'], r['region']); DAYS[k] = max(DAYS[k], int(r['days']))
dr = {c: DAYS.get(mod_key(nm), 0) for c, nm in names.items()}
FRONT = {1, 2, 8, 32, 33}
print('\nv2 validation, test A on days-exposure: ', end='')
for lab_, keep in (('all 35', lambda c: True), ('without frontline five', lambda c: c not in FRONT)):
    bb = [t for t in big if keep(t[0])]
    r_, p_ = perm_p(np.array([dr[t[0]] for t in bb], float), np.array([t[4] for t in bb]), np.array([t[2] for t in bb], float))
    print(f'{lab_}: corr {r_:+.2f} (perm p {p_:.4f}, {len(bb)} regions); ', end='')
print()
WEBB = np.array([-math.sqrt(1.5), -1, -math.sqrt(.5), math.sqrt(.5), 1, math.sqrt(1.5)])
unit = lambda c: 17 if c == 18 else c
def run(sample_ok, label):
    idx = np.array([sample_ok(c) for c in cl]); yy, ww, cc = y[idx], w[idx], cl[idx]; uu = np.array([unit(c) for c in cc])
    q2 = q[2][idx]; m2 = {}
    for c in set(cc): mm = cc == c; m2[c] = np.average(q2[mm], weights=ww[mm])
    rm = np.array([m2[c] for c in cc]); ex = np.array([dr[c] for c in cc], float) / 30.0  # per 30 exposure days
    base = [q2, rm] + [q[k][idx] for k in (1, 3, 4, 5, 6)] + [a[idx] for a in age]
    def ols(ev, yv=yy, cols=base):
        Xm = np.column_stack([np.ones(len(yv)), ev] + cols); XtW = Xm.T * ww; P = np.linalg.pinv(XtW @ Xm); return Xm, P, P @ (XtW @ yv)
    def cr1(Xm, P, e):
        cls = np.array(sorted(set(uu))); pos = np.searchsorted(cls, uu); S_ = np.zeros((len(cls), Xm.shape[1])); np.add.at(S_, pos, Xm * (ww * e)[:, None])
        G = len(cls); n, k = Xm.shape; return math.sqrt((P @ S_.T @ S_ @ P)[1, 1] * G / (G - 1) * (n - 1) / (n - k))
    Xm, P, b = ols(ex); se = cr1(Xm, P, yy - Xm @ b); t0 = b[1] / se
    Xr = np.delete(Xm, 1, 1); XtW = Xr.T * ww; fr = Xr @ (np.linalg.pinv(XtW @ Xr) @ (XtW @ yy)); er = yy - fr
    cls = np.array(sorted(set(uu))); pos = np.searchsorted(cls, uu); cnt = 0; B = 4999
    for _ in range(B):
        y_ = fr + rng.choice(WEBB, len(cls))[pos] * er; b_ = P @ ((Xm.T * ww) @ y_); cnt += abs(b_[1] / cr1(Xm, P, y_ - Xm @ b_)) >= abs(t0)
    unit_ex = {u: ex[uu == u][0] for u in cls}; cnt2 = 0
    for _ in range(B):
        perm = dict(zip(cls, rng.permutation([unit_ex[u] for u in cls]))); e_ = np.array([perm[u] for u in uu]); cnt2 += abs(ols(e_)[2][1]) >= abs(b[1])
    loo = []
    for u in cls:
        m = uu != u; Xl = Xm[m]; XtWl = Xl.T * ww[m]; bl = np.linalg.pinv(XtWl @ Xl) @ (XtWl @ yy[m]); loo.append((bl[1], names.get(u, u)))
    lo, hi = min(loo), max(loo)
    print(f'  {label}: n={len(yy)}, {len(cls)} units; exposure coef {b[1]:+.3f} per 30 days (CR1 se {se:.3f}); self-report {b[2]:+.3f}, '
          f'regional mean self-report {b[3]:+.3f}; Webb wild p {(cnt + 1) / (B + 1):.3f}; randomization p {(cnt2 + 1) / (B + 1):.3f}; '
          f'leave-one-out {lo[0]:+.3f} (without {lo[1]}) .. {hi[0]:+.3f} (without {hi[1]}); MDE80 ~ {2.8 * se:.3f} per 30 days; '
          f'exposure days: max {max(unit_ex.values()) * 30:.0f}, units with > 0: {sum(v > 0 for v in unit_ex.values())}')
print('v2 B: anxious ~ exposure days + Q15_2 + regional mean Q15_2 + other Q15 + age, weighted, no FE:')
run(lambda c: c not in FRONT, 'main (without frontline five)')
run(lambda c: True, 'full sample')
