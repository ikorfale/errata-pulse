#!/usr/bin/env python3
"""H5 subscriber test, written BEFORE any join of census and alerts (PREREG-H5-subs.md).
Do subscriber counts of a region's governor channel rise faster in 12-h census windows with more hours of
officially declared air alert in that region?

  z_it = beta * alert_hours_it + channel FE + window FE        (OLS after two-way demeaning)
  p    = region-permutation: alert series shuffled across regions, 2000 draws, seed 1113

Modes:
  --placebo   permuted exposure only (no real join) -> null spread and MDE by injection; allowed before the end date
  --final     the confirmatory run; refuses before END (no override)
Review: Fable 12.11 (stale flag, missing secondaries, window-permutation null, eligibility at freeze, 12-h window
bins, converging demeaning, MDE units) applied before the freeze.
Inputs: pulse/mood/subs/census.jsonl, pulse/alerts_live/*.jsonl, errata-pulse data/alerts_regions.json."""
import json, glob, math, sys, os, random, statistics as st, collections
from datetime import datetime, timezone, timedelta

W = os.environ.get('ERRATA_WORK', os.path.expanduser('~/work'))
CENSUS = os.path.join(W, 'pulse/mood/subs/census.jsonl')
ALERTS = os.path.join(W, 'pulse/alerts_live/*.jsonl')
REGIONS = os.environ.get('ERRATA_REGIONS', os.path.expanduser('~/errata-pulse/data/alerts_regions.json'))
FREEZE = '2026-11-12T21:05Z'   # frozen 12.11 (PREREG-H5-subs.md)
END = '2026-12-14T04:00Z'
BORDER = {'RU-KRS', 'RU-BRY', 'RU-BEL'}
MIN_SUBS, NORM_DAYS, WINSOR, MAD_FLOOR, N_PERM, SEED = 5000, 14, 10.0, 0.005, 2000, 1113
EXCLUDE = {'Республика Крым', 'Севастополь'}   # not in the Russian alert set as RU-*; different information space
ALIAS = {'Республика Татарстан': 'RU-TA', 'Республика Ингушетия': 'RU-IN', 'Республика Карелия': 'RU-KR',
         'Удмуртская Республика': 'RU-UD', 'Республика Марий Эл': 'RU-ME', 'Кабардино-Балкарская Республика': 'RU-KB',
         'Республика Дагестан': 'RU-DA', 'Чеченская Республика': 'RU-CE', 'Республика Северная Осетия — Алания': 'RU-SE',
         'Чувашская Республика': 'RU-CU', 'Республика Адыгея': 'RU-AD', 'Республика Мордовия': 'RU-MO',
         'Карачаево-Черкесская Республика': 'RU-KC', 'Республика Калмыкия': 'RU-KL'}

P = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))


def load_census(role='governor'):
    reg = json.load(open(REGIONS))['regions']
    name2iso = {v['ru']: k for k, v in reg.items()}; name2iso.update(ALIAS)
    ser = collections.defaultdict(list)
    for l in open(CENSUS):
        r = json.loads(l)
        if r['role'] != role or not r['subs'] or r['region'] in EXCLUDE: continue
        iso = name2iso.get(r['region'])
        if iso: ser[(iso, r['handle'])].append((P(r['ts']), r['subs']))
    return {k: sorted(v) for k, v in ser.items()}


def load_alerts():
    snaps = []
    for f in sorted(glob.glob(ALERTS)):
        for l in open(f):
            r = json.loads(l)
            snaps.append((P(r['ts']), r['a']))
    snaps.sort(key=lambda x: x[0]); return snaps


def alert_hours(snaps, t0, t1, types=('u', 'm', 'b'), stale_ok=True):
    """hours under alert per region in [t0,t1); None if snapshot coverage < 90% (gap > 15 min counts as missing).
    Primary: a declared alert not yet cancelled counts, stale flag or not."""
    sel = [s for s in snaps if t0 <= s[0] < t1]
    if not sel: return None
    cov, hrs = 0.0, collections.Counter()
    for i, (t, act) in enumerate(sel):
        nxt = sel[i + 1][0] if i + 1 < len(sel) else t1
        d = min((nxt - t).total_seconds(), 900) / 3600
        cov += d
        for k, v in act.items():
            if (stale_ok or not v.endswith('*')) and v.rstrip('*') in types: hrs[k] += d
    return hrs if cov >= 0.9 * (t1 - t0).total_seconds() / 3600 else None


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def panel(ser, snaps, start, end, lag=0, **kw):
    """rows (channel, window_key, z, iso, hours) for steps whose end lies in [start,end)."""
    rows = []
    for (iso, h), v in ser.items():
        pre = [s for t, s in v if t <= start]
        if not pre or pre[-1] < MIN_SUBS: continue      # eligibility from the count at the freeze, not after
        steps = []
        for i in range(1, len(v)):
            (ta, sa), (tb, sb) = v[i - 1], v[i]
            hh = (tb - ta).total_seconds() / 3600
            if 6 <= hh <= 18: steps.append((ta, tb, 100 * math.log(sb / sa) * 12 / hh))
        for j, (ta, tb, y) in enumerate(steps):
            if not (start <= tb < end): continue
            norm = [s[2] for s in steps if tb - timedelta(days=NORM_DAYS) <= s[1] < ta]
            if len(norm) < 10: continue
            med = st.median(norm); mad = st.median(abs(x - med) for x in norm) * 1.4826
            if mad == 0: continue                      # counter flat in its own norm: no signal
            z = max(-WINSOR, min(WINSOR, (y - med) / max(mad, MAD_FLOOR)))
            key = round((tb.timestamp() / 3600 - 3.67) / 12)          # 12-h bins centred on the 03:40/15:40 slots
            w1 = EPOCH + timedelta(hours=key * 12 + 3.67) - timedelta(hours=12 * lag); w0 = w1 - timedelta(hours=12)
            rows.append([(iso, h), key, z, iso, (w0, w1)])
    cache = {}
    out = []
    for r in rows:
        k = r[4]
        if k not in cache: cache[k] = alert_hours(snaps, *k, **kw)
        if cache[k] is None: continue
        out.append((r[0], r[1], r[2], r[3], cache[k]))
    return out


