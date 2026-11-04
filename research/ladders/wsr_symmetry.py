# 2026-11-04: is the per-family difference sign-symmetric under the reshuffle null? Run from research/ladders.
# Is the per-family difference sign-symmetric under the within-family reshuffle null? (180-365 | >365, min 1 eps, 15 fams)
import sys; sys.argv=['x']
exec(open('paired_power_wsr.py').read().split("print('boundary")[0])
i=3
fams=[(np.array(v[i]),np.array(v[i+1])) for v in g.values() if len(v.get(i,[]))>=1 and len(v.get(i+1,[]))>=1]
rng2=np.random.default_rng(7)
print('families',len(fams))
skews=[]
for a,bb in fams:
    D=[]
    pool=np.r_[a,bb]
    for _ in range(4000):
        p=rng2.permutation(pool); D.append(np.median(p[len(a):])-np.median(p[:len(a)]))
    D=np.array(D); nz=D[np.abs(D)>1e-12]
    skews.append((len(a),len(bb),round(float(np.mean(D)),3),round(float((nz>0).mean()),3) if len(nz) else None))
for s in skews: print(s)
# FP with 4000 datasets
hits=0; N=4000
for _ in range(N):
    d=[]
    for a,bb in fams:
        pool=rng2.permutation(np.r_[a,bb]); d.append(np.median(pool[len(a):])-np.median(pool[:len(a)]))
    p,n=wsr_p(np.array(d)); hits+=p<0.05
print('FP r=1, 4000 datasets:',hits/N,'SE',round((hits/N*(1-hits/N)/N)**.5,4))
