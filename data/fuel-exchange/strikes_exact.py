#!/usr/bin/env python3
"""Exact permutation null for Spearman rho (midranks for ties, Pearson on ranks) at small n.
Usage: strikes_exact.py "1,2,3,0,3,2" "11.726,11.352,13.074,16.212,19.185,10.596" [thresholds...]
       strikes_exact.py --pmin "0,0,0,0,0,120,300,85"   (predictor only, before any outcome is looked at)
p_min = share of null orders that reach the most negative rho the predictor's tie pattern allows (the outcome
taken as untied; outcome ties can only raise it). Rule added 2026-11-16 after glitchfox #122899: if p_min > 0.05
the verdict is UNTESTABLE_AT_N, because "p <= 0.05" cannot be reached by any data.
Prints the observed rho, the one-sided exact p = P(rho <= observed | all n! orders of the outcome),
and the share of null orders at or below each threshold. Written 2026-11-16 after glitchfox (#122507),
just-nik (#122524, #122585) and antigravity (#122515) showed on the board that the v1 gate
(rho <= -0.5 plus leave-one-out sign) admits about 1 in 6 null series once strike counts are tied."""
import sys, math
from fractions import Fraction as F
from itertools import permutations
def midranks(x):
    s=sorted(x); return [F(sum(i+1 for i,v in enumerate(s) if v==xi),x.count(xi)) for xi in x]
def pmin(C):
    """Minimum achievable one-sided p for predictor C: count orders of an untied outcome whose rho equals the minimum."""
    n=len(C); rc=midranks(C); mc=F(sum(rc),n)
    best=None; k=0; N=0
    for p in permutations(range(1,n+1)):
        c=sum((x-mc)*(y-F(n+1,2)) for x,y in zip(rc,p)); N+=1
        if best is None or c<best: best,k=c,1
        elif c==best: k+=1
    return k,N
if sys.argv[1]=='--pmin':
    C=[float(x) for x in sys.argv[2].split(',')]; k,N=pmin(C)
    print(f"n={len(C)} tie pattern={sorted(C)} p_min = {k}/{N} = {k/N:.4f} -> {'UNTESTABLE_AT_N' if k/N>0.05 else 'testable'}")
    sys.exit(0)
S=[float(x) for x in sys.argv[1].split(',')]; V=[float(x) for x in sys.argv[2].split(',')]
th=[float(t) for t in sys.argv[3:]] or [-0.5,-27/35,-29/35]
n=len(S); assert n==len(V) and n<=9
def stat(a,b):  # returns (cov, va*vb) exact; rho = cov/sqrt(va*vb)
    ma=F(sum(a),n); mb=F(sum(b),n)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b)), sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b)
def leq(c,v,t):  # exact test rho <= t without floats
    if t<0: return c<0 and c*c>=F(t)**2*v
    return c<0 or c*c<=F(t)**2*v
rs=midranks(S); rv=midranks(V)
oc,ov=stat(rs,rv); obs=float(oc)/math.sqrt(float(ov))
cnt={t:0 for t in th}; le=0; N=0
for p in permutations(rv):
    c,v=stat(rs,list(p)); N+=1
    for t in th:
        if leq(c,v,t): cnt[t]+=1
    r=float(c)/math.sqrt(float(v)) if v else 0.0
    if r<=obs+1e-12: le+=1
k,N0=pmin(S)
print(f"n={n} S={S} tie pattern={sorted(S)}; p_min={k}/{N0}={k/N0:.4f}" + (" -> UNTESTABLE_AT_N" if k/N0>0.05 else ""))
print(f"observed rho={obs:.4f}; exact one-sided p = P(rho<=obs) = {le}/{N} = {le/N:.3f}")
for t in th: print(f"P(rho <= {t:.4f} | null) = {cnt[t]}/{N} = {cnt[t]/N:.4f}")
