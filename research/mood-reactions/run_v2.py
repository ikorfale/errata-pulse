#!/usr/bin/env python3
"""Mood v2 (#536): reader fear after deadly strikes, day-level rank over a register of events, strictly by PREREG-v2.md
(sha256 in FROZEN-v2.sha256). Written 27.10 after the freeze, before any reaction value of the test windows was read.

  run_v2.py check   pre-read checks only: hashes, fetch coverage, alarm-emoji SET per channel, block-0 coverage,
                    empty blocks, unparsed reactions. Prints no reaction count and no share.
  run_v2.py run     the test: primary (alarm), secondary (grief), placebo for both, without-Belgorod, manipulation check.
  --data DIR        data directory (default data_v2r: re-fetch that keeps custom emoji and paid stars, parse_v2r.py)
  --channels FILE   region<TAB>username overrides (robustness run on the 2nd eligible channel, PREREG "Ranking date")

Decisions the PREREG left to code, fixed here before reading (each one says why):
  D1 hour 0 = first official statement that people died. Events 5 and 10: first notice said only "есть пострадавшие"
     (injured, no deaths), so hour 0 = first death number (civ_verify_b.tsv col 3). Events 2 and 15: first notice
     already said "есть погибшие" (deaths, no number): that is a death statement, hour 0 = the notice.
     Event 12: the opershtab post 08:15:31Z (exact time); the governor's ~08:13Z is read off a preview, not exact.
  D2 block k = [hour0 + 24k h, hour0 + 24(k+1) h), k = -29..0; times compared in UTC.
  D3 drops are applied in the PREREG's order: fetch coverage (abort, re-fetch), block-0 coverage (no strike post),
     floor (computed on baseline blocks only, before block 0's value is computed), block 0 missing.
  D4 the placebo is run on the events that pass block-0 coverage (coverage is about the event, not its values);
     its own floor over blocks -29..-16; block -15 missing drops the event from the placebo, reported. Also printed,
     descriptive only: the placebo on just the events that entered the test. Rostov 17's placebo baseline holds
     27.07, event 11's block 0 (no rule changes that; reported).
  D5 a post's reaction total includes every key (plain, custom:<id>, paid). Posts with unparsed reaction badges
     are counted and reported; the check aborts if any post in a test window has one.
  D6 classification runs on the full post text (data_v2r keeps it whole; data_v2 cut it at 600 characters).
  D7 null: block 0's mid-rank from the top is uniform on 1..n (n = blocks present for that event); observed mid-ranks
     may be halves, so the convolution runs on doubled ranks; p = P(S_null <= S_obs), one-sided (low rank = more fear).
  D8 register: events of civ_verify_b.tsv with an official toll >= 4 within 72 h, minus Moscow obl (6: toll 3; 13: no
     channel), minus Belgorod 14, 18, 20 (baseline walk #500, belg_baseline.txt); the 14-day same-region exclusion is
     checked here in code. Event 2 (Bryansk) stays in the list and drops by the block-0 rule, as the PREREG says.
"""
import sys, os, json, glob, io, hashlib, contextlib, argparse
import datetime as dt
from fractions import Fraction

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

FROZEN = {l.split()[1]: l.split()[0] for l in open(f'{D}/FROZEN-v2.sha256') if l.strip()}
for name in ('PREREG-v2.md', 'regex_v2_check.py'):
    assert sha(f'{D}/{name}') == FROZEN[name], f'{name} changed since the freeze'

_cwd = os.getcwd(); os.chdir(D)
with contextlib.redirect_stdout(io.StringIO()):     # the frozen module runs its 50-post check on import; silence it
    from regex_v2_check import FOOTER, URL, letters, STRIKE_V2
os.chdir(_cwd)

