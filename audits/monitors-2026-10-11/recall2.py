"""Re-measure (#182) of the Chaos Pulse monitors after the 07.10 query widening (energy + clash now name Russia,
Ukraine, the Black Sea, cargo/grain ships and NATO EEZs).

Window: ledger events with date_published 2026-10-08 .. 2026-10-11 (to 13:10 UTC), against monitor hits from
2026-10-08 00:00 (alerts.jsonl lines 16-52). 10-07 events are left out: the first measurement (recall.py) ended
7.10 21:07 and their publication hour is not in the ledger. Hand labels, one row each, so a row can be disputed.
Caveat that matters: the ledger is partly built FROM the hits (found_via=monitor), which inflates recall. The
result is split by that, and the honest number is the one on events I found some other way.
"""
import json, math, collections
P = "./"  # frozen copies of the event ledger and monitor hits sit next to this script
ev = {json.loads(l)["id"]: json.loads(l) for l in open(P + "events.jsonl")}
# id -> (scope: monitor name | 'gap' (material, no query covers it) | 'out' (not alert material), region, caught hit line or None)
L = {
 "salavat-refinery-1008":            ("energy", "russia", 16),
 "trump-iran-end-soon-strike-prep-1008": ("ceasefire", "mideast", 18),
 "us-gulf-isaias-shutin-1008":       ("energy", "other", 20),
 "trump-no-iran-strike-before-midterms-1008": ("ceasefire", "mideast", 21),
 "hormuz-transit-drop-ft-1006":      ("out", "mideast", None),
 "omsk-refinery-1008":               ("energy", "russia", None),
 "saudi-airport-deaths-1007":        ("clash", "mideast", None),
 "miami-talks-1009":                 ("ceasefire", "russia", 26),
 "nordstream-kushner-dmitriev-1008": ("out", "russia", None),
 "kramatorsk-minibus-1008":          ("out", "ukraine", None),
 "telegraph-surovikin-bridges-1008": ("out", "russia", None),
 "yandex-dc-sasovo-1008":            ("gap", "russia", None),
 "redkino-plant-1009":               ("energy", "russia", 23),
 "ukraine-grid-emergency-1009":      ("energy", "ukraine", 24),
 "ru-milpolice-draft-decree-1008":   ("out", "russia", None),
 "yandex-dc-kaluga-1009":            ("gap", "russia", 25),
 "ukhta-refinery-1009":              ("energy", "russia", 27),
 "saudi-no-houthi-truce-1009":       ("ceasefire", "mideast", 28),
 "nv-sunshine-lpg-1009":             ("energy", "mideast", 31),
 "ru-energy-truce-sanctions-1009":   ("ceasefire", "russia", 33),
 "us-ru-diesel-gl135-1009":          ("ceasefire", "russia", 34),
 "ru-kuibyshev-npz-reserve-ad-1008": ("out", "russia", 35),
 "kpler-mideast-exports-1009":       ("out", "mideast", None),
 "fujairah-vlcc-fire-1008":          ("energy", "mideast", None),
 "klitschko-survival-1009":          ("out", "ukraine", None),
 "rostov-nznp-terminal-1010":        ("energy", "russia", 36),
 "riyadh-airport-terminal-1010":     ("clash", "mideast", 39),
 "ua-strike-samara-lpds-1007-1010":  ("energy", "russia", 42),
 "ru-bill-women-service-age-1009":   ("out", "russia", 43),
 "us-ua-intel-threat-1010":          ("out", "russia", None),
 "trump-new-president-ua-1010":      ("out", "russia", None),
 "novoshakhtinsk-terminal-1010":     ("energy", "russia", 44),
 "kyiv-metro-water-1010":            ("energy", "ukraine", 38),
 "zaporizhzhia-strikes-1010":        ("out", "ukraine", None),
 "putin-relays-iran-position-1010":  ("out", "mideast", None),
 "yemen-taiz-entrance-1010":         ("out", "mideast", None),
 "saudi-filming-ban-1010":           ("out", "mideast", None),
 "miami-talks-end-1010":             ("ceasefire", "russia", 37),
 "putin-all-objectives-call-1009":   ("ceasefire", "russia", 34),
 "isw-ua-counterattacks-lyman-1008": ("out", "ukraine", None),
 "yandex-dc-vladimir-1011":          ("gap", "russia", 46),   # caught only by digital-infra, created after the strike (backlog hit)
 "ua-grid-limits-1011":              ("energy", "ukraine", 47),
 "uk-ua-energy-truce-call-1010":     ("ceasefire", "russia", 48),
 "us-ru-incentives-nyt-1010":        ("ceasefire", "russia", 51),
}
# every hit line 16-52: new (first report of a ledger event or of a new consequence), dup (same event again), noise (not alert material)
HITS = {16:"new",17:"noise",18:"new",19:"noise",20:"new",21:"new",22:"dup",23:"new",24:"new",25:"new",26:"new",27:"new",28:"new",
        29:"dup",30:"noise",31:"new",32:"noise",33:"new",34:"new",35:"noise",36:"new",37:"new",38:"new",39:"new",40:"dup",41:"dup",
        42:"new",43:"noise",44:"new",45:"dup",46:"new",47:"new",48:"new",49:"noise",50:"dup",51:"new",52:"noise"}
# 17 India truce: the ledger event is published 10-07 (outside window) -> labelled noise here only for window accounting; see note
win = [k for k, e in ev.items() if "2026-10-08" <= str(e.get("date_published", ""))[:10] <= "2026-10-11"]
missing = sorted(set(win) - set(L)); extra = sorted(set(L) - set(win))
assert not extra, extra
print(f"window events in ledger: {len(win)}, labelled: {len(L)}, unlabelled: {missing}")
def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); s = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)); return ((c-s)/d, (c+s)/d)
def rep(name, rows):
    k = sum(1 for r in rows if r[2] is not None); n = len(rows); lo, hi = wilson(k, n)
    print(f"{name:<44} {k}/{n} = {100*k/max(n,1):.0f}%  [95% {100*lo:.0f}%, {100*hi:.0f}%]")
mat = [(i,) + L[i][1:] for i in L if L[i][0] != "out"]
scoped = [(i,) + L[i][1:] for i in L if L[i][0] not in ("out", "gap")]
fv = lambda i: (ev[i].get("found_via") or "").startswith("monitor")
rep("recall, in scope of a query", scoped)
rep("recall, all material incl. gaps", mat)
rep("recall, in scope, events NOT found via monitor", [r for r in scoped if not fv(r[0])])
for reg in ("russia", "ukraine", "mideast", "other"): rep(f"  in scope, {reg}", [r for r in scoped if r[1] == reg])
for m in ("energy", "ceasefire", "clash"): rep(f"  in scope, {m}", [(i,) + L[i][1:] for i in L if L[i][0] == m])
print("missed (in scope):", [i for i, *_ in scoped if L[i][2] is None])
print("gaps (material, no query):", [i for i in L if L[i][0] == "gap"])
c = collections.Counter(HITS.values()); n = len(HITS)
print(f"hits {n} in {85:.0f} h = {24*n/85:.1f}/day; new {c['new']}, duplicate {c['dup']}, noise {c['noise']} (noise share {100*c['noise']/n:.0f}%)")
print("first measurement (recall.py, 5-7 Oct, old queries): in scope 13/17 = 76%, Russia/Black Sea 1/5, 6.6 hits/day")
