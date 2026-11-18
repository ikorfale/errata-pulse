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


import re, unicodedata
_PFX = re.compile(r'^(m\.?\s*/?\s*[vt]\.?|mv|mt|msv)\s+')


def norm_name(x):
    # v3c.1 (2026-11-17, before any post-15.11 incident; bug found by glitchfox #123770): casefold, drop MV/MT/M/V/M.V./MSV
    # prefix and punctuation. Former names and transliterations are NOT matched (frozen as "does not match").
    # v3c.3 (2026-11-17, before any post-15.11 incident; canary 4 by glitchfox #123814): NFKD and drop combining marks
    # first, so SELENE with accents equals Selene (it used to split into 's l ne').
    t = unicodedata.normalize('NFKD', str(x))
    t = ''.join(ch for ch in t if not unicodedata.combining(ch)).casefold().strip()
    t = _PFX.sub('', t)
    t = re.sub(r'[^0-9a-z\u0400-\u04ff]+', ' ', t).strip()
    # v3c.3 (canary 2): placeholders are not a name; an empty or placeholder name gives no token at all
    # v3c.4 (2026-11-17, before any post-15.11 incident; canary by glitchfox #123841): a name made only of stoplist words
    # ('unidentified vessel', 'a vessel', 'not disclosed', bare 'MV' or 'M/V') is not a name either. A real name keeps all its words.
    if t in PLACEHOLDERS or all(w in NAME_STOP for w in t.split()):
        return None
    # v3c.6 (2026-11-17, before any post-15.11 incident; canary by glitchfox #123876): 'Liberian-flagged tanker',
    # 'Greek-owned tanker', 'Israeli-linked vessel' describe a ship whose name is withheld. A descriptor word makes the
    # whole string a description, not a name; the flag word goes to the type/flag branch instead.
    if any(w in DESCRIPTORS for w in t.split()):
        return None
    # v3c.7 (2026-11-17, before any post-15.11 incident; structural guard by glitchfox #123954): the descriptor list kept
    # losing the race ('US-sanctioned tanker', 'a shadow fleet tanker', 'a tanker flying the Liberian flag'). With >=2
    # tokens, a string that starts with 'a'/'an' or ends in a type word is a description, not a name. Costs, frozen:
    # 'A LADY' and 'GOLDEN CARRIER' lose their names (a miss, never a wrong match).
    w = t.split()
    if len(w) >= 2 and (w[0] in ('a', 'an') or w[-1] in TYPE_END):
        return None
    # v3c.8 (2026-11-18, before any post-15.11 incident; canary by glitchfox #124218): plurals and trailing words slipped
    # past the end check ('two Iranian tankers', 'Liberian tanker hit', 'VLCC (name not released)'). With >=2 tokens, a
    # type word (or its plural, or a size class) at any position after the first, or a withheld-name word anywhere, makes
    # it a description. 'TANKER OCEAN' (type word first) keeps its name. Costs, frozen: real names with a type word after
    # the first token ('Tara Gas', 'Star Bulk') were already lost in v3c.7, from the name field too; a miss, never a wrong match.
    if len(w) >= 2 and (any(x in TYPE_ANY for x in w[1:]) or any(x in WITHHELD for x in w)):
        return None
    return t


NAME_STOP = set('a an the unknown unidentified unnamed undisclosed not named known disclosed merchant vessel ship mv m v'.split())
# v3c.5 (2026-11-17, before any post-15.11 incident; canary by glitchfox #123847): type vocabulary is never identity.
# Add the prefixes _PFX strips (mt t msv), glitchfox's type words, and every token of the frozen CLASSES list.
NAME_STOP |= set('mt t msv tanker carrier bulk container lpg lng crude product products chemical oil cargo general'.split())
NAME_STOP |= {w for k, _ in CLASSES for w in re.sub(r'[^0-9a-z]+', ' ', k).split()}
DESCRIPTORS = set('flagged owned linked operated managed registered chartered bound affiliated'.split())
TYPE_END = set('tanker carrier vessel ship'.split()) | {w for k, _ in CLASSES for w in re.sub(r'[^0-9a-z]+', ' ', k).split()}
TYPE_ANY = TYPE_END | {x + 's' for x in TYPE_END} | set('vlcc vlccs ulcc ulccs suezmax aframax panamax handysize'.split())
WITHHELD = set('withheld released redacted'.split())
PLACEHOLDERS = {'', 'n a', 'na', 'unknown', 'not named', 'unnamed', 'tbc', 'tba', 'none', 'nil', 'not known', 'vessel', 'merchant vessel'}


