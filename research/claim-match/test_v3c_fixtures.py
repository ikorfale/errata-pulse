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
assert m.norm_name('the tanker MT OCEAN STAR') != 'ocean star'  # frozen recall cost: a miss, not a wrong match (None since v3c.8)
# v3c.7 (#123954)
for ph in ('a Chinese-built tanker', 'an Iranian-crewed tanker', 'US-sanctioned tanker', 'a Greek-controlled tanker', 'a shadow fleet tanker', 'a Liberian flag tanker', 'a tanker flying the Liberian flag'): assert m.norm_name(ph) is None, ph
assert not m.id_agree(m.name_given({'ukmto_name_given': 'US-sanctioned tanker'}), m.ident({'ship': 'US-Sanctioned Tanker'}))
for cost in ('A LADY', 'GOLDEN CARRIER', 'BOUND STAR', 'MANAGED RISK', 'the Panama-flagged LPG tanker Tara Gas'): assert m.norm_name(cost) is None, cost  # frozen recall costs
for keep, want in (('OCEAN STAR', 'ocean star'), ('MY TUTOR', 'my tutor'), ('TANKER OCEAN', 'tanker ocean'), ('LIBERIAN STAR', 'liberian star'), ('Selene', 'selene')): assert m.norm_name(keep) == want, keep
# v3c.8 (#124218)
for ph in ('US-sanctioned tankers', 'two Iranian tankers', 'Liberian tanker hit', 'tanker, name withheld', 'VLCC (name not released)', 'sanctioned tanker in the Gulf of Oman'): assert m.norm_name(ph) is None, ph
assert not m.id_agree(m.name_given({'ukmto_name_given': 'two Iranian tankers'}), m.ident({'ship': 'Two Iranian Tankers'}))
for cost in ('Tara Gas', 'Star Bulk', 'Ocean Container', 'the tanker MT OCEAN STAR'): assert m.norm_name(cost) is None, cost  # frozen: lost from the name field too
for keep, want in (('Gas Tara', 'gas tara'), ('Front Crude', 'front crude'), ('TANKER OCEAN', 'tanker ocean'), ('LIBERIAN STAR', 'liberian star')): assert m.norm_name(keep) == want, keep
# v3c.9 (#124452)
for ph in ('tanker seized by Iran', 'Tankers attacked off Fujairah', 'ship hit near Hodeidah', 'vessel, name unknown', 'name not disclosed', 'vlcc', 'released'): assert m.norm_name(ph) is None, ph
assert not m.id_agree(m.name_given({'ukmto_name_given': 'vessel, name unknown'}), m.ident({'ship': 'Vessel, Name Unknown'}))
assert m.norm_name('Gas Tara Star') is None  # frozen recall cost
for keep, want in (('TANKER OCEAN', 'tanker ocean'), ('Gas Tara', 'gas tara'), ('OCEAN STAR', 'ocean star'), ('MY TUTOR', 'my tutor'), ('LIBERIAN STAR', 'liberian star'), ('Selene', 'selene'), ('Bulk Shanghai', 'bulk shanghai'), ('Seaways Shipping', 'seaways shipping')): assert m.norm_name(keep) == want, keep
# v3c.10 (#124482): the v3c.9 hole closes by case of the second raw token
for ph in ('tanker attacked', 'Tanker attacked', 'Tanker, attacked', 'Ship hit', 'vessel sinking', 'Carrier seized', 'MV tanker attacked'): assert m.norm_name(ph) is None, ph
for s_, want in (('TANKER OCEAN', 'tanker ocean'), ('Tanker Ocean', 'tanker ocean'), ('tanker Ocean', 'tanker ocean'), ('MV Tanker Ocean', 'tanker ocean'), ('GAS TARA', 'gas tara'), ('Gas Tara', 'gas tara'), ('Bulk Shanghai', 'bulk shanghai'), ('MY TUTOR', 'my tutor'), ('OCEAN STAR', 'ocean star'), ('Selene', 'selene')): assert m.norm_name(s_) == want, (s_, m.norm_name(s_))
assert m.norm_name('tanker ocean') is None  # frozen recall cost: all-lowercase real name
assert m.norm_name('TANKER ATTACKED') == 'tanker attacked' and m.norm_name('Tanker Attacked') == 'tanker attacked'  # open, known: headline case
print(f'{len(NAMES) + len(IMOS) + 2 + 9 + 10 + 14 + 8 + 18 + 15 + 17 + 20} fixtures ok')
