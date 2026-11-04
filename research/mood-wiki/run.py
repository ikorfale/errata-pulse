"""Mood H5 wiki test, as frozen in PREREG.md (3531524). Usage: run.py MOD_CLAIMS.jsonl [--fix]
--fix: the post-freeze exposure correction in POSTFREEZE.md; window then ends on the last fetched bulletin date."""
import json, re, sys, collections, urllib.request, urllib.parse, datetime as dt
import numpy as np
def spearmanr(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return (np.corrcoef(ra, rb)[0, 1],)
UA = {"User-Agent": "errata-mood/1 (errata@agentmail.to; AI agent research)"}
FIX = '--fix' in sys.argv
S, E = '2025-11-09', ('2026-10-19' if FIX else '2026-11-01')
FAM = {'primary': ['Бомбоубежище', 'Гражданская оборона', 'Автоматизированная система централизованного оповещения', 'Эвакуация'],
       'air_defence': ['Противовоздушная оборона', 'Беспилотный летательный аппарат', 'Военное применение беспилотных летательных аппаратов', 'Shahed 136']}
days = [str(dt.date.fromisoformat(S) + dt.timedelta(i)) for i in range((dt.date.fromisoformat(E) - dt.date.fromisoformat(S)).days + 1)]
def views(t):
    u = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/ru.wikipedia/all-access/user/"
         + urllib.parse.quote(t.replace(' ', '_'), safe='') + f"/daily/{S.replace('-','')}/{E.replace('-','')}")
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
        return {f"{i['timestamp'][:4]}-{i['timestamp'][4:6]}-{i['timestamp'][6:8]}": i['views'] for i in json.load(r)['items']}
# exposure: the mod_regions_2025.py parser, per date
import os
code = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mod_regions_2025.py')).read()  # copy of the frozen parser (#385)
pre = code.split('tot = collections.Counter()')[0].split("START, END =")[0]
exec(pre)  # W, TENS, NUM, ITEM, SING, TV from the frozen parser
exec(code.split("START, END =")[1].split('\n', 1)[1].split('tot = collections.Counter()')[0])  # dictionaries
expo = collections.Counter()
for l in open(sys.argv[1]):
    x = json.loads(l); d = x['dt'][:10]
    if not (S <= d <= E): continue
    t = TENS.sub(lambda m: str(TV[m.group(1).lower()] + (W[m.group(2).lower()] if m.group(2) else 0)), x['text'])
    if 'беспилот' not in t and 'БПЛА' not in t: continue
    if re.search(r'прошедш\w+ недел|в течение недели|за неделю', t, re.I): continue
    items = ITEM.findall(t)
    if not items and not re.search(r'[▫▪•]', t):
        m = re.search(NUM + r'\s+украинск\w+\s+беспилотн[^.:]*?над\s+территорией\s+((?:(?!\s+и\s)[^,.;\n(])+)', t, re.I)
        if m: items = [(m.group(1), 'территорией', m.group(2))]
    if not items:
        m = SING.search(t)
        if m: items = [('1', m.group(1), m.group(2))]
    if not items and FIX:  # POSTFREEZE.md: national headline total, the format the MoD uses since April 2026
        m = re.search(NUM + r'\s+украинск\w+\s+беспилотн[^.:]*?над\s+(?:территори(?:ей|ями)|акватори)', t, re.I)
        if m: items = [(m.group(1), 'national', '')]
    for n, kind, reg in items: expo[d] += int(n) if n.isdigit() else W[n.lower()]
X = np.array([expo[d] for d in days], float)
print(f'exposure: {int(X.sum())} claimed UAVs over {len(days)} days, {int((X>0).sum())} days >0, median {np.median(X):.0f}, max {X.max():.0f} on {days[int(X.argmax())]}')
def resid(v):
    y = np.log1p(v); r = np.array([y[i] - np.median(y[max(0,i-14):i+15]) for i in range(len(y))])
    wd = np.array([dt.date.fromisoformat(d).weekday() for d in days])
    for k in range(7): r[wd==k] -= r[wd==k].mean()
    return r
rx = resid(X)
for fam, ts in FAM.items():
    Y = np.zeros(len(days)); miss = 0
    for t in ts:
        v = views(t); Y += np.array([v.get(d, 0) for d in days]); miss += sum(d not in v for d in days)
    ry = resid(Y); rho = spearmanr(rx, ry)[0]
    pl = [spearmanr(np.roll(rx, L), ry)[0] for L in list(range(-120, -13)) + list(range(14, 121))]
    p = np.mean(np.abs(pl) >= abs(rho))
    top = np.argsort(-X)[:10]
    lift = np.exp(ry[top]).mean()
    print(f'{fam}: views median/day {np.median(Y):.0f}, missing day-article cells {miss}; rho {rho:+.3f}, placebo |rho| p = {p:.3f} '
          f'(n lags {len(pl)}, placebo |rho| 95th pct {np.percentile(np.abs(pl),95):.3f}); 10 heaviest days: views x{lift:.2f} of local norm')
