"""v3 candidate (frozen 2026-11-15 ~07:50Z, before any post-15.11 incident is collected). Proposed by glitchfox on the
board (#122284) AFTER seeing both false matches (Ocean Jazz 2024, NCC Wafa 2026), so its back-test is fit to the errors
it was chosen on and is NOT evidence; only incidents after 2026-11-15 test it.
Rule: v1 (or v2) as before, plus: a single-candidate 'match' also needs POSITIVE agreement between claim and entry on
type class or on flag; 'no information' is not agreement, and such a match is downgraded to 'ambiguous'.
label_confidence: a pair whose note starts with "WEAK" is a weak label; the script prints tallies for all labels and
for strong labels only (weak pairs dropped from the claims).
v3b (my own variant, frozen at the same time, also chosen after seeing Wafa): entry type class may also come from the
entry's prose (ukmto_text = the UKMTO warning text verbatim, a field post-15.11 collection must fill; plus ukmto_outcome) when ukmto_type_given is empty; new class 'small' (dhow, MSV, fishing) contradicts every
ship class. Both v3a (+positive) and v3b (+prose) are judged on post-15.11 incidents by fewer WRONG, then fewer ambiguous.
Back-test note: in validation_2026 the dhow's 'mechanized sailing vessel' sits only in the collector's note, not in a
data field, so v3b cannot fix NCC Wafa on the old data; that is a data gap, and also no evidence that v3b works.
Usage: match_rule_v3.py FILE   (prints v1/v2 x plain/positive x all/strong)

Inherited v2 docstring: v2 (written 15.11.2026 before validation_2026.jsonl arrived): identical to v1 except one added condition:
E must report an attack on a vessel (ukmto_event == "attack"), not a sighting, approach or other. Runs v1 and v2 side by side.
Usage: match_rule_v2.py validation_2026.jsonl

Original v1 docstring: Blind check of the claim-match rule (errata-pulse research/claim-match/RULE.md, frozen 2026-10-18).

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
CLASSES = [('dhow', 'small'), ('msv', 'small'), ('mechanized sailing', 'small'), ('mechanised sailing', 'small'), ('fishing', 'small'), ('lng', 'lng'), ('lpg', 'lpg'), ('gas', 'lpg'), ('car carrier', 'car'), ('vehicle', 'car'), ('ro-ro', 'cargo'),
           ('container', 'container'), ('bulk', 'bulk'), ('tanker', 'tanker'), ('general cargo', 'cargo'), ('cargo', 'cargo')]


def cls(t):
    t = (t or '').lower()
    for k, c in CLASSES:
        if k in t: return c
    return None


def name_given(e):
    # v3c only: vessel name / IMO exactly as the verifier entry prints it (fields filled by the post-15.11 collector)
    return {x.strip().lower() for x in (e.get('ukmto_name_given'), e.get('ukmto_imo_given')) if x}


def ident(c):
    return {str(x).strip().lower() for x in (c.get('ship'), c.get('imo')) if x}


def area_ok(claim_area, e_area):
    if not claim_area: return e_area in RED
    if claim_area == e_area: return True
    return e_area == 'Bab el-Mandeb' and claim_area in ('Red Sea', 'Gulf of Aden')


def d(s): return dt.date.fromisoformat(s)


def etype(e, prose):
    return cls(e.get('ukmto_type_given')) or (cls((e.get('ukmto_text') or '') + ' ' + (e.get('ukmto_outcome') or '')) if prose else None)


def main(v2, pos=False, strong=False, prose=False, zen=False):
    rows = [json.loads(l) for l in open(F) if l.strip()]
    if strong: rows = [r for r in rows if not (r.get('kind') == 'pair' and (r.get('note') or '').upper().startswith('WEAK'))]
    claims = [r for r in rows if r.get('kind') in ('pair', 'claim_only') and r.get('claim_date')]
    entries = [r for r in rows if r.get('kind') in ('pair', 'ukmto_only') and r.get('ukmto_date')]
    elig = (lambda e: e.get('ukmto_event') == 'attack') if v2 else (lambda e: True)
    cand = {}; posok = {}
    for i, c in enumerate(claims):
        dc = d(c['claim_date']); ct = cls(c.get('ship_type')); out = []
        for j, e in enumerate(entries):
            if not elig(e): continue
            de = d(e['ukmto_date'])
            if not (dc - dt.timedelta(days=2) <= de <= dc + dt.timedelta(days=1)): continue
            if not area_ok(c.get('claim_area'), e.get('ukmto_area')): continue
            et = etype(e, prose)
            en = name_given(e)
            if zen and en:  # v3c: a vessel name/IMO in the verifier entry decides alone
                if en & ident(c): out.append(j)
                continue
            if ct and et and ct != et: continue
            ef = e.get('ukmto_flag_given'); cf = c.get('flag')
            if ef and cf and ef.lower() != cf.lower(): continue
            out.append(j)
        cand[i] = out
        for j in out:
            e = entries[j]; et = etype(e, prose); ef = e.get('ukmto_flag_given'); cf = c.get('flag')
            posok[(i, j)] = bool((ct and et and ct == et) or (ef and cf and ef.lower() == cf.lower()))
            if zen: posok[(i, j)] = bool(name_given(e) & ident(c)) or bool(ct and et and ct == et)  # flag alone is not enough
    claimed_by = collections.Counter(j for js in cand.values() for j in js)
    tally = collections.Counter(); lines = []
    for i, c in enumerate(claims):
        js = cand[i]
        if len(js) == 1 and claimed_by[js[0]] == 1 and not ((pos or zen) and not posok[(i, js[0])]): verdict, j = 'match', js[0]
        elif not js: verdict, j = 'none', None
        else: verdict, j = 'ambiguous', None
        truth = entries.index(c) if c.get('kind') == 'pair' and c in entries else None
        if verdict == 'match': score = 'correct' if j == truth else 'WRONG'
        elif verdict == 'none': score = 'missed' if truth is not None else 'correct-none'
        else: score = 'ambiguous'
        tally[score] += 1
        lines.append(f"{c['claim_date']} {c.get('ship')!s:<24} {c.get('kind'):<10} cands={len(js)} {verdict:<9} {score}")
    print(f"=== {'v2 (attack-only)' if v2 else 'v1 (frozen 18.10)'}: claims {len(claims)}, UKMTO entries {len(entries)} (attacks {sum(e.get('ukmto_event') == 'attack' for e in entries)})")
    print('\n'.join(lines))
    print('TALLY', dict(tally))
    noinc = [s for (s, c) in zip([l.split()[-1] for l in lines], claims) if c.get('kind') == 'claim_only']
    print('no-incident claims', len(noinc), dict(collections.Counter(noinc)))
    print('RULE USABLE' if tally['WRONG'] == 0 else 'RULE NOT USABLE: at least one wrong assignment')
    return tally


if __name__ == '__main__':
    for strong in (False, True):
        for v2 in (False, True):
            for pos, prose, zen in ((False, False, False), (True, False, False), (False, True, False), (False, True, True)):
                print('--- labels=%s rule=%s%s' % ('strong' if strong else 'all', 'v2' if v2 else 'v1', '+v3c(name or positive type)' if zen else '+positive' if pos else '+prose' if prose else '')); main(v2, pos, strong, prose, zen)
