"""#113349 (glitchfox): does centred U beat the median difference because it uses every A-B pair (then the
Hodges-Lehmann median over all B-A pairs should match U) or because it is scale-free per family (then a log-scale
median difference should match U)? Note: in paired_power_u.py the 'med' column was ALREADY on log heal (g holds
math.log(heal)), so 'log med' = 'med' there. Two extra columns here: HL over all pairs (log scale), and the log median
difference divided by the family's pooled log sd (the pooled sd does not change under the within-family reshuffle, so
the null symmetry is the same as med's), and U/(nA*nB): if U wins by
weighting families with more pairs (its magnitude grows with nA*nB), the normalised U should lose that power. Same families, null, B times r, exact signed-rank decision and seed as
paired_power_u.py, all five statistics on the SAME reshuffled datasets, 1000 per cell, min 1 episode per side.
Written 2026-11-04 (date -u). Run: python3 paired_power_hl.py > resolved/paired_power_hl.txt"""
import sys, math; sys.argv = ['x']
import numpy as np
exec(open('paired_power_wsr.py').read().split("rng = np.random")[0])
exec('def wsr_p' + open('paired_power_wsr.py').read().split('def wsr_p')[1].split('def power')[0])
rng = np.random.default_rng(113344); ND = 1000
def cu(A, B):
    d = B[:, None] - A[None, :]; return (d > 1e-12).sum() + 0.5 * (np.abs(d) <= 1e-12).sum() - len(A) * len(B) / 2
def run(fams, r):
    h = np.zeros(5)
    for _ in range(ND):
        D = [[], [], [], [], []]
        for a, bb in fams:
            pool = rng.permutation(np.r_[a, bb]); A, B = pool[:len(a)], pool[len(a):] + math.log(r)
            s = np.std(np.r_[a, bb]) or 1.0
            md = np.median(B) - np.median(A)
            D[0].append(md); D[1].append(cu(A, B)); D[2].append(np.median((B[:, None] - A[None, :]).ravel())); D[3].append(md / s); D[4].append(D[1][-1] / (len(A) * len(B)))
        for j in range(5): h[j] += wsr_p(np.array(D[j], float))[0] < 0.05
    return h / ND
print(f'ND={ND} per cell, MC SE ~0.007 at 0.05, ~0.015 at 0.3. All on log heal. med = median diff, U = centred MW U,')
print('HL = median of all B-A pairs, med/sd = median diff over the family pooled sd (sd from unshifted data),\nU/nn = centred U divided by nA*nB (same sign, no weight for family size)')
print('boundary          fams   FP: med   U     HL   med/sd U/nn  |  x2: med   U     HL   med/sd U/nn  | sd of family log sd')
for i in range(4):
    fams = [(np.array(v[i]), np.array(v[i + 1])) for v in g.values() if len(v.get(i, [])) >= 1 and len(v.get(i + 1, [])) >= 1]
    sds = [np.std(np.r_[a, bb]) for a, bb in fams]
    o0, o2 = run(fams, 1), run(fams, 2)
    print(f'{BINS[i][2]:>7} | {BINS[i+1][2]:<8} {len(fams):>3}   ' + ' '.join(f'{x:.3f}' for x in o0) + ' | '
          + ' '.join(f'{x:.3f}' for x in o2) + f' | {np.std(sds):.2f} (median {np.median(sds):.2f})', flush=True)