UTC = dt.timezone.utc
def T(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(UTC)

# id, region, hour 0 (D1)
EVENTS = [
    ('1', 'Smolensk', '2026-02-25T09:00:03Z'), ('2', 'Bryansk', '2026-03-10T16:02:30Z'),
    ('4', 'Crimea', '2026-05-05T21:10:07Z'), ('5', 'Ryazan', '2026-05-15T02:54:34Z'),
    ('8', 'Tambov', '2026-07-18T02:36:15Z'), ('9', 'Belgorod', '2026-07-20T12:11:46Z'),
    ('10', 'Kirov', '2026-07-24T09:49:18Z'), ('11', 'Rostov', '2026-07-27T02:32:54Z'),
    ('12', 'Krasnodar', '2026-08-03T08:15:31Z'), ('15', 'Tatarstan', '2026-08-10T05:37:18Z'),
    ('17', 'Rostov', '2026-08-16T04:13:26Z'), ('21', 'Krasnodar', '2026-09-09T05:48:55Z'),
]
CHANNELS = {'Smolensk': 'inc_smol', 'Bryansk': 'br_gorod', 'Crimea': 'chp_crimea', 'Ryazan': 'overheardryazan',
            'Tambov': 'tambov_smi', 'Belgorod': 'belgorod_granica', 'Kirov': 'kirov_bezcenz',
            'Rostov': 'privet_rostov_ru', 'Krasnodar': 'krasnodarkray1', 'Tatarstan': 'kazancity'}  # usernames-v2.tsv
CHANNELS['Ryazan'] = 'ryazan_smi'   # 27.10: overheardryazan has no alarm emoji in blocks -21..-15 -> next eligible (#3)
# Bryansk keeps br_gorod: zero posts in the window, the event drops by block-0 coverage as the frozen pre-freeze note
# says (PREREG-v2.md "Pre-freeze results"); bryansk_smi enters only the robustness run (POSTFREEZE-v2.md, Fable review 1).

ALARM = {'\U0001F631', '\U0001F628'}
GRIEF = {'\U0001F622', '\U0001F62D'}
MIN_REACT, FLOOR, LETTERS = 30, 50, 30

def classify(text):
    """'strike' | 'other' | 'excluded' (no strike word and under 30 letters once footer, URLs and handles are gone)."""
    t = FOOTER.sub('', text or '')
    if STRIKE_V2.search(t): return 'strike'
    return 'excluded' if letters(t) < LETTERS else 'other'

def load(data, ch):
    p = f'{data}/{ch}.jsonl'
    if not os.path.exists(p): return []
    rows = [json.loads(l) for l in open(p, encoding='utf-8')]
    for r in rows:
        r['t'] = T(r['time']); r['cls'] = classify(r.get('text', ''))
        r['n'] = sum(r['reacts'].values())
    return rows

def block_of(t, h0):
    return (t - h0) // dt.timedelta(hours=24)       # floor division: block k holds [h0+24k, h0+24(k+1))

def blocks(rows, h0, lo=-29, hi=0):
    out = {k: [] for k in range(lo, hi + 1)}
    for r in rows:
        k = block_of(r['t'], h0)
        if lo <= k <= hi: out[k].append(r)
    return out

def primary_posts(posts): return [p for p in posts if p['cls'] == 'other' and p['n'] >= MIN_REACT]

def value(posts, fear):
    q = primary_posts(posts)
    if not q: return None                           # missing block
    return sum(v for p in q for e, v in p['reacts'].items() if e in fear) / sum(p['n'] for p in q)

def fear_count(posts, fear):
    return sum(v for p in primary_posts(posts) for e, v in p['reacts'].items() if e in fear)

def midrank_top(x, others):
    """Mid-rank of x among x + others, 1 = highest."""
    above = sum(1 for o in others if o > x); ties = sum(1 for o in others if o == x)
    return Fraction(2 * above + ties + 2, 2)

def p_value(obs_ranks, ns):
    """Exact P(sum of independent uniform{1..n_i} <= sum of observed mid-ranks), on doubled ranks."""
    dist = {0: Fraction(1)}
    for n in ns:
        nd = {}
        for s, pr in dist.items():
            for r in range(1, n + 1):
                nd[s + 2 * r] = nd.get(s + 2 * r, 0) + pr / n
        dist = nd
    obs2 = int(2 * sum(obs_ranks))
    return float(sum(pr for s, pr in dist.items() if s <= obs2)), dist

def register():
    ev = [(i, reg, T(h)) for i, reg, h in EVENTS]
    for i, reg, h0 in ev:                           # 14-day same-region exclusion (PREREG "Event register")
        prev = [j for j, r2, t2 in ev if r2 == reg and dt.timedelta(0) < h0 - t2 <= dt.timedelta(days=14)]
        assert not prev, f'event {i} has an included event {prev} in {reg} in the previous 14 days'
    return ev

def check(data, chans):
    print(f'# run_v2 check, data={data}, PREREG sha ok, regex module sha ok; no reaction counts printed')
    ev = register(); ok = True; first = {}
    for i, reg, h0 in sorted(ev, key=lambda e: e[2]): first.setdefault(reg, (i, h0))
    for i, reg, h0 in ev:
        ch = chans[reg]; rows = load(data, ch)
        if not rows: print(f'event {i:>2} {reg:10} {ch}: NO DATA FILE'); ok = False; continue
        start = h0 - dt.timedelta(hours=24 * 29)
        reach = min(r['t'] for r in rows) < start
        b = blocks(rows, h0)
        unparsed = sum(r.get('unparsed_reactions', 0) for k in b for r in b[k])
        empty = [k for k in b if not b[k]]
        s0 = sum(1 for r in b[0] if r['cls'] == 'strike')
        print(f'event {i:>2} {reg:10} {ch:18} h0 {h0:%Y-%m-%d %H:%M}  fetch reaches block -29: {reach}  '
              f'posts -29..0: {sum(len(v) for v in b.values())}  empty blocks: {empty or "none"}  '
              f'block-0 strike posts: {s0} -> {"covered" if s0 else "NOT COVERED (drops)"}  unparsed badges: {unparsed}')
        if not reach or unparsed: ok = False
    for reg, (i, h0) in first.items():
        rows = load(data, chans[reg]); b = blocks(rows, h0, -21, -15)
        keys = {e for k in b for r in b[k] for e in r['reacts']}
        npost = sum(len(v) for v in b.values())
        verdict = ('no posts (event drops by block-0 coverage)' if not npost else
                   'present' if keys & ALARM else 'ABSENT -> next eligible channel')
        print(f'alarm-emoji set, {reg:10} {chans[reg]:18} blocks -21..-15 of event {i}: {verdict}')
        if npost and not keys & ALARM: ok = False
    print('CHECK', 'PASSED' if ok else 'FAILED: re-fetch before reading anything')
    return ok

def test(ev_rows, fear, lo_base, hi_base, ev_block, label, floor_name):
    """One rank test. ev_rows: [(id, region, rows, h0)]. Baseline blocks lo_base..hi_base, event block ev_block."""
    ranks, ns, lines, entered = [], [], [], []
    for i, reg, rows, h0 in ev_rows:
        b = blocks(rows, h0)
        base = {k: b[k] for k in range(lo_base, hi_base + 1)}
        fc = sum(fear_count(v, fear) for v in base.values())
        if fc < FLOOR:                               # floor first, before the event block's value exists
            lines.append(f'  event {i:>2} {reg:10} drops: {floor_name} floor {fc} < {FLOOR} over blocks {lo_base}..{hi_base}')
            continue
        x = value(b[ev_block], fear)
        if x is None:
            lines.append(f'  event {i:>2} {reg:10} drops: block {ev_block} missing (no primary-cell post with >= {MIN_REACT} reactions)')
            continue
        bv = [v for v in (value(base[k], fear) for k in base) if v is not None]
        r = midrank_top(x, bv); n = len(bv) + 1
        ranks.append(r); ns.append(n); entered.append(i)
        lines.append(f'  event {i:>2} {reg:10} block {ev_block} share {x:.4f}  baseline median '
                     f'{sorted(bv)[len(bv)//2] if bv else float("nan"):.4f}  rank {float(r):g} of {n}  ({floor_name} floor {fc})')
    print(f'## {label}: {len(ranks)} events enter: {",".join(entered)}')
    print('\n'.join(lines))
    if len(ranks) < 2:
        print(f'  -> not testable (needs >= 2 events; PREREG "Minimum"), not a null'); return None, entered
    p, dist = p_value(ranks, ns)
    exp = sum(Fraction(n + 1, 2) for n in ns)
    print(f'  statistic S = {float(sum(ranks)):g} (null mean {float(exp):g}; mean rank {float(sum(ranks))/len(ranks):.2f}, '
          f'null mean rank {float(exp)/len(ranks):.2f}), one-sided exact p = {p:.4f}')
    return p, entered

def run(data, chans):
    if not check(data, chans): sys.exit('check failed: nothing read')
    ev = register(); covered = []
    print('\n# block-0 coverage (manipulation check with a consequence) and strike-post counts')
    for i, reg, h0 in ev:
        rows = load(data, chans[reg]); b = blocks(rows, h0)
        s = [sum(1 for r in b[k] if r['cls'] == 'strike') for k in range(-14, 1)]
        base_mean = sum(s[:-1]) / 14
        print(f'  event {i:>2} {reg:10} strike posts block 0: {s[-1]}, baseline mean {base_mean:.1f}/block')
        if s[-1]: covered.append((i, reg, rows, h0))
        else: print(f'  event {i:>2} {reg:10} drops: not covered (no strike post in block 0)')
    res = {}
    for name, fear in (('alarm', ALARM), ('grief', GRIEF)):
        tag = 'PRIMARY' if name == 'alarm' else 'SECONDARY'
        print()
        res[(name, 'test')], ent = test(covered, fear, -14, -1, 0, f'{tag} {name}: block 0 vs blocks -14..-1', name)
        res[(name, 'placebo')], _ = test(covered, fear, -29, -16, -15, f'PLACEBO {name}: block -15 vs blocks -29..-16', name)
        test([e for e in covered if e[0] in ent], fear, -29, -16, -15,
             f'PLACEBO {name}, only the events that entered the test (D4 note, descriptive)', name)
        test([e for e in covered if e[1] != 'Belgorod'], fear, -14, -1, 0, f'{tag} {name} without Belgorod', name)
    print('\n# verdict (PREREG: claim only if test p <= 0.05 AND placebo p > 0.05)')
    for name in ('alarm', 'grief'):
        p, pl = res[(name, 'test')], res[(name, 'placebo')]
        if p is None: v = 'not testable'
        elif pl is None: v = f'p = {p:.4f}, placebo not testable -> no claim'
        elif pl <= 0.05: v = f'p = {p:.4f}, placebo p = {pl:.4f} <= 0.05 -> no claim (method fires on ordinary days)'
        elif p <= 0.05: v = f'p = {p:.4f} <= 0.05, placebo p = {pl:.4f} -> effect claimed'
        else: v = f'p = {p:.4f} > 0.05, placebo p = {pl:.4f} -> bounded null (no effect of the size the design can see)'
        print(f'  {name}: {v}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['check', 'run'])
    ap.add_argument('--data', default=f'{D}/data_v2r'); ap.add_argument('--channels')
    a = ap.parse_args(); chans = dict(CHANNELS)
    if a.channels:
        chans.update(dict(l.rstrip('\n').split('\t')[:2] for l in open(a.channels) if l.strip() and not l.startswith('#')))
    (check if a.mode == 'check' else run)(a.data, chans)
