"""Fixtures for v3c.3 name/IMO normalisation (canaries: glitchfox, board #123797, #123814). Run: python3 test_v3c_fixtures.py"""
import match_rule_v3 as m

NAMES = [('MVKOS', 'mvkos'), ('MTWARA', 'mtwara'), ('M/V. TUTOR', 'tutor'), ('M/T TUTOR', 'tutor'),
         ('MV TUTOR', 'tutor'), ('M.V. TUTOR', 'tutor'), ('Tutor', 'tutor'), ('MY TUTOR', 'my tutor')]
IMOS = [('IMO 99431400', None), ('MMSI 636019825', None), ('Tel +7 994 314 0', None),
        ('IMO: 9943140 (MMSI 636019825)', 'imo:9943140'), ('IMO 9943141', 'imo_bad:9943141'), (9943140, 'imo:9943140')]

for s, want in NAMES: assert m.norm_name(s) == want, (s, m.norm_name(s), want)
for s, want in IMOS: assert m.norm_imo(s) == want, (s, m.norm_imo(s), want)
assert m.name_given({'ukmto_name_given': 'MV TUTOR', 'ukmto_imo_given': 'IMO 9943140'}) & m.ident({'ship': 'Tutor', 'imo': 9943140})
assert not (m.name_given({'ukmto_imo_given': 'IMO 9943141'}) & m.ident({'ship': 'X', 'imo': 9943141}))
# v3c.3 (#123814)
assert not m.id_agree(m.name_given({'ukmto_name_given': 'OCEAN STAR', 'ukmto_imo_given': 'IMO 9312341'}), m.ident({'ship': 'Ocean Star', 'imo': 9943140}))
assert m.id_agree(m.name_given({'ukmto_name_given': 'OCEAN STAR'}), m.ident({'ship': 'Ocean Star', 'imo': 9943140}))
assert not (m.name_given({'ukmto_name_given': '—'}) or m.ident({'ship': '-'}))
for ph in ('N/A', 'Unknown', '?', 'TBC', 'not named'): assert m.norm_name(ph) is None, ph
assert m.norm_imo('IMO ٩٩٤٣١٤٠') == 'imo:9943140'
assert m.norm_name('SÉLÈNE') == m.norm_name('Selene') == 'selene'
# v3c.4 (#123841)
for ph in ('unidentified vessel', 'Unknown Vessel', 'unnamed vessel', 'a vessel', 'not disclosed', 'undisclosed', 'MV', 'M/V'): assert m.norm_name(ph) is None, ph
assert not m.id_agree(m.name_given({'ukmto_name_given': 'unidentified vessel'}), m.ident({'ship': 'Unidentified Vessel'}))
assert m.norm_name('OCEAN STAR') == 'ocean star' and m.norm_name('MY TUTOR') == 'my tutor' and m.norm_name('THE ONE') == 'the one'
# v3c.5 (#123847)
for ph in ('unknown tanker', 'Unknown tanker', 'unidentified bulk carrier', 'LPG tanker', 'container ship', 'bulk carrier', 'MT', 'MSV', 'general cargo', 'crude oil tanker', 'fishing dhow'): assert m.norm_name(ph) is None, ph
assert not m.id_agree(m.name_given({'ukmto_name_given': 'unknown tanker'}), m.ident({'ship': 'Unknown tanker'}))
assert not m.name_given({'ukmto_name_given': 'LPG tanker'})  # names no vessel -> type branch
assert m.norm_name('OCEAN STAR') == 'ocean star' and m.norm_name('MY TUTOR') == 'my tutor' and m.norm_name('TANKER OCEAN') == 'tanker ocean'
# v3c.6 (#123876)
for ph in ('a Liberian-flagged tanker', 'Marshall Islands-flagged bulk carrier', 'UK-flagged LPG carrier', 'Greek-owned tanker', 'an Israeli-linked vessel', 'oil tanker'): assert m.norm_name(ph) is None, ph
assert not m.id_agree(m.name_given({'ukmto_name_given': 'Liberian-flagged tanker'}), m.ident({'ship': 'Liberian-Flagged Tanker'}))
assert m.norm_name('the tanker MT OCEAN STAR') == 'the tanker mt ocean star'  # frozen recall cost: a miss, not a wrong match
print(f'{len(NAMES) + len(IMOS) + 2 + 9 + 10 + 14 + 8} fixtures ok')
