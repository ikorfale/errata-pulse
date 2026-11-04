"""#113344 (glitchfox): per-family centred Mann-Whitney U (U_B - nA*nB/2, ties 0.5) is exactly sign-symmetric under the
within-family reshuffle for any counts; the median difference is not. Same families, null, B times r and exact
signed-rank decision (p<0.05, zeros dropped and counted) as paired_power_wsr.py; both statistics computed on the SAME
reshuffled datasets, 1000 per cell, seed 113344. Extra row 'A<B only': families with fewer episodes on side A, where
the median-difference leans should not cancel. Written 2026-11-04 (date -u).
Run: python3 paired_power_u.py > resolved/paired_power_u.txt"""
import sys, math; sys.argv = ['x']
import numpy as np
exec(open('paired_power_wsr.py').read().split("rng = np.random")[0])
exec('def wsr_p' + open('paired_power_wsr.py').read().split('def wsr_p')[1].split('def power')[0])
rng = np.random.default_rng(113344); ND = 1000
def cu(A, B):
    d = B[:, None] - A[None, :]; return (d > 1e-12).sum() + 0.5 * (np.abs(d) <= 1e-12).sum() - len(A) * len(B) / 2
def run(fams, r):
    hm = hu = zm = zu = 0
    for _ in range(ND):
        dm, du = [], []
        for a, bb in fams:
            pool = rng.permutation(np.r_[a, bb]); A, B = pool[:len(a)], pool[len(a):] + math.log(r)
            dm.append(np.median(B) - np.median(A)); du.append(cu(A, B))
        pm, nm = wsr_p(np.array(dm)); pu, nu = wsr_p(np.array(du, float))
        hm += pm < 0.05; hu += pu < 0.05; zm += len(dm) - nm; zu += len(du) - nu
    return hm / ND, hu / ND, zm / ND, zu / ND
print(f'ND={ND} per cell, MC SE ~0.007 at 0.05, ~0.015 at 0.3. med = median difference, U = centred Mann-Whitney U')
print('boundary          min eps  fams   FP med  FP U   x2 med  x2 U   x3 med  x3 U   zeros/fam med  U')
for i in range(4):
    for k, sub in ((1, 'all'), (3, 'all'), (1, 'A<B only')):
        fams = [(np.array(v[i]), np.array(v[i + 1])) for v in g.values() if len(v.get(i, [])) >= k and len(v.get(i + 1, [])) >= k]
        if sub != 'all': fams = [(a, bb) for a, bb in fams if len(a) < len(bb)]
        if len(fams) < 5: print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {k:>3} {sub:>8} {len(fams):>3}  -'); continue
        o = [run(fams, r) for r in (1, 2, 3)]
        print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {k:>3} {sub:>8} {len(fams):>3}  ' + '  '.join(f'{x[0]:.3f}  {x[1]:.3f}' for x in o)
              + f'   {o[0][2]/len(fams):.2f}  {o[0][3]/len(fams):.2f}', flush=True)
