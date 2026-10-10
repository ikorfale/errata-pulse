"""maya_bombaya (Moltbook, 10.10): (1) count family EVENTS (runs of top-3 days) and ask how often >=3 families
START an event within +-1 day; (2) use IAAFT surrogates (keep each voice's autocorrelation and value
distribution, break alignment) instead of circular shifts. Reuses chord_null.py voices (CARRIED=1 masking). Run from repo root: [NOCLIP=1] python3 sonify/iaaft_null.py <signals file>."""
import os, sys, numpy as np
os.environ.setdefault("CARRIED", "1")
sys.argv = sys.argv[:1] + sys.argv[1:]
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import chord_null as C      # builds C.M (families x 30 days), -inf = unmeasured day
M, F, days = C.M, C.F, C.days
rng = np.random.default_rng(1010)

def iaaft(x, it=200):
    """Schreiber & Schmitz 1996: match amplitude spectrum and value distribution."""
    amp = np.abs(np.fft.rfft(x)); srt = np.sort(x); y = rng.permutation(x)
    for _ in range(it):
        ph = np.angle(np.fft.rfft(y)); y = np.fft.irfft(amp * np.exp(1j * ph), n=len(x))
        y = srt[np.argsort(np.argsort(y))]
    return y

def surrogate(M):
    out = []
    for r in M:
        ok = np.isfinite(r); s = r.copy()
        s[ok] = iaaft(r[ok])        # unmeasured days stay where they are, unknown
        out.append(s)
    return np.vstack(out)

def top3(r): return r >= np.sort(r[np.isfinite(r)])[-3]
def starts(M):
    T = np.vstack([top3(r) for r in M])
    return np.hstack([T[:, :1], T[:, 1:] & ~T[:, :-1]])   # first day of each run = event start
def chord_days(M):     # strict ranks, as in the post
    return int((np.vstack([top3(r) for r in M]).sum(0) >= 3).sum())
def event_chords(M, tol=1):
    S = starts(M); n = S.shape[1]
    near = np.vstack([[S[i, max(0, t - tol):t + tol + 1].any() for t in range(n)] for i in range(len(S))])
    c = near.sum(0) >= 3
    return int(c[0] + (c[1:] & ~c[:-1]).sum())   # windows that merge count once

S = starts(M)
print('events per family:', {f: [days[t] for t in np.where(S[i])[0]] for i, f in enumerate(F)})
N = 2000
for name, fn in [('strict ranks (days)', chord_days), ('event starts within +-1 day', event_chords)]:
    real = fn(M)
    null = np.array([fn(surrogate(M)) for _ in range(N)])
    circ = np.array([fn(C.circ(M)) for _ in range(N)])
    p = (1 + (null >= real).sum()) / (N + 1); pc = (1 + (circ >= real).sum()) / (N + 1)
    print(f'{name:30s}: real {real} | IAAFT null mean {null.mean():.2f}, p={p:.3f} | circular null mean {circ.mean():.2f}, p={pc:.3f}  (N={N})')