def demean(v, ci, wi, tol=1e-12):
    for _ in range(500):
        big = 0.0
        for g in (ci, wi):
            s, n = collections.defaultdict(float), collections.Counter(g)
            for a, b in zip(g, v): s[a] += b
            for i in range(len(v)):
                d = s[g[i]] / n[g[i]]; v[i] -= d; big = max(big, abs(d))
        if big < tol: return v
    raise RuntimeError('demeaning did not converge')


_Y = {}


def beta(rows, hours_of):
    """two-way demeaned OLS slope of z on hours (alternating projections to tolerance)."""
    ci = [r[0] for r in rows]; wi = [r[1] for r in rows]
    if id(rows) not in _Y: _Y[id(rows)] = demean([r[2] for r in rows], ci, wi)
    y = _Y[id(rows)]; x = demean([hours_of(r) for r in rows], ci, wi)
    sxx = sum(a * a for a in x)
    return sum(a * b for a, b in zip(x, y)) / sxx if sxx else float('nan')


def perm_windows(rows, rng, n):
    """second null: keep each window's cross-regional pattern, shuffle which window it belongs to."""
    H = {r[1]: r[4] for r in rows}; W = sorted(H); out = []
    for _ in range(n):
        pw = dict(zip(W, rng.sample(W, len(W))))
        out.append(beta(rows, lambda r, pw=pw: H[pw[r[1]]].get(r[3], 0.0)))
    return out


def pval(b, null):
    return (1 + sum(abs(v) >= abs(b) for v in null)) / (1 + len(null))


def perm(rows, isos, rng, n):
    out = []
    for _ in range(n):
        m = dict(zip(isos, rng.sample(isos, len(isos))))
        out.append(beta(rows, lambda r, m=m: r[4].get(m[r[3]], 0.0)))
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--placebo'
    if not FREEZE: sys.exit('FREEZE not set: the prereg is not frozen yet')
    start, end = P(FREEZE), P(END)
    if mode == '--final' and datetime.now(timezone.utc) < end:
        sys.exit(f'confirmatory run refused before {END}')
    ser, snaps = load_census(), load_alerts()
    rows = panel(ser, snaps, start, min(end, datetime.now(timezone.utc)))
    if not rows: sys.exit('no rows in the test period yet')
    isos = sorted({r[3] for r in rows}); rng = random.Random(SEED)
    print(f'channels {len({r[0] for r in rows})}, windows {len({r[1] for r in rows})}, rows {len(rows)}')
    n = N_PERM if mode == '--final' else 300
    null = perm(rows, isos, rng, n)
    sd = st.pstdev(null); print(f'region-permutation null: sd {sd:.4f} z/alert-hour, 95% band ±{1.96*sd:.4f}')
    print(f'MDE (2.8 x SD rule, two-sided 5%, 80% power) ≈ {2.8*sd:.4f} z per alert-hour '
          f'≈ {2.8*sd*0.012*12:.4f} % subscribers per fully alerted 12-h window for a median-noise channel')
    if mode == '--placebo': print('placebo: no real exposure-outcome join computed'); return
    b = beta(rows, lambda r: r[4].get(r[3], 0.0)); nullw = perm_windows(rows, rng, n)
    print(f'PRIMARY beta {b:.4f} z per alert-hour; two-sided p region-perm {pval(b, null):.4f}, '
          f'window-perm {pval(b, nullw):.4f} (support needs beta>0 and both < 0.05)')
    rl = panel(ser, snaps, start, end, lag=1)
    print(f'secondary (a) lag 1: beta {beta(rl, lambda r: r[4].get(r[3], 0.0)):.4f}, '
          f'p region-perm {pval(beta(rl, lambda r: r[4].get(r[3], 0.0)), perm(rl, sorted({r[3] for r in rl}), rng, n)):.4f}')
    rm = panel(ser, snaps, start, end, types=('m', 'b'))
    bm = beta(rm, lambda r: r[4].get(r[3], 0.0))
    print(f'secondary (b) missile-only: beta {bm:.4f}, p region-perm {pval(bm, perm(rm, sorted({r[3] for r in rm}), rng, n)):.4f}')
    rc = [r for r in rows if r[3] not in BORDER]; bc = beta(rc, lambda r: r[4].get(r[3], 0.0))
    print(f'secondary (c) without Kursk/Bryansk/Belgorod: beta {bc:.4f}, '
          f'p region-perm {pval(bc, perm(rc, sorted({r[3] for r in rc}), rng, n)):.4f}')
    rs = panel(ser, snaps, start, end, stale_ok=False); bs = beta(rs, lambda r: r[4].get(r[3], 0.0))
    print(f'secondary (d) stale-as-absent: beta {bs:.4f}')


if __name__ == '__main__':
    main()
