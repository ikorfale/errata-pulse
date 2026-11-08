"""ollybloom (Moltbook, 08.11): on the same masked October month, compare an EVENT-COUNT null with a MATCHED RUN-LENGTH null,
to separate "more chord events than chance" from "events clustering into longer perceptual bursts".
Both nulls act on each family's binary top-3 strip over its known days (unmeasured days stay unknown = never in the top 3,
CARRIED=1 masking as in iaaft_null.py), break alignment between families, and keep:
  event-count null : the family's number of events, each re-placed as a SINGLE day uniformly among its known days
                     (widths destroyed; only its chord-events row is meaningful, chord days and bursts are degenerate);
  run-length null  : the family's multiset of event widths and of gap lengths, in shuffled order, segments rotated by a
                     random number of segments so runs never split (widths kept, positions and alignment broken).
Statistics: chord days (days with >=3 families in their top 3), chord events (>=3 families starting an event within +-1 day,
overlapping windows merged), longest burst (max consecutive chord days).
Run from repo root: python3 sonify/runlen_null.py <path to pulse/signals/2026-10-08.json (the work dir copy)>"""
import os, sys, io, contextlib, numpy as np
os.environ.setdefault("CARRIED", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with contextlib.redirect_stdout(io.StringIO()):
    import chord_null as C
import iaaft_null as I
M, F, days = C.M, C.F, C.days
rng = np.random.default_rng(1108)
T = np.vstack([I.top3(r) for r in M]); known = np.isfinite(M)

def chord_days(T): return int((T.sum(0) >= 3).sum())
def burst(T):
    c = T.sum(0) >= 3; best = cur = 0
    for v in c: cur = cur + 1 if v else 0; best = max(best, cur)
    return int(best)
def event_chords(T, tol=1):
    S = np.hstack([T[:, :1], T[:, 1:] & ~T[:, :-1]]); n = S.shape[1]
    near = np.vstack([[S[i, max(0, t - tol):t + tol + 1].any() for t in range(n)] for i in range(len(S))])
    c = near.sum(0) >= 3
    return int(c[0] + (c[1:] & ~c[:-1]).sum())
def segments(s):
    out = []; 
    for v in s:
        if out and out[-1][0] == v: out[-1][1] += 1
        else: out.append([v, 1])
    return out
def runlen_strip(s):
    seg = segments(s)
    ones = [l for v, l in seg if v]; zeros = [l for v, l in seg if not v]
    rng.shuffle(ones); rng.shuffle(zeros); io_ = iter(ones); iz = iter(zeros)
    new = [[v, next(io_) if v else next(iz)] for v, _ in seg]
    k = rng.integers(len(new)); new = new[k:] + new[:k]
    return np.concatenate([np.full(l, bool(v)) for v, l in new])
def null_runlen(T):
    out = np.zeros_like(T)
    for i in range(len(T)):
        kd = np.where(known[i])[0]
        if kd.size == 0 or not T[i, kd].any(): continue
        out[i, kd] = runlen_strip(T[i, kd])
    return out
def null_count(T):
    out = np.zeros_like(T)
    for i in range(len(T)):
        kd = np.where(known[i])[0]; s = T[i, kd]
        n = int(s[0]) + int((s[1:] & ~s[:-1]).sum()) if s.size else 0
        if n: out[i, rng.choice(kd, n, replace=False)] = True
    return out

if __name__ == "__main__":
    N = 2000
    stats = [("chord days", chord_days), ("chord events (+-1 day)", event_chords), ("longest burst (days)", burst)]
    print("families:", F, "| known days per family:", known.sum(1).tolist(), "| top-3 days per family:", T.sum(1).tolist())
    print("event widths per family:", {f: [l for v, l in segments(T[i, known[i]]) if v] for i, f in enumerate(F)})
    draws = {"run-length null": [null_runlen(T) for _ in range(N)], "event-count null": [null_count(T) for _ in range(N)]}
    for name, fn in stats:
        real = fn(T); line = f"{name:24s}: real {real}"
        for nn, D in draws.items():
            v = np.array([fn(x) for x in D]); p = (1 + (v >= real).sum()) / (N + 1)
            line += f" | {nn} mean {v.mean():.2f} sd {v.std():.2f} p={p:.3f}"
        print(line + f"  (N={N}, seed 1108)")
    print("=== end")
