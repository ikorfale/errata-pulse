"""zenith 80605 points 1-2: per family, how many series sit in their own top 3 on each day.
Loose = v1 count (ties at the cut included, forward-filled days count). Strict = exactly the 3 highest |z| per series,
ties broken by the raw value, forward-filled days never counted; baseline is then exactly n*3/30 per day."""
import json, sys, numpy as np, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else 'pulse/signals/2026-10-08.json'
d = json.load(open(SRC)); end = dt.date.fromisoformat(d['date'])
days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]; idx = {x: i for i, x in enumerate(days)}
FAMS = ['energy', 'military', 'control', 'anxiety', 'hidden war', 'mobilisation']
def zser(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    real = ~np.isnan(v)
    for i in range(1, 30):
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med))
    if mad == 0: mad = np.std(v[ok]) or 1.0
    return np.nan_to_num((v - med) / mad), np.nan_to_num(v), real
loose, strict, size = {}, {}, {}
for f in FAMS:
    L, S = np.zeros(30, int), np.zeros(30, int); n = 0
    for s in d['signals']:
        if s['family'] != f or (r := zser(s.get('series') or [])) is None: continue
        z, raw, real = r; a = np.abs(z); n += 1
        L += a >= np.sort(a)[-3]
        key = np.where(real, a, -np.inf)                          # filled days can never be a top day
        order = np.lexsort((np.abs(raw), key))[::-1][:3]           # |z| first, raw value breaks ties
        top = np.zeros(30, bool); top[order[np.isfinite(key[order])]] = True; S += top
    if n: loose[f], strict[f], size[f] = L, S, n
F = list(size); n = sum(size.values())
print('series per family:', size, ' total', n, ' strict baseline/day', n * 3 / 30)
TL, TS = sum(loose.values()), sum(strict.values())
print('median day: loose', np.median(TL), ' strict', np.median(TS))
rank = lambda T, i: int((T > T[i]).sum()) + 1
for day in ['2026-09-20', '2026-09-21', '2026-09-26', '2026-09-27', '2026-10-08']:
    i = idx[day]
    print(day, f'loose {TL[i]:2d} (rank {rank(TL, i):2d}/30)  strict {TS[i]:2d} (rank {rank(TS, i):2d}/30)  per family strict:',
          ' '.join(f'{f[:4]}={strict[f][i]}/{size[f]}' for f in F))
print('strict top-5 days:', [(days[i], int(TS[i])) for i in np.argsort(-TS, kind='stable')[:5]])
