"""Exact Wilcoxon signed-rank by sign-flip enumeration over midranks, in integers only (2026-11-04, after glitchfox
113528/113534/113542/113557 and nadir-codex 113533/113541/113553 on ties). No float anywhere in the decision path.

- zeros (d == 0 exactly) are dropped and counted; n_nonzero == 0 -> p is undefined (None), never 1.
- ties in |d| are decided by exact equality (values converted with Fraction, so half-integer U values are exact);
  tied |d| get midranks, stored doubled so every rank is an integer.
- statistic: W = sum of doubled ranks of positive d. Null: all 2^n sign patterns, counted by integer DP.
- two-sided p = min(1, 2 * min(#{W' <= W}, #{W' >= W}) / 2^n), both tails inclusive (>=, <=).
- decision at alpha = 1/20 in integers: reject iff 20 * count2 <= 2^n (p is dyadic, so it never equals 0.05).
- attainable(): the set S of statistics some sign pattern reaches, for fixtures (targets must come from S).
Run: python3 wsr_exact.py  (self-tests)"""
from fractions import Fraction

def _ranks2(a):
    """doubled midranks for the list of positive Fractions a, same order as a"""
    order = sorted(range(len(a)), key=lambda i: a[i]); r2 = [0] * len(a); i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]: j += 1
        for k in order[i:j + 1]: r2[k] = i + j + 2   # 2 * ((i+1 + j+1) / 2)
        i = j + 1
    return r2

def null_counts(r2):
    """counts[w] = number of sign patterns with W == w (Python ints, exact)"""
    c = [0] * (sum(r2) + 1); c[0] = 1
    for v in r2:
        c = [c[w] + (c[w - v] if w >= v else 0) for w in range(len(c))]
    return c

def wsr(d):
    """returns dict: n_zero, n_nonzero, r2, W, lower, upper, total, p2 (Fraction or None)"""
    d = [Fraction(x) for x in d]; nz = [x for x in d if x != 0]; n = len(nz)
    out = {'n_zero': len(d) - n, 'n_nonzero': n}
    if n == 0: return {**out, 'p2': None, 'note': 'undefined: no nonzero values'}
    r2 = _ranks2([abs(x) for x in nz]); W = sum(r for r, x in zip(r2, nz) if x > 0)
    c = null_counts(r2); total = 2 ** n
    lower = sum(c[:W + 1]); upper = sum(c[W:])
    two = min(total, 2 * min(lower, upper))
    return {**out, 'r2': r2, 'W': W, 'lower': lower, 'upper': upper, 'total': total,
            'count2': two, 'p2': Fraction(two, total)}

def reject(res, alpha=Fraction(1, 20)):
    """p2 <= alpha, decided as integers: count2 * alpha.denominator <= alpha.numerator * total"""
    if res['p2'] is None: return None
    return res['count2'] * alpha.denominator <= alpha.numerator * res['total']

def attainable(absd):
    c = null_counts(_ranks2([Fraction(x) for x in absd]))
    return {w for w, k in enumerate(c) if k}

def attainable_size(n_or_absd, alpha=Fraction(1, 20)):
    """largest two-sided p <= alpha reachable for these |d| (the tied null, not the no-ties table)"""
    absd = list(range(1, n_or_absd + 1)) if isinstance(n_or_absd, int) else n_or_absd
    r2 = _ranks2([Fraction(x) for x in absd]); c = null_counts(r2); total = 2 ** len(r2); best = None; low = 0
    for w in range(len(c)):
        low += c[w]
        if c[w]:
            p = Fraction(min(total, 2 * low), total)   # lower tail; null is symmetric
            if p <= alpha and (best is None or p > best): best = p
    return best

if __name__ == '__main__':
    F = Fraction
    r = wsr([0, 0, 0]); assert r['p2'] is None and reject(r) is None
    r = wsr([3]); assert (r['upper'], r['total'], r['p2']) == (1, 2, 1)
    r = wsr([2, 2, 2, 2, -2, 2, 2, 1])                       # glitchfox 113528/113534
    assert r['upper'] == 9 and r['total'] == 256 and r['p2'] == F(18, 256), r
    r = wsr([1, -1, 2, -2, 3, -3]); assert r['upper'] == 36 and r['p2'] == 1, r
    r = wsr([1, 2, -3]); assert r['upper'] == 5 and r['total'] == 8, r   # T+ >= 3 gives 5/8
    r = wsr([-2, 1, 3, -1, -2]); assert r['lower'] == 21 or r['upper'] == 21, r   # floats gave 19/32
    assert attainable([1, 1, 2, 3]) == {0, 3, 6, 8, 9, 11, 12, 14, 17, 20}           # glitchfox 113557
    assert _ranks2([F(1), F(1), F(2), F(3)]) == [3, 3, 6, 8]
    # integer boundary at alpha 1/20, n=8: count 12 passes, 13 fails (113542)
    assert reject({'p2': F(12, 256), 'count2': 12, 'total': 256}) and not reject({'p2': F(13, 256), 'count2': 13, 'total': 256})
    for n in range(1, 21): assert F(1, 20) * 2 ** n != int(F(1, 20) * 2 ** n)   # p never equals 0.05 exactly
    assert attainable_size(6) == F(2, 64)                    # 113309: 0.031 at six families, no ties
    assert attainable_size(5) is None                         # five families cannot reject
    assert wsr([F(1, 2), F(-1, 2), F(3, 2)])['r2'] == [3, 3, 6]   # half-integer U ties are exact
    print('all tests pass')
