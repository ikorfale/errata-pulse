"""Fixtures for v3c.2 name/IMO normalisation (canaries: glitchfox, board #123797). Run: python3 test_v3c_fixtures.py"""
import match_rule_v3 as m

NAMES = [('MVKOS', 'mvkos'), ('MTWARA', 'mtwara'), ('M/V. TUTOR', 'tutor'), ('M/T TUTOR', 'tutor'),
         ('MV TUTOR', 'tutor'), ('M.V. TUTOR', 'tutor'), ('Tutor', 'tutor'), ('MY TUTOR', 'my tutor')]
IMOS = [('IMO 99431400', None), ('MMSI 636019825', None), ('Tel +7 994 314 0', None),
        ('IMO: 9943140 (MMSI 636019825)', 'imo:9943140'), ('IMO 9943141', 'imo_bad:9943141'), (9943140, 'imo:9943140')]

for s, want in NAMES: assert m.norm_name(s) == want, (s, m.norm_name(s), want)
for s, want in IMOS: assert m.norm_imo(s) == want, (s, m.norm_imo(s), want)
assert m.name_given({'ukmto_name_given': 'MV TUTOR', 'ukmto_imo_given': 'IMO 9943140'}) & m.ident({'ship': 'Tutor', 'imo': 9943140})
assert not (m.name_given({'ukmto_imo_given': 'IMO 9943141'}) & m.ident({'ship': 'X', 'imo': 9943141}))
print(f'{len(NAMES) + len(IMOS) + 2} fixtures ok')
