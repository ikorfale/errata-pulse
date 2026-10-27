"""Compare hand labels (regex_v2_labels.tsv) with the PREREG-v2 strike regex on the full text of the 50 sampled posts."""
import json, glob, re
FOOTER = re.compile(r'вс[юя] информаци[юя] (по|об) (атак|бпла)[^\n]*', re.I)
URL = re.compile(r'https?://\S+|\S+\.(?:ru|me|com)/\S*|@\w+')
def letters(t): return sum(ch.isalpha() for ch in URL.sub('', t))
STRIKE_V2 = re.compile(r'погиб|удар|бпла|беспилот|дрон|ракет|атак|обстрел|всу|ранен|траур|соболезн|пво|сирен|укрыти|взрыв|прил[её]т', re.I)
text = {}
for f in glob.glob("data_v2/*.jsonl"):
    for l in open(f, encoding="utf-8"):
        d = json.loads(l); text[(f.split("/")[-1][:-6], str(d["id"]))] = d.get("text", "")
sample = [l.split("\t")[:2] for l in open("regex_v2_sample.tsv", encoding="utf-8")]
lab = [l.rstrip("\n").split("\t")[1] for l in open("regex_v2_labels.tsv", encoding="utf-8") if not l.startswith("#")]
tp = fp = fn = tn = 0
for n, ((ch, i), y) in enumerate(zip(sample, lab), 1):
    t = FOOTER.sub("", text[(ch, i)]); m = STRIKE_V2.search(t)
    if letters(t) < 30 and not m: print(f"EMPTY #{n} {ch} {i} (label {y}): no strike word, under 30 letters: excluded from both cells"); continue
    if m and y == "S": tp += 1
    elif m: fp += 1; print(f"FP #{n} {ch} {i}: '{t[max(0,m.start()-25):m.end()+25]}'")
    elif y == "S": fn += 1; print(f"FN #{n} {ch} {i}")
    else: tn += 1
print("classified on text with the promo footer removed (PREREG-v2 amendment 27.10)"); print(f"n={len(lab)} TP {tp} FP {fp} FN {fn} TN {tn}")
