"""#206: which per-signal anomaly badges (5-8 Oct) survive a family-max baseline?
A flagged signal survives if, on its day, its family's strongest |z| is > 2 robust sigma above
the family's usual strongest |z| over the 30 days (same statistic as the sonify voices),
and its own |z| is at least half of that day's family maximum (it is one of the signals making the noise)."""
import json, numpy as np, datetime as dt
def zser(series, days):
    idx = {x: i for i, x in enumerate(days)}; v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    for i in range(1, 30):
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med)) or (np.std(v[ok]) or 1.0)
    return np.nan_to_num((v - med) / mad)
tot = surv = 0
for day in ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08']:
    d = json.load(open(f'pulse/signals/{day}.json')); end = dt.date.fromisoformat(day)
    days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]
    fam = {}
    for s in d['signals']:
        z = zser(s.get('series') or [], days)
        if z is not None: fam.setdefault(s['family'], {})[s['id']] = z
    for s in d['signals']:
        if not s.get('anomaly'): continue
        tot += 1; F = fam.get(s['family'], {})
        if not F or s['id'] not in F: print(day, s['id'], '-> no 30-day series, cannot test'); continue
        m = np.abs(np.vstack(list(F.values()))).max(axis=0)
        mad = 1.4826 * np.median(np.abs(m - np.median(m))) or 1.0
        fz = (m[-1] - np.median(m)) / mad; own = F[s['id']][-1]
        ok = bool(fz > 2 and abs(own) >= 0.5 * m[-1]); surv += ok   # the family is unusual today AND this signal is among its loudest
        print(day, s['id'][:38].ljust(38), f'own z {own:6.1f}  family-max z {fz:5.1f}  n={len(F):2d}', 'SURVIVES' if ok else 'drops')
print(f'{surv} of {tot} badges survive')
