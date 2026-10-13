"""Approximate map positions (errata, 13 Oct 2026) for ledger lines without coordinates: a named port or area gives a
point just offshore of it, with a small seeded jitter so markers do not hide each other. Marked coords_from=
'area-approx (errata)'; these are drawing positions, not where the ship was. Lines with no named place stay off the map."""
import json, random
random.seed(20261013)
A = [('Taganrog', 47.0, 38.4), ('Bystroe', 45.3, 29.85), ('Danube', 45.3, 29.85), ('Chornomorsk', 46.25, 30.75),
     ('Odesa', 46.35, 30.95), ('Novorossiysk', 44.6, 37.65), ('CPC', 44.62, 37.6), ('Tuapse', 44.05, 38.95),
     ('Sochi', 43.5, 39.6), ('Gemlik', None, None)]
L = [json.loads(l) for l in open('ledger.jsonl') if l.strip()]
n = 0
for r in L:
    if r.get('aggregate') or r.get('lat') is not None or r['zone'] in ('unknown', 'open-sea'): continue
    for key, la, lo in A:
        if key.lower() in r['where'].lower() and la is not None:
            r['lat'] = round(la + random.uniform(-0.18, 0.18), 3); r['lon'] = round(lo + random.uniform(-0.25, 0.25), 3)
            r['coords_from'] = 'area-approx (errata)'; n += 1; break
open('ledger.jsonl', 'w').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in L))
print('placed', n)
