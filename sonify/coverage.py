"""Board 80838/80874/80900: does the render move because signals move, or because series enter the pool?
Per family and day: observed / forward-filled / missing (before the series' first value) counts.
Then the family track recomputed on the fixed common roster (series with a real value on day 1 of the
window, so never missing) with the same scaling rule, against the track as rendered (each day's available rows)."""
import json, sys, numpy as np, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else 'pulse/signals/2026-10-08.json'
import os; src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sonify.py')).read()
exec(src[src.index('FAM = '):src.index('fam_z, fam_n')].replace("d = json.load(open(SRC))", "d = json.load(open(SRC))"))
def raw(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    return v
def track(zs):
    Z = np.nan_to_num(np.vstack(zs)); m = np.abs(Z).max(axis=0)
    mad = 1.4826 * np.median(np.abs(m - np.median(m))) or 1.0
    return np.clip((m - np.median(m)) / mad, -3, 3), m
print('source', SRC, 'window', days[0], '..', days[-1])
for key, *_ in FAM:
    S = [s for s in d['signals'] if s['family'] == key and zser(s.get('series') or []) is not None]
    if not S: continue
    R = np.vstack([raw(s.get('series') or []) for s in S])
    obs = (~np.isnan(R)).sum(0)
    started = np.vstack([np.maximum.accumulate(~np.isnan(r)) for r in R]).sum(0)
    ffill, miss = started - obs, len(S) - started
    full = [s for s, r in zip(S, R) if not np.isnan(r[0])]
    za, ma = track([zser(s['series']) for s in S])
    print(f"\n{key}: n={len(S)} fixed-roster n={len(full)}  missing-before-start per day: max {miss.max()}, days with any {int((miss>0).sum())}; "
          f"forward-filled per day: median {int(np.median(ffill))}, max {ffill.max()}")
    if len(full) and len(full) < len(S):
        zf, mf = track([zser(s['series']) for s in full])
        r = np.corrcoef(za, zf)[0, 1]
        print(f"  track as rendered vs fixed roster: r={r:.2f}, max |diff|={np.abs(za-zf).max():.2f}, "
              f"loudest day {days[int(za.argmax())]} vs {days[int(zf.argmax())]}, days with |diff|>0.5: {int((np.abs(za-zf)>0.5).sum())}")
        late = [s['id'] for s, r in zip(S, R) if np.isnan(r[0])]
        print('  late entrants:', ', '.join(f"{i}@{days[int(np.argmax(~np.isnan(raw(s['series']))))]}" for i, s in zip(late, [s for s, r in zip(S, R) if np.isnan(r[0])])))
    else:
        print('  roster is fixed for the whole window: the track cannot move by membership')
print('__END__')
