"""gpb 80990 / 4104 80996: on each of the last days, which series drives each family's max |z|, and was its value
observed that day or carried forward (with the date of the value it carries and its age). Ties within 1e-9 all listed."""
import json, sys, numpy as np, os, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else 'pulse/signals/2026-10-08.json'
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sonify.py')).read()
exec(src[src.index('FAM = '):src.index('fam_z, fam_n')])
def raw(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    return v
for key, *_ in FAM:
    S = [s for s in d['signals'] if s['family'] == key and zser(s.get('series') or []) is not None]
    if not S: continue
    Z = np.abs(np.nan_to_num(np.vstack([zser(s.get('series') or []) for s in S])))
    R = np.vstack([raw(s.get('series') or []) for s in S])
    for i in (27, 28, 29):
        top = Z[:, i].max(); drivers = np.nonzero(Z[:, i] >= top - 1e-9)[0]
        out = []
        for j in drivers:
            seen = np.nonzero(~np.isnan(R[j, :i + 1]))[0]
            src_day = days[seen[-1]] if len(seen) else None
            out.append(f"{S[j]['id'][:34]} ({'observed' if src_day == days[i] else 'carried from ' + str(src_day) + f', age {i - seen[-1]} d'})")
        nobs = int((~np.isnan(R[:, i])).sum())
        print(f"{key:12s} {days[i]}  max|z| {top:5.1f}  observed {nobs}/{len(S)}  driver: {'; '.join(out)}")
