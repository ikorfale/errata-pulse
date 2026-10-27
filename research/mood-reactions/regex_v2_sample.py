"""PREREG-v2 classifier check: 50 posts drawn at random (seed 20261027) from data_v2, text only (reactions never printed).
Hand labels go in regex_v2_labels.tsv; regex_v2_check.py compares them with the frozen regex."""
import json, glob, random
rows = []
for f in sorted(glob.glob("data_v2/*.jsonl")):
    for l in open(f, encoding="utf-8"):
        d = json.loads(l)
        if d.get("text", "").strip(): rows.append((f.split("/")[-1][:-6], d["id"], d["text"]))
random.Random(20261027).shuffle(rows)
for ch, i, t in rows[:50]: print(f"{ch}\t{i}\t{' '.join(t.split())[:260]}")
