"""Cleveland Fed inflation nowcast vs the rounded one-decimal CPI print (what Kalshi settles on).
Data: nowcast_month_<vintage>.json from clevelandfed.org (one chart per target month, daily nowcast values).
'Actual' in that file is Cleveland's current-vintage value, not necessarily the first print."""
import json, math, sys, statistics as st
from decimal import Decimal, ROUND_HALF_UP
# fetch: curl -o nowcast_month.json 'https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json?sc_lang=en'
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'nowcast_month.json'))
r1 = lambda x: float(Decimal(str(x)).quantize(Decimal('0.1'), ROUND_HALF_UP))
rows = []
for c in d:
    m = c['chart']['subcaption']
    labels = [x['label'] for x in c['categories'][0]['category']]
    S = {s['seriesname']: s['data'] for s in c['dataset']}
    for name, act in (('CPI Inflation', 'Actual CPI Inflation'), ('Core CPI Inflation', 'Actual Core CPI Inflation')):
        a = [(i, float(x['value'])) for i, x in enumerate(S.get(act, [])) if x.get('value') not in ('', None)]
        if not a: continue
        ia, av = a[0]
        nc = [(i, float(x['value'])) for i, x in enumerate(S[name]) if x.get('value') not in ('', None) and i < ia]
        if not nc: continue
        last = nc[-1][1]
        early = nc[max(0, len(nc) - 15)][1]  # ~15 business days before the release
        rows.append(dict(month=m, measure='headline' if name.startswith('CPI') else 'core', last=last, early=early, actual=av))
out = []
for meas in ('headline', 'core'):
    R = [r for r in rows if r['measure'] == meas]
    for k in ('last', 'early'):
        diff = [round((r1(r[k]) - r1(r['actual'])) * 10) for r in R]
        err = [r[k] - r['actual'] for r in R]
        n = len(R)
        exact = sum(1 for x in diff if x == 0); one = sum(1 for x in diff if abs(x) == 1); two = n - exact - one
        out.append(f"{meas:8s} {k:5s} n={n} months {R[0]['month']}..{R[-1]['month']}: rounded exact {exact} ({exact/n:.0%}), off by 0.1 {one} ({one/n:.0%}), off by >=0.2 {two} ({two/n:.0%}); "
                   f"raw error mean {st.mean(err):+.3f} sd {st.pstdev(err):.3f} pp; nowcast too low {sum(1 for x in diff if x<0)}, too high {sum(1 for x in diff if x>0)}")
    # since 2022: recent regime
    R2 = [r for r in R if r['month'] >= '2022-01']
    diff = [round((r1(r['last']) - r1(r['actual'])) * 10) for r in R2]
    out.append(f"{meas:8s} last  since 2022-01 n={len(R2)}: exact {sum(1 for x in diff if x==0)}, off 0.1 {sum(1 for x in diff if abs(x)==1)}, off >=0.2 {sum(1 for x in diff if abs(x)>=2)}")
    # threshold view: Kalshi 'above T' strictly greater; if you bet the side the nowcast points to on the threshold just under/over it
    sd = st.pstdev([r['last'] - r['actual'] for r in R])
    near = [r for r in R if abs(r['last'] - (math.floor(r['last'] * 10) / 10 + 0.05)) < 0.025]
    exact_near = sum(1 for r in near if r1(r['last']) == r1(r['actual']))
    out.append(f"{meas:8s} last  nowcast within 0.025 of a rounding edge (x.x5): n={len(near)}, rounded exact {exact_near}")
print('\n'.join(out))
