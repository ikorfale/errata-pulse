"""maya_bombaya (Moltbook, 11.10): a power row. Plant k shared events into the real October month: on each of
k random days, m random families get that day lifted to the top of their month (just above their current maximum),
so each planted day is a sure top-3 day for those families: the smallest chord the rank statistics can see.
(A first version bumped by s x SD; the families are spiky, so even 3 SD bumps mostly stayed outside the top 3 —
see bump_share below.) Then run the two
secondary statistics with the circular null (which agreed with IAAFT to ~0.01 on this month, iaaft-*-2026-10-10.txt)
and count how often p < 0.05. Run from repo root: CARRIED=1 NOCLIP=1 python3 sonify/power_planted.py <signals file>."""
import os, sys, numpy as np
os.environ.setdefault("CARRIED", "1")
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import iaaft_null as I
C, M0 = I.C, I.M
rng = np.random.default_rng(1111)
NPLANT, NNULL = int(os.environ.get("NPLANT", 60)), int(os.environ.get("NNULL", 300))
sd = np.array([np.nanstd(np.where(np.isfinite(r), r, np.nan)) for r in M0])

def plant(k, m):
    M = M0.copy(); n = M.shape[1]
    for t in rng.choice(n, k, replace=False):
        for i in rng.choice(len(M), m, replace=False):
            if np.isfinite(M[i, t]): M[i, t] = np.nanmax(np.where(np.isfinite(M[i]), M[i], np.nan)) + 1e-6  # unknown stays unknown
    return M

def bump_share(s, n=2000):   # how often a random known day bumped by s SD enters its family's top 3
    hit = 0
    for _ in range(n):
        i = rng.integers(len(M0)); t = rng.integers(M0.shape[1])
        if not np.isfinite(M0[i, t]): continue
        r = M0[i].copy(); r[t] += s * sd[i]; hit += I.top3(r)[t] and not I.top3(M0[i])[t]
    return hit / n

def pval(fn, M):
    real = fn(M); null = np.array([fn(C.circ(M)) for _ in range(NNULL)])
    return (1 + (null >= real).sum()) / (NNULL + 1)

print(f'families {len(M0)}, days {M0.shape[1]}, known share {np.isfinite(M0).mean():.2f}; plants per cell {NPLANT}, null draws {NNULL}')
print(f'unplanted month: strict p={pval(I.chord_days, M0):.3f}, events p={pval(I.event_chords, M0):.3f}')
for s in (1, 2, 3):
    print(f'a {s} SD bump on a random known day newly enters that family top 3 in {bump_share(s):.2f} of cases', flush=True)
for m in (3, 4):
    for k in (1, 2, 3):
        ps = np.array([[pval(fn, Mp) for fn in (I.chord_days, I.event_chords)] for Mp in (plant(k, m) for _ in range(NPLANT))])
        print(f'{k} planted shared peak day(s), {m} of 6 families each: power strict {(ps[:,0] < .05).mean():.2f}, events {(ps[:,1] < .05).mean():.2f}', flush=True)
