import json, random, glob, os
rng = random.Random(353); out = []
for f in sorted(glob.glob("data_v2/*.jsonl")):
    ch = os.path.basename(f)[:-6]; P = [json.loads(l) for l in open(f)]
    P = [p for p in P if len((p.get("text") or "").strip()) >= 30]
    score = lambda p: sum(p.get("reacts", {}).get(e, 0) for e in "😱🤬😢😡") / max(p.get("views") or 1, 1)
    top = sorted(P, key=score, reverse=True)[:max(len(P) // 4, 6)]
    r = rng.sample(P, 6); ids = {p["id"] for p in r}
    t = rng.sample([p for p in top if p["id"] not in ids], 6)
    out += [(ch, p["id"], "rand", p["text"]) for p in r] + [(ch, p["id"], "react", p["text"]) for p in t]
rng.shuffle(out)
with open("sample.tsv", "w") as f:
    for i, (ch, pid, stratum, txt) in enumerate(out):
        f.write("%d\t%s\t%s\t%s\t%s\n" % (i, ch, pid, stratum, " ".join(txt.split())[:700]))
print(len(out))
