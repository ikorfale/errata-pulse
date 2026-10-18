"""Blind check of the claim-match rule (errata-pulse research/claim-match/RULE.md, frozen 2026-10-18).

Reads validation_2024_25.jsonl (kind pair / ukmto_only / claim_only). The matcher sees, for a claim, only its date,
its area and the named ship's public type and flag; for a UKMTO entry only date, area and the type/flag UKMTO gave.
Names, IMO and the true pairing are used only afterwards, to score.

Interpretations fixed here before the data was seen (written 18.10 while the dataset was still being collected):
- Bab el-Mandeb is compatible with a claim naming the Red Sea or the Gulf of Aden (it is the strait between them);
  otherwise areas must be equal. Claim with no area: Red Sea, Bab el-Mandeb or Gulf of Aden.
- Type contradiction only between distinct classes (tanker, bulk, container, general cargo/ro-ro, car carrier, LPG/LNG);
  "merchant vessel" or missing contradicts nothing. Flag contradicts only if both are given and differ.
- Rule 4 ("not matched to another claim"): a claim matches only when it has exactly one candidate AND no other claim
  has that same entry as a candidate. Otherwise ambiguous. Order-free.
"""
import json, sys, datetime as dt, collections

F = sys.argv[1] if len(sys.argv) > 1 else 'validation_2024_25.jsonl'
RED = {'Red Sea', 'Bab el-Mandeb', 'Gulf of Aden'}
CLASSES = [('lng', 'lng'), ('lpg', 'lpg'), ('gas', 'lpg'), ('car carrier', 'car'), ('vehicle', 'car'), ('ro-ro', 'cargo'),
           ('container', 'container'), ('bulk', 'bulk'), ('tanker', 'tanker'), ('general cargo', 'cargo'), ('cargo', 'cargo')]


def cls(t):
    t = (t or '').lower()
    for k, c in CLASSES:
        if k in t: return c
    return None


def area_ok(claim_area, e_area):
    if not claim_area: return e_area in RED
    if claim_area == e_area: return True
    return e_area == 'Bab el-Mandeb' and claim_area in ('Red Sea', 'Gulf of Aden')


def d(s): return dt.date.fromisoformat(s)


def main():
    rows = [json.loads(l) for l in open(F) if l.strip()]
    claims = [r for r in rows if r.get('kind') in ('pair', 'claim_only') and r.get('claim_date')]
    entries = [r for r in rows if r.get('kind') in ('pair', 'ukmto_only') and r.get('ukmto_date')]
    cand = {}
    for i, c in enumerate(claims):
        dc = d(c['claim_date']); ct = cls(c.get('ship_type')); out = []
        for j, e in enumerate(entries):
            de = d(e['ukmto_date'])
            if not (dc - dt.timedelta(days=2) <= de <= dc + dt.timedelta(days=1)): continue
            if not area_ok(c.get('claim_area'), e.get('ukmto_area')): continue
            et = cls(e.get('ukmto_type_given'))
            if ct and et and ct != et: continue
            ef = e.get('ukmto_flag_given'); cf = c.get('flag')
            if ef and cf and ef.lower() != cf.lower(): continue
            out.append(j)
        cand[i] = out
    claimed_by = collections.Counter(j for js in cand.values() for j in js)
    tally = collections.Counter(); lines = []
    for i, c in enumerate(claims):
        js = cand[i]
        if len(js) == 1 and claimed_by[js[0]] == 1: verdict, j = 'match', js[0]
        elif not js: verdict, j = 'none', None
        else: verdict, j = 'ambiguous', None
        truth = entries.index(c) if c.get('kind') == 'pair' and c in entries else None
        if verdict == 'match': score = 'correct' if j == truth else 'WRONG'
        elif verdict == 'none': score = 'missed' if truth is not None else 'correct-none'
        else: score = 'ambiguous'
        tally[score] += 1
        lines.append(f"{c['claim_date']} {c.get('ship')!s:<24} {c.get('kind'):<10} cands={len(js)} {verdict:<9} {score}")
    print(f"claims {len(claims)}, UKMTO entries {len(entries)}")
    print('\n'.join(lines))
    print('TALLY', dict(tally))
    print('RULE USABLE ON 2026' if tally['WRONG'] == 0 else 'RULE NOT USABLE: at least one wrong assignment')


if __name__ == '__main__':
    main()