def imo_check(d):
    # IMO check digit: first six digits weighted 7..2, sum mod 10 == seventh digit
    return sum(int(c) * w for c, w in zip(d[:6], range(7, 1, -1))) % 10 == int(d[6])


def norm_imo(x):
    # v3c.2 (2026-11-17, before any post-15.11 incident; canaries by glitchfox #123797): take only a bounded run of
    # exactly 7 digits (an 8-digit typo, a 9-digit MMSI or a phone number yields nothing), keep the first run that passes
    # the IMO check digit. A 7-digit run that fails the check gives 'imo_bad:<digits>': the entry still counts as naming a
    # vessel, but that token can never match a claim (safe direction), and the run prints it.
    # v3c.3 (canary 3): NFKC + ASCII-only digits, after mapping any Unicode decimal digit (Arabic-Indic etc.) to ASCII
    t = unicodedata.normalize('NFKC', str(x))
    t = ''.join(str(unicodedata.decimal(ch)) if ch.isdecimal() else ch for ch in t)
    runs = re.findall(r'(?<!\d)\d{7}(?!\d)', t, flags=re.ASCII)
    for d in runs:
        if imo_check(d): return 'imo:' + d
    return 'imo_bad:' + runs[0] if runs else None


def name_given(e):
    # v3c: vessel name / IMO as the verifier entry prints it (fields filled by the post-15.11 collector), normalised (v3c.1)
    out = set()
    if e.get('ukmto_name_given') and norm_name(e['ukmto_name_given']): out.add('name:' + norm_name(e['ukmto_name_given']))
    if e.get('ukmto_imo_given') and norm_imo(e['ukmto_imo_given']): out.add(norm_imo(e['ukmto_imo_given']))
    return out


def ident(c):
    out = set()
    if c.get('ship') and norm_name(c['ship']): out.add('name:' + norm_name(c['ship']))
    if c.get('imo') and (norm_imo(c['imo']) or '').startswith('imo:'): out.add(norm_imo(c['imo']))
    return out


def id_agree(en, ci):
    # v3c.3 (canary 1, glitchfox #123814): a valid IMO is unique, a name is not. If both sides carry a valid IMO and they
    # differ, that is a contradiction whatever the name says; otherwise any shared token (name or IMO) agrees.
    ei = {t for t in en if t.startswith('imo:')}; cimo = {t for t in ci if t.startswith('imo:')}
    if ei and cimo and not (ei & cimo): return False
    return bool(en & ci)


def cls_hit(t):
    # which keyword fired and at what offset, so every prose class at the readout can be audited by eye (v3c.1)
    t = (t or '').lower()
    for k, c in CLASSES:
        i = t.find(k)
        if i >= 0: return (c, k, i)
    return None


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
                if id_agree(en, ident(c)): out.append(j)
                continue
            if ct and et and ct != et: continue
            ef = e.get('ukmto_flag_given'); cf = c.get('flag')
            if ef and cf and ef.lower() != cf.lower(): continue
            out.append(j)
        cand[i] = out
        for j in out:
            e = entries[j]; et = etype(e, prose); ef = e.get('ukmto_flag_given'); cf = c.get('flag')
            posok[(i, j)] = bool((ct and et and ct == et) or (ef and cf and ef.lower() == cf.lower()))
            if zen:  # flag alone is not enough; v3c.1: a class read from prose may only contradict, never corroborate
                tg = cls(e.get('ukmto_type_given'))
                posok[(i, j)] = id_agree(name_given(e), ident(c)) or bool(ct and tg and ct == tg)
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
        if zen and prose:
            for jj in js:
                ee = entries[jj]
                if not ee.get('ukmto_type_given') and ee.get('ukmto_text'): lines[-1] += f" cls_hit[{jj}]={cls_hit((ee.get('ukmto_text') or '') + ' ' + (ee.get('ukmto_outcome') or ''))}"
    if zen:
        bad = [(k, t) for k, e in enumerate(entries) for t in name_given(e) if t.startswith('imo_bad:')]
        if bad: print('imo_bad_check (entry names a vessel, IMO fails check digit, never matches): ' + ', '.join(f'[{k}] {t}' for k, t in bad))
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
                print('--- labels=%s rule=%s%s' % ('strong' if strong else 'all', 'v2' if v2 else 'v1', '+v3c.7(name/IMO normalised, or positive type from ukmto_type_given only)' if zen else '+positive' if pos else '+prose' if prose else '')); main(v2, pos, strong, prose, zen)
