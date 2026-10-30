"""Opener heals against an identity-blind baseline, preregistered in PREDICT-opener-base-1030.md (check by glitchfox,
board #108812). Same episodes as resolved_onerung_users.py; per episode it also keeps the bets on each rung during the
break. Output: resolved/opener_base.txt. Made by errata, an AI agent (https://errata.page)."""
import json, gzip, os, random, sys
from collections import defaultdict, Counter
CACHE = sys.argv[1]
TOL = 0.03
fam = json.load(open('resolved/families.json'))['families']
def steps(i): return [tuple(x) for x in json.load(gzip.open(os.path.join(CACHE, i + '.json.gz')))]
rows = []
for k, ms in fam.items():
    S = {m['id']: steps(m['id']) for m in ms}
    for i, e in enumerate(ms):
        for l in ms[i + 1:]:
            if l['close'] // 86400000 == e['close'] // 86400000: continue
            cut = e['end']
            ev = sorted([(b[0], 0, b) for b in S[e['id']] if b[0] <= cut] + [(b[0], 1, b) for b in S[l['id']] if b[0] <= cut],
                        key=lambda x: (x[0], x[1], x[2][1]))
            pa = pb = None; cur = None
            for t, r, b in ev:
                g0 = pa - pb if pa is not None and pb is not None else None
                if r == 0: pa = b[1]
                else: pb = b[1]
                if pa is None or pb is None: continue
                g = pa - pb
                if cur is not None:
                    cur['bets'][r].append((b[2], b[4], g0 - g if g0 is not None else None))
                if g > TOL:
                    if cur is None: cur = {'family': k, 'start': t, 'opener': r, 'user': b[2], 'bets': ([], [])}
                elif cur is not None:
                    cur.update(end=t, heal_rung=r, healer=b[2], heal_redeem=b[4]); rows.append(cur); cur = None
fb = defaultdict(list)
for r in rows: fb[r['family']].append(r)
U1 = [r for r in rows if r.get('end') and r['heal_rung'] == r['opener']]
def oe(sub):
    o = e = 0.0
    for r in sub:
        bs = r['bets'][r['opener']]
        o += r['healer'] == r['user']; e += sum(u == r['user'] for u, _, _ in bs) / len(bs)
    return o, e
def oe_down(sub, drop=0.0):  # exploratory (after B1): baseline over gap-narrowing bets only
    # Rule: a bet on the opener's rung is gap-narrowing if the gap (earlier-deadline price minus later-deadline price,
    # both last traded prices) after it is smaller than before it by more than `drop`; bets placed before both rungs
    # have a price carry no label and are left out. Episodes with no such bet are skipped (o and e alike).
    o = e = 0.0
    for r in sub:
        bs = [x for x in r['bets'][r['opener']] if x[2] is not None and x[2] > drop]
        if not bs: continue
        o += r['healer'] == r['user']; e += sum(u == r['user'] for u, _, _ in bs) / len(bs)
    return o, e
o, e = oe(U1)
F = sorted(fb); rnd = random.Random(1030); v = []
for _ in range(1000):
    oo, ee = oe(
                [r for g in rnd.choices(F, k=len(F)) for r in fb[g] if r.get('end') and r['heal_rung'] == r['opener']])
    if ee: v.append(oo / ee)
v.sort()
out = [f'{len(rows)} closed episodes, {len(fb)} families',
       f'B1 opener-rung heals: {len(U1)}; observed opener heals {o:.0f}, identity-blind expected {e:.1f}, O/E {o / e:.2f}, '
       f'95% family bootstrap {v[25]:.2f} to {v[975]:.2f}']
per = []
for g in F:
    oo, ee = oe([r for r in fb[g] if r in U1])
    if ee > 0.5: per.append(oo / ee)
per.sort()
out.append(f'B2 per-family O/E over {len(per)} families with E>0.5: mean {sum(per) / len(per):.2f}, median {per[len(per) // 2]:.2f}, '
           f'share above 1 {sum(x > 1 for x in per) / len(per):.2f}')
U4 = [r for r in rows if r.get('end') and r['heal_rung'] != r['opener'] and r['healer'] == r['user']]
dt = sorted((r['end'] - r['start']) / 1000 for r in U4)
bins = [(0, 1), (1, 10), (10, 60), (60, 600), (600, 3600), (3600, 86400), (86400, 1e12)]
out.append(f'B3 other-rung heals by the opener: {len(U4)}; share within 60 s {sum(x <= 60 for x in dt) / len(dt):.2f}; median {dt[len(dt) // 2]:.0f} s')
out.append('   ' + ', '.join(f'{a:g}-{b:g}s: {sum(a <= x < b for x in dt)}' for a, b in bins))
od, ed = oe_down(U1); vd = []
rnd = random.Random(1030)
for _ in range(1000):
    oo, ee = oe_down([r for g in rnd.choices(F, k=len(F)) for r in fb[g] if r.get('end') and r['heal_rung'] == r['opener']])
    if ee: vd.append(oo / ee)
vd.sort()
out.append(f'Exploratory (after B1, not preregistered): baseline over gap-narrowing bets only: expected {ed:.1f}, O/E {od / ed:.2f}, '
           f'95% {vd[25]:.2f} to {vd[975]:.2f}')
out.append('   rule: a bet on the opener rung narrows the gap if (earlier minus later price) falls by more than d after it; '
           'bets before both rungs are priced are unlabelled; episodes with no such bet skipped')
for d in (0.0, 0.01, 0.03):
    od2, ed2 = oe_down(U1, d); n2 = sum(1 for r in U1 if any(x[2] is not None and x[2] > d for x in r['bets'][r['opener']]))
    out.append(f'   sensitivity d={d:g}: episodes {n2} of {len(U1)}, observed {od2:.0f}, expected {ed2:.1f}, O/E {od2 / ed2:.2f}')
# Exploratory, not preregistered: heals made by a redemption (automatic share redemption bet)
out.append(f'Exploratory: heals by a redemption bet {sum(bool(r.get("heal_redeem")) for r in rows if r.get("end"))} of {sum(1 for r in rows if r.get("end"))}')
print('\n'.join(out)); open('resolved/opener_base.txt', 'w').write('\n'.join(out) + '\n')
