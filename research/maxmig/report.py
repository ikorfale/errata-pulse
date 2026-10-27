"""Did governors' Telegram channels shrink as MAX was pushed? Per channel: posts per week in a common baseline window
(the first 4 full weeks after 30 Mar 2026) vs the last 4 full weeks before collection, and what kind of max.ru link
each post carries. Descriptive only. Run after collect.py: python3 report.py > report.txt
v3 (27.10) after Fable's review of 25.10 (FABLE-REVIEW-1025.txt): asserts every verified handle is present; buckets
by Moscow time; one common window for all channels (a channel without the baseline is listed apart, never pooled);
drops each channel's own collection week; personal channels and official feeds reported apart; Oryol classified by
hand; links classified as own profile (footer), other profile, post link (cross-post or repost) and invite; first
link date printed only when link-free posts precede it; median log ratio with a two-sided sign test."""
import json, os, re, math, datetime as dt
from collections import defaultdict

rows = [l.rstrip('\n').split('\t') for l in open('verified.tsv')][1:]
KEEP = {r[2]: (r[0], r[1]) for r in rows if r[3] == 'yes'}
OFFICIAL = {'kurskadm': 'regional government feed', 'opershtab23': 'Krasnodar operational HQ', 'pul69': 'Tver region official feed'}
HAND = {'Klychkov_Andrey': 'MOVED TO MAX on 1 Apr 2026 (Kommersant 9 Apr, doc/8572550: "all tasks are done by the MAX channel"); '
                          'Telegram since: 6 posts Apr-Jul, last 3 Jul, none in the end window. By hand, not pooled'}

P = [p for p in map(json.loads, open('posts.jsonl')) if p['handle'] in KEEP]
if os.path.exists('posts_deep.jsonl'):   # deep re-walks replace a handle's rows
    D = [p for p in map(json.loads, open('posts_deep.jsonl')) if p['handle'] in KEEP]; dh = {p['handle'] for p in D}
    P = [p for p in P if p['handle'] not in dh] + D
walk = {}
for f in ('walks.jsonl',):
    for l in open(f): w = json.loads(l); walk[w['handle']] = w     # last walk per handle wins (deep re-walk appends)
missing = sorted(set(KEEP) - {p['handle'] for p in P})
assert not missing, f'verified handles with no rows: {missing}'
bad = {h: w['end'] for h, w in walk.items() if h in KEEP and w['end'] not in ('reached date', 'channel start')}

msk = lambda t: dt.datetime.fromisoformat(t[:19]) + dt.timedelta(hours=3)
wk = lambda t: msk(t).date().isocalendar()[:2]
BASE = [(2026, w) for w in range(14, 18)]                       # 30 Mar .. 26 Apr, Moscow time
last_full = {h: dt.date.fromisoformat(w['collected'][:10]).isocalendar()[:2] for h, w in walk.items()}
END_W = min(v for h, v in last_full.items() if h in KEEP)       # every channel collected in this ISO week or later
END = [(END_W[0], END_W[1] - k) for k in range(4, 0, -1)]      # the 4 full weeks before it

def kind(u, own):
    u = re.sub(r'^https?://(www\.)?', '', u.split('?')[0]).rstrip(').,!?»').lower(); parts = u.split('/')
    if len(parts) > 1 and parts[1] == 'join': return 'invite'
    if len(parts) > 2 and parts[2]: return 'post'
    return 'own' if parts[1:] and parts[1] in own else 'other'

by = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
prof = defaultdict(lambda: defaultdict(int))
for p in P:
    for u in p['max_urls']:
        u = re.sub(r'^https?://(www\.)?', '', u.split('?')[0]).rstrip(').,!?»').lower().split('/')
        if len(u) == 2: prof[p['handle']][u[1]] += 1
own = {h: {max(c, key=c.get)} for h, c in prof.items()}         # the channel's most linked profile = its own MAX channel
for p in P:
    w = wk(p['t']); c = by[p['handle']][w]; c['n'] += 1
    ks = {kind(u, own.get(p['handle'], set())) for u in p['max_urls']}
    for k in ks: c[k] += 1
    c['any'] += bool(ks)

def win(h, W):
    n = sum(by[h][w]['n'] for w in W)
    return n / 4, {k: sum(by[h][w][k] for w in W) / max(1, n) for k in ('any', 'own', 'other', 'post', 'invite')}

oldest = {}
for p in P: oldest[p['handle']] = min(oldest.get(p['handle'], p['t']), p['t'])
first = {}
for p in sorted(P, key=lambda p: p['t']):
    if p['max_urls'] and p['handle'] not in first:
        before = sum(q['handle'] == p['handle'] and q['t'] < p['t'] for q in P)
        first[p['handle']] = p['t'][:10] if before >= 20 else 'before window'

def sign_p(k, n):
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n) if n else 1.0

def sign_ci(n):
    # largest k with P(Bin(n, .5) <= k) <= .025: the CI is the (k+1)-th smallest .. (k+1)-th largest
    k, c = -1, 0.0
    while True:
        c2 = c + math.comb(n, k + 1) / 2 ** n
        if c2 > .025: return max(k, 0)   # index of the (k+1)-th order statistic
        k += 1; c = c2

print(f'Baseline weeks {BASE[0][1]}-{BASE[-1][1]} (30 Mar-26 Apr), end weeks {END[0][1]}-{END[-1][1]} of 2026, Moscow time.')
print('posts/week base -> end, log ratio; link shares base -> end: own MAX channel (footer), post links (cross-post or repost)')
print('Note: the end window follows the September 2026 election season, when governors\' output normally dips; no VK control yet.\n')
groups = {'personal': [], 'official': []}
for h in sorted(KEEP, key=lambda h: (h in OFFICIAL, KEEP[h][0])):
    region, role = KEEP[h]
    if h in HAND: print(f'{h:22} {region:15} {HAND[h]}'); continue
    if h in bad: print(f'{h:22} {region:15} walk ended by {bad[h][:40]}: not used'); continue
    if oldest[h] >= '2026-03-30': print(f'{h:22} {region:15} channel starts {oldest[h][:10]} (successor): no baseline, not pooled'); continue
    n0, s0 = win(h, BASE); n1, s1 = win(h, END)
    lr = math.log((n1 + .5) / (n0 + .5))
    groups['official' if h in OFFICIAL else 'personal'].append(lr)
    tag = f' [{OFFICIAL[h]}]' if h in OFFICIAL else ''
    print(f'{h:22} {region:15} {n0:5.1f} -> {n1:5.1f}  {lr:+.2f}   own {s0["own"]:.2f}->{s1["own"]:.2f}  post {s0["post"]:.2f}->{s1["post"]:.2f}  other {s0["other"]:.2f}->{s1["other"]:.2f}  first link {first.get(h, "-")}{tag}')
for g, v in groups.items():
    if not v: continue
    v = sorted(v); med = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
    down = sum(x < 0 for x in v); n = sum(x != 0 for x in v)
    lo, hi = (v[sign_ci(len(v))], v[len(v) - 1 - sign_ci(len(v))]) if len(v) >= 6 else (v[0], v[-1])
    print(f'\n{g}: {len(v)} channels, median log ratio {med:+.2f} (x{math.exp(med):.2f}, sign-based 95% CI x{math.exp(lo):.2f}..x{math.exp(hi):.2f}), {down} of {n} down, two-sided sign test p = {sign_p(down, n):.3f}')
print(f'\nposts {len(P)}; verified handles {len(KEEP)}; walks ended by error: {sorted(bad) or "none"}')
