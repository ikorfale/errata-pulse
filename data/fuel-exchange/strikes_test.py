# Preregistered test (PREREG-strikes.md, errata-pulse 181afd1): Spearman(S lag-1 week, V per session), Reuters rows only.
import csv
from collections import Counter
from scipy.stats import spearmanr
S=Counter(r['week'] for r in csv.DictReader(open('strikes_weekly.csv')) if r['status']=='confirmed')
V={x['period']:int(x['total_t_per_session'])/1000 for x in csv.DictReader(open('series.csv')) if x['kind']=='week' and not x['source'].startswith('DIFFERENT')}
pair={'2026-09-07..11':'W1','2026-09-14..18':'W2','2026-10-19..23':'W4','2026-10-26..30':'W5','2026-11-02..06':'W6','2026-11-09..13':'W7'}
def run(adj,label):
    s=[S[w]+adj.get(w,0) for w in pair.values()]; v=[V[p] for p in pair]
    rho=spearmanr(s,v)[0]; loo=[round(spearmanr(s[:i]+s[i+1:],v[:i]+v[i+1:])[0],2) for i in range(len(s))]
    print(f"{label}: n={len(s)} S={s} V={v} rho={rho:.2f} LOO={loo}")
run({},'MAIN')
run({'W4':-2},'sens: Novak 14.10 disputed dropped')
run({'W6':1,'W7':1},'sens: Bloomberg source counted')
run({'W2':-0},'(W3 S=%d pairs with excluded NBCA week)'%S['W3'])
