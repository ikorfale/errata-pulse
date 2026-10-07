"""How good are the four hourly Chaos Pulse news monitors?

Ground truth = my own event ledger (pulse/events.jsonl) for events published after the
monitors started (2026-10-05 11:11 UTC) up to 2026-10-07 21:07 UTC, plus the 07.10
ceasefire briefing noted in STATE.md. Each event is hand-labelled: which monitor's query
wording covers it (or 'gap' = material but outside every query), and which hit caught it.
Each hit (pulse/alerts.jsonl line number) is labelled new / backlog / duplicate.
Labels are judgement calls, written down here so anyone can disagree with a specific row.
"""
import json, math, datetime, collections

import os
HERE = os.path.dirname(os.path.abspath(__file__)) + "/"  # frozen copies of alerts.jsonl and events.jsonl
hits = [json.loads(l) for l in open(HERE + "alerts.jsonl")]

# event id -> (scope monitor or 'gap' or 'out', region, caught_by hit index or None, why)
EVENTS = {
    "lipsi-tanker-hit":            ("energy", "gulf", 0, "Hormuz tanker hit, published 10-05"),
    "irgc-khasab-turnback-1005":   ("energy", "gulf", 3, "IRGC turns tanker back"),
    "ew-pipeline-khurais-1004":    ("energy", "gulf", 7, "pumping station, single source"),
    "lb-il-talks-1020":            ("ceasefire", "levant", 4, "talks scheduled"),
    "hormuz-tanker-strike-1005":   ("energy", "gulf", 6, "tanker fire 16:37 UTC"),
    "iran-reviews-us-reply-1004":  ("ceasefire", "gulf", None, "Iran-US exchange via mediators, AFP"),
    "mecca-pact-activation-1005":  ("clash", "gulf", None, "Turkey+Pakistan defence pledge = new states entering"),
    "yemen-dhubab-claims-1006":    ("clash", "yemen", 5, "new offensive / front"),
    "france-m51-3-vigilant-1006":  ("nuclear", "europe", 8, "SLBM test"),
    "on-peace-tanker-1006":        ("energy", "gulf", 9, "tanker hit, 12 injured"),
    "qatar-us-iran-talks-1006":    ("ceasefire", "gulf", 10, "talks continue"),
    "volodarskaya-lpds-1006":      ("energy", "russia", None, "Transneft fuel node fire after drone strike"),
    "sochi-tanker-fire-1006":      ("energy", "russia", None, "tanker burning off Sochi (claimed)"),
    "yemen-escalation-1007":       ("clash", "yemen", 11, "270 dead in a day, Riyadh intercept"),
    "lithuania-nuke-ban-vote-1006": ("nuclear", "europe", 13, "constitutional WMD ban repeal, 1st reading"),
    "hormuz-pace-oct-1007":        ("energy", "gulf", 14, "9 attacks in 7 days"),
    "ceasefire-tracks-1007":       ("ceasefire", "russia", 15, "Kyiv: five ceasefire formats (STATE.md)"),
    # material, but no query's wording covers them: cargo/grain ships sunk by drones in NATO EEZs
    "black-sea-bulgaria-eez-1006": ("gap", "russia", None, "2 cargo ships hit in Bulgarian EEZ, AP+Reuters"),
    "black-sea-romania-eez-1005":  ("gap", "russia", None, "grain ship sunk in Romanian EEZ, AP"),
    # in the ledger, outside every query and not material for an alert
    "houthi-taiz-aden-cut-1005":   ("out", "yemen", None, "road cut"),
    "ua-claims-51pct-refining":    ("out", "russia", None, "cumulative claim, no new event"),
    "kremlin-pay-price-1005":      ("out", "russia", None, "rhetoric"),
    "tasnim-riyadh-flights-1005":  ("out", "yemen", None, "claimed flight halt"),
    "zelensky-mass-strike-warning-1006": ("out", "russia", None, "warning"),
}
# hit index -> (judgement, note)
HITS = {0: ("new", "lipsi"), 1: ("backlog", "Bab el-Mandeb 10-04, already counted"),
        2: ("backlog", "US talks offer, published 10-04, already in ledger"),
        3: ("new", ""), 4: ("new", ""), 5: ("new", ""), 6: ("new", ""),
        7: ("new", "single source, later disputed"), 8: ("new", ""), 9: ("new", ""),
        10: ("new", ""), 11: ("new", ""), 12: ("duplicate", "same Yemen escalation as 11"),
        13: ("new", "mixed: stale 25.09 RIA column + new Seimas vote"), 14: ("new", ""), 15: ("new", "")}
# known event times (UTC) for latency: hit -> (first publication or event time, source)
FIRST = {6: ("2026-10-05T16:37", "UKMTO event time"),
         15: ("2026-10-07T11:21", "UNN 14:21 Kyiv time")}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


assert len(hits) == len(HITS), (len(hits), len(HITS))
ledger_ids = {json.loads(l)["id"] for l in open(HERE + "events.jsonl")}
missing = [e for e in EVENTS if e not in ledger_ids and e != "ceasefire-tracks-1007"]
assert not missing, missing

span_h = (hits[-1]["seen_at"] - 1791198672) / 3600  # monitors created 2026-10-05 11:11:12 UTC
print(f"window: {span_h:.0f} h, hits: {len(hits)}, ledger events labelled: {len(EVENTS)}")

inscope = {k: v for k, v in EVENTS.items() if v[0] not in ("gap", "out")}
k = sum(v[2] is not None for v in inscope.values())
lo, hi = wilson(k, len(inscope))
print(f"recall, in scope of a query: {k}/{len(inscope)} = {k/len(inscope):.0%}  [95% {lo:.0%}, {hi:.0%}]")
material = {k_: v for k_, v in EVENTS.items() if v[0] != "out"}
km = sum(v[2] is not None for v in material.values())
print(f"recall, all material events incl. query gaps: {km}/{len(material)} = {km/len(material):.0%}")
by = collections.defaultdict(lambda: [0, 0])
for v in material.values():
    reg = "Russia/Black Sea" if v[1] == "russia" else ("Europe" if v[1] == "europe" else "Middle East")
    by[reg][1] += 1
    by[reg][0] += v[2] is not None
for reg, (a, n) in sorted(by.items()):
    print(f"  {reg:17s} {a}/{n}")
print("missed:")
for e, v in material.items():
    if v[2] is None:
        print(f"  {e:30s} [{v[0]}] {v[3]}")
c = collections.Counter(j for j, _ in HITS.values())
print(f"hits: new {c['new']}, backlog {c['backlog']}, duplicate {c['duplicate']}; "
      f"met the operator-alert threshold: 0 of {len(hits)}")
print(f"hits per day: {len(hits) / span_h * 24:.1f}")
for i, (t, src) in FIRST.items():
    t0 = datetime.datetime.fromisoformat(t).replace(tzinfo=datetime.UTC).timestamp()
    print(f"latency hit {i}: {(hits[i]['seen_at'] - t0) / 3600:.1f} h after {src}")
print("__END__")
