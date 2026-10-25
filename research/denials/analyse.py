"""Descriptive comparison under PREREG.md (sha256 20f8d27d). Re-derivable: python3 analyse.py"""
import json, re, datetime as dt
D = lambda s: dt.date.fromisoformat(s)
WIN = {"2022": (D("2022-02-24"), D("2022-09-20")), "2026": (D("2026-06-01"), D("2026-10-25"))}
HEDGE = re.compile(r"на сегодня|сегодняшн|в настоящий момент|сейчас|пока|я думаю|насколько|по крайней", re.I)
NARROW = re.compile(r"всеобщ|массов|general|mass", re.I)
for y, (a, b) in WIN.items():
    rows = [json.loads(l) for l in open(f"ledger_{y}.jsonl")]
    den = [r for r in rows if r.get("type") != "trigger_only" and r.get("in_rule", True)]
    trig = [r for r in rows if r.get("type") == "trigger_only"]
    weeks = ((b - a).days + 1) / 7
    print(f"== {y}: window {a}..{b} ({weeks:.1f} weeks)")
    print(f"in-rule denials {len(den)} = {len(den)/weeks:.2f}/week; trigger-only rows {len(trig)}")
    print(f"triggered (not unprompted/unknown) {sum(r['trigger'] not in ('unprompted','unknown') for r in den)}/{len(den)}")
    # recode hedge and scope from the quote text, same rule for both helpers
    print(f"hedge words in quote {sum(bool(HEDGE.search(r['quote'])) for r in den)}/{len(den)}; "
          f"narrowed to general/mass {sum(bool(NARROW.search(r['quote'])) for r in den)}/{len(den)}")
    last = den[-1]["date"]
    print(f"last in-rule denial {last} ({den[-1]['speaker']}); later triggers: "
          + "; ".join(f"{t['date']} {t['what'][:50]}" for t in trig if t['date'] > last))
    for r in den[-4:]:
        print("  ", r["date"], r["speaker"][:22], "| hedge" if HEDGE.search(r["quote"]) else "| -", "| narrow" if NARROW.search(r["quote"]) else "| -", "|", r["quote"][:70])

# strict reading (review 25.10): drop rows whose verbatim quote has no explicit negation of mobilisation
NOT_EXPLICIT = {("2022", "2022-09-06"), ("2026", "2026-08-25"), ("2026", "2026-08-28")}
print("== strict reading (explicit negation in the quote)")
for y, (a, b) in WIN.items():
    den = [r for r in map(json.loads, open(f"ledger_{y}.jsonl")) if r.get("type") != "trigger_only" and r.get("in_rule", True)]
    strict = [r for r in den if (y, r["date"]) not in NOT_EXPLICIT]
    weeks = ((b - a).days + 1) / 7
    ds = [D(r["date"]) for r in strict]
    gaps = sorted(((ds[i+1] - ds[i]).days, str(ds[i]), str(ds[i+1])) for i in range(len(ds) - 1))
    print(f"{y}: {len(strict)} = {len(strict)/weeks:.2f}/week; longest gap {gaps[-1]}; open gap to window end {(b - ds[-1]).days} d")
