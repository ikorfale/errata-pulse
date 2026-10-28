"""Agreement between my blind labels (labels.tsv) and an independent second labeler (labels_fable.tsv, Claude Fable 5.1,
same rules, texts only). Per category: both/only-me/only-fable counts and Cohen's kappa; then dict_v1 scored against the
consensus (posts where both agree), so a labeler's quirk can't make the dictionary look better or worse."""
import csv
from dict_v1 import tag, CATS
rd = lambda f: {r[0]: set() if r[1].strip() == "-" else {x.strip() for x in r[1].split(",")} for r in csv.reader(open(f), delimiter="\t")}
A, B = rd("labels.tsv"), rd("labels_fable.tsv"); S = {r[0]: r[4] for r in csv.reader(open("sample.tsv"), delimiter="\t")}
assert set(A) == set(B) == set(S), (len(A), len(B))
n = len(A); print("cat          both me_only fable_only  kappa | dict vs consensus: n tp fp fn")
for c in CATS:
    a = [c in A[i] for i in A]; b = [c in B[i] for i in A]
    both = sum(x and y for x, y in zip(a, b)); ma = sum(x and not y for x, y in zip(a, b)); mb = sum(y and not x for x, y in zip(a, b))
    po = sum(x == y for x, y in zip(a, b)) / n; pa, pb = sum(a) / n, sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb)
    k = "%.2f" % ((po - pe) / (1 - pe)) if pe < 1 else "  -"
    cons = [i for i in A if (c in A[i]) == (c in B[i])]
    tp = sum(c in A[i] and c in tag(S[i]) for i in cons); fp = sum(c not in A[i] and c in tag(S[i]) for i in cons); fn = sum(c in A[i] and c not in tag(S[i]) for i in cons)
    print("%-12s %4d %7d %10d  %5s | %d %d %d %d" % (c, both, ma, mb, k, len(cons), tp, fp, fn))
print("posts with any label: me %d, fable %d, either %d" % (sum(bool(v) for v in A.values()), sum(bool(v) for v in B.values()), sum(bool(A[i] or B[i]) for i in A)))
