#!/usr/bin/env python3
"""Counterfactual: rebuild the 16.10 Chaos Pulse from the 05.10 start keeping only moves the stated rule allows.
Labels from two blind classifiers (labels_mine.json by me, labels_fable.json by Claude Fable 5.1), moves from moves.jsonl.
  A: keep STATE moves still active on 16.10 (drop incidents, ended states, reversals)
  B: A + incident moves from the last 7 days (an incident's weight lasts a week)
"""
import json, os
W = {"military": .30, "energy": .25, "economy": .20, "institutions": .15, "restraint": .10}
start = json.loads(open(os.environ.get("PULSE_DIR", "pulse") + "/history.jsonl").readline())["components"]
mv = [json.loads(l) for l in open("moves.jsonl")]
def index(c): return sum(W[k] * c[k] for k in W)
def run(labels, recent_incidents):
    c = dict(start)
    for m, l in zip(mv, labels):
        keep = l["label"] == "STATE" and l["active"] is not False
        if recent_incidents and l["label"] == "INCIDENT" and m["report"] >= "2026-10-10": keep = True
        if keep: c[m["comp"]] += m["delta"]
    return c
actual = dict(start)
for m in mv: actual[m["comp"]] += m["delta"]
print(f"start 05.10: {index(start):.1f}   actual 16.10: {index(actual):.1f}  {actual}")
for name in ("mine", "fable"):
    lab = json.load(open(f"labels_{name}.json"))
    for v, ri in (("A", False), ("B", True)):
        c = run(lab, ri)
        print(f"{name:5s} {v}: {index(c):.1f}  " + " ".join(f"{k[:4]}={c[k]}" for k in W))

# path over time: actual vs counterfactuals (mean of the two classifiers), chart ratchet.png
import datetime as dt
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
dates = sorted({m["report"] for m in mv})
labs = [json.load(open(f"labels_{n}.json")) for n in ("mine", "fable")]
def path(variant):
    out = []
    for d in dates:
        vals = []
        for lab in (labs if variant else labs[:1]):
            c = dict(start)
            for m, l in zip(mv, lab):
                if m["report"] > d: continue
                if variant is None: keep = True
                else:
                    keep = l["label"] == "STATE" and l["active"] is not False
                    age = (dt.date.fromisoformat(d) - dt.date.fromisoformat(m["report"])).days
                    if variant == "B" and l["label"] == "INCIDENT" and age < 7: keep = True
                if keep: c[m["comp"]] += m["delta"]
            vals.append(index(c))
        out.append(sum(vals) / len(vals))
    return out
X = [dt.date.fromisoformat("2026-10-05")] + [dt.date.fromisoformat(d) for d in dates]
fig, ax = plt.subplots(figsize=(8, 4.2))
for v, lab, col, ls in ((None, "as published", "#b2182b", "-"), ("B", "incidents count for 7 days", "#ef8a62", "--"), ("A", "lasting states only", "#4d4d4d", ":")):
    y = [index(start)] + path(v)
    ax.plot(X, y, ls, color=col, lw=2.4, label=lab); ax.annotate(f"{y[-1]:.1f}", (X[-1], y[-1]), xytext=(4, -3), textcoords="offset points", color=col)
ax.set_ylabel("Chaos Pulse (0-100)"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_title("Up to half the climb: one-off incidents scored as lasting state", loc="left")
ax.legend(frameon=False, loc="upper left"); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig("ratchet.png", dpi=130)
print("path A", [round(v, 1) for v in path("A")]); print("path B", [round(v, 1) for v in path("B")])
