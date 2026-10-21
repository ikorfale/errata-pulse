"""PREREG-fom-strikes v1.1 primary test: spaced label permutation (plan #396).
Units: wave positions (index in the FOM series) with their stat2 values; n of them are treatment waves.
Null: every choice of n units with no two closer than GAP waves (|i - j| >= GAP; GAP = 3 keeps a treatment wave out of
another's 2-wave baseline, as in mde_sim.py), uniformly. Statistic: mean(chosen) - mean(rest), one-sided.
If the number of admissible choices is < ENUM_MAX, all are enumerated; otherwise DRAWS are sampled exactly uniformly by
dynamic programming over positions (no rejection, no draw can fail).
usage: python3 perm_test.py --selftest      (DP count vs brute force, sampler uniformity, p-value on toy data)"""
import itertools, sys, numpy as np
GAP, ENUM_MAX, DRAWS = 3, 200_000, 20_000

def count_table(pos, n, gap=GAP):
    """C[i][k] = number of admissible k-subsets of units i..end (units sorted by position)."""
    m = len(pos); nxt = [next((j for j in range(i + 1, m) if pos[j] - pos[i] >= gap), m) for i in range(m)]
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m, -1, -1): C[i][0] = 1
    for i in range(m - 1, -1, -1):
        for k in range(1, n + 1): C[i][k] = C[i + 1][k] + C[nxt[i]][k - 1]
    return C, nxt

def enumerate_all(pos, n, gap=GAP):
    out = []
    def rec(i, k, cur):
        if k == 0: out.append(tuple(cur)); return
        for j in range(i, len(pos)):
            if not cur or pos[j] - pos[cur[-1]] >= gap: rec(j + 1, k - 1, cur + [j])
    rec(0, n, []); return out

def sample(pos, n, rng, C, nxt):
    """One admissible k-subset, exactly uniform: at unit i, take it with prob C[nxt[i]][k-1] / C[i][k]."""
    i, k, out = 0, n, []
    while k:
        if rng.random() * C[i][k] < C[nxt[i]][k - 1]: out.append(i); i = nxt[i]; k -= 1
        else: i += 1
    return tuple(out)

def perm_test(pos, val, treated, gap=GAP, seed=396):
    """pos: sorted wave positions of all units; val: stat2 per unit; treated: indices into pos. Returns a dict."""
    pos, val = list(pos), np.asarray(val, float); n = len(treated); tot = val.sum(); m = len(pos)
    stat = lambda S: val[list(S)].mean() - (tot - val[list(S)].sum()) / (m - n)
    for a, b in zip(sorted(treated), sorted(treated)[1:]): assert pos[b] - pos[a] >= gap, 'treatment waves violate the spacing'
    C, nxt = count_table(pos, n, gap); total = C[0][n]
    if total < ENUM_MAX: null = np.array([stat(S) for S in enumerate_all(pos, n, gap)]); mode = 'enumerated'
    else:
        rng = np.random.default_rng(seed); null = np.array([stat(sample(pos, n, rng, C, nxt)) for _ in range(DRAWS)]); mode = f'{DRAWS} uniform draws'
    obs = stat(treated); p = float((null >= obs - 1e-12).mean())
    q05, q20, q95 = np.percentile(null, [5, 20, 95])
    return dict(n=n, units=m, relabellings=total, mode=mode, obs=obs, p=p, upper95=obs - q05, mde80=q95 - q20, null_sd=null.std())

def selftest():
    rng = np.random.default_rng(1)
    for trial in range(30):  # DP count == brute force
        m = rng.integers(6, 14); pos = sorted(rng.choice(40, m, replace=False)); n = int(rng.integers(1, 4))
        brute = sum(all(b - a >= GAP for a, b in zip(S, S[1:])) for S in itertools.combinations(pos, n))
        assert count_table(pos, n)[0][0][n] == brute == len(enumerate_all(pos, n)), (pos, n)
    pos = list(range(12)); n = 3; C, nxt = count_table(pos, n); allS = enumerate_all(pos, n)
    freq = {S: 0 for S in allS}; R = 200_000
    for _ in range(R): freq[sample(pos, n, rng, C, nxt)] += 1
    exp = R / len(allS); chi2 = sum((f - exp) ** 2 / exp for f in freq.values())
    print(f"selftest: DP count = brute force on 30 random cases; sampler over {len(allS)} subsets of 12 positions: chi2 {chi2:.1f} on {len(allS) - 1} df")
    assert chi2 < 2 * len(allS), 'sampler not uniform'
    val = rng.normal(0, 2.7, 60); pos = list(range(60)); tr = [5, 15, 25, 35, 45]
    r0 = perm_test(pos, val, tr); val2 = val.copy(); val2[tr] += 5; r1 = perm_test(pos, val2, tr)
    print(f"toy null: p {r0['p']:.3f} ({r0['mode']}, {r0['relabellings']} relabellings); toy +5 pts: p {r1['p']:.4f}, MDE80 {r1['mde80']:.2f}")
    assert r1['p'] < 0.05

if __name__ == '__main__' and '--selftest' in sys.argv: selftest()
