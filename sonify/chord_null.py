"""zenith 80489: is the 'chord' real? Count days where >=3 of the 6 family voices are in their own
top-3 days of the month; compare with nulls that keep each family's series but break alignment:
(a) circular shift of each family by a random offset, (b) block shuffle, block = 7 days (longest rolling window).
Family value = the sonify voice (family max |z| vs its own usual max)."""
import json, sys, numpy as np, datetime as dt
SRC = sys.argv[1] if len(sys.argv) > 1 else 'pulse/signals/2026-10-08.json'
d = json.load(open(SRC)); end = dt.date.fromisoformat(d['date'])
days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]; idx = {x: i for i, x in enumerate(days)}
def zser(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    for i in range(1, 30):
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med))
    if mad == 0: mad = np.std(v[ok]) or 1.0
    return np.nan_to_num((v - med) / mad)
import os; CLIP = None if os.environ.get("NOCLIP") else 3.0
FAMS = ['energy', 'military', 'control', 'anxiety', 'hidden war', 'mobilisation']
V = {}
for f in FAMS:
    zs = [z for s in d['signals'] if s['family'] == f and (z := zser(s.get('series') or [])) is not None]
    if not zs: continue
    m = np.abs(np.vstack(zs)).max(axis=0); mad = 1.4826 * np.median(np.abs(m - np.median(m))) or 1.0
    V[f] = (m - np.median(m)) / mad if CLIP is None else np.clip((m - np.median(m)) / mad, -CLIP, CLIP)
# board 80838/80874: a family whose every series is only carried forward on a day was not measured that day
# (Wikipedia pageviews lag a day, so the file's last day is all copies). CARRIED=1 marks those days unknown.
if os.environ.get("CARRIED"):
    for f in V:
        R = []
        for s in d['signals']:
            if s['family'] == f and zser(s.get('series') or []) is not None:
                v = np.zeros(30, bool)
                for t, x in s['series']:
                    if t in idx and x is not None: v[idx[t]] = True
                R.append(v)
        V[f] = np.where(np.vstack(R).any(axis=0), V[f], -np.inf)
        if np.isinf(V[f]).any(): print('unmeasured:', f, [days[i] for i in np.where(np.isinf(V[f]))[0]])
# board 81109 (gpb), PREREG addendum 2026-10-09 21:40: secondary statistic, never the primary. A family's day t uses
# only series with a real value on t; its value is compared with the same series' max on every other day of the
# window, so the reference set changes with the day. Score = -(days whose reference max beats it): >= -2 means
# "in its own top 3" (ties at the cut count). No fresh series that day = unknown (-inf).
OBS = bool(os.environ.get("OBSERVED_ONLY"))
if OBS:
    for f in list(V):
        Z, O = [], []
        for s in d['signals']:
            if s['family'] == f and (z := zser(s.get('series') or [])) is not None:
                o = np.zeros(30, bool)
                for t, x in s['series']:
                    if t in idx and x is not None: o[idx[t]] = True
                Z.append(np.abs(z)); O.append(o)
        Z, O = np.vstack(Z), np.vstack(O)
        sc = np.full(30, -np.inf)
        for t in range(30):
            if O[:, t].any():
                ref = Z[O[:, t]].max(axis=0)
                sc[t] = -float((ref > ref[t]).sum())
        V[f] = sc
        print(f'observed-only {f}: fresh series per day min {O.sum(0).min()} median {int(np.median(O.sum(0)))} of {len(O)}; '
              f'unknown days {[days[i] for i in np.where(np.isinf(sc))[0]]}')
F = list(V); M = np.vstack([V[f] for f in F])
def top3(row):  # days in the family's top 3 (ties at the cut included, so clipped plateaus count fully)
    return row >= -2 if OBS else row >= np.sort(row)[-3]
RUNS = bool(os.environ.get("RUNS"))  # zenith 80562: count runs of neighbouring chord days as one event
def chord_days(M, k=3):
    c = np.vstack([top3(r) for r in M]).sum(axis=0) >= k
    if not RUNS: return int(c.sum())
    return int(c[0] + (c[1:] & ~c[:-1]).sum())
real = chord_days(M); hits = np.vstack([top3(r) for r in M]).sum(axis=0)
for k in (3, 4): print('k', k, 'days:', [days[i] for i in np.where(hits >= k)[0]])
print('families:', F, ' top3 sizes:', [int(top3(r).sum()) for r in M])
print('real month: days with >=3 families in their top 3 =', real, ' on', [days[i] for i in np.where(hits >= 3)[0]])
rng = np.random.default_rng(1009); N = 2000
def circ(M): return np.vstack([np.roll(r, rng.integers(30)) for r in M])
def block(M, b=7):
    out = []
    for r in M:
        s = rng.integers(b); r2 = np.roll(r, -s); blocks = [r2[i:i + b] for i in range(0, 30, b)]
        rng.shuffle(blocks); out.append(np.roll(np.concatenate(blocks), s))
    return np.vstack(out)
for name, fn in [('circular shift', circ), ('block shuffle b=7', block)]:
    null = np.array([chord_days(fn(M)) for _ in range(N)])
    p = (1 + (null >= real).sum()) / (N + 1)
    print(f'{name:18s}: null mean {null.mean():.2f}, 95th pct {np.percentile(null, 95):.0f}, max {null.max()}, P(null >= {real}) = {p:.4f}  (N={N})')
for k in (2, 4):
    r = chord_days(M, k); null = np.array([chord_days(circ(M), k) for _ in range(N)])
    print(f'k={k}: real {r}, circular null mean {null.mean():.2f}, p = {(1 + (null >= r).sum()) / (N + 1):.4f}')
