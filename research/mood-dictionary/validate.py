"""Score frozen dict_v1 against the blind labels (labels.tsv) on sample.tsv. Prints per-category TP/FP/FN, precision, recall,
with the stratum split (rand vs react) and every disagreement, so each number can be checked by hand."""
import csv, sys
from dict_v1 import tag, CATS
S = {r[0]: r for r in csv.reader(open("sample.tsv"), delimiter="\t")}
L = {r[0]: set() if r[1] == "-" else set(r[1].split(",")) for r in csv.reader(open("labels.tsv"), delimiter="\t")}
assert set(S) == set(L) and len(S) == 120
print("cat          gold  tp  fp  fn  precision  recall   (gold in rand/react)")
dis = []
for c in CATS:
    tp = fp = fn = 0; g = {"rand": 0, "react": 0}
    for i, r in S.items():
        h, y = c in tag(r[4]), c in L[i]
        g[r[3]] += y; tp += h and y; fp += h and not y; fn += y and not h
        if h != y: dis.append((c, "FP" if h else "FN", i, r[1], r[4][:110]))
    p = "%.2f" % (tp / (tp + fp)) if tp + fp else "  -"; rc = "%.2f" % (tp / (tp + fn)) if tp + fn else "  -"
    print("%-12s %4d %3d %3d %3d  %9s  %6s   (%d/%d)" % (c, tp + fn, tp, fp, fn, p, rc, g["rand"], g["react"]))
print("posts with any gold label: %d of 120" % sum(bool(v) for v in L.values()))
for d in dis: print(*d, sep=" | ")
