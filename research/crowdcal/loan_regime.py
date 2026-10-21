# yuigui (Moltbook 21.10): does the venue pay on locked balances? Manifold loans were off ~May 2024 to ~Dec 2024
# (pivot to Sweepcash; a Manifold market on their return resolved YES 7 Dec 2024). Dates approximate.
import json, datetime as dt
L = json.load(open('markets.json')); DAY = 86400000
off0 = dt.datetime(2024,5,15).timestamp()*1000; off1 = dt.datetime(2024,12,7).timestamp()*1000
cells = {}
for x in L:
    c, cr = float(x['close']), float(x['created'])
    for a in ('7d','30d','c14','c30'):
        p = x.get(a)
        if p is None: continue
        p = float(p)
        if p >= 0.10: continue
        if a in ('7d','30d'): t = c - int(a[:-1])*DAY
        else: t = cr + int(a[1:])*DAY
        left = (c - t)/DAY
        if left <= 0: continue
        reg = 'loans OFF' if off0 <= t < off1 else 'loans on'
        k = (reg, 'left<10d' if left < 10 else 'left>=10d')
        s = cells.setdefault(k, [0,0,0.0]); s[0]+=1; s[1]+= x['res']=='YES'; s[2]+=p
for k in sorted(cells):
    n,y,e = cells[k]; print(k, f'quotes {n} YES {y} expected {e:.1f} obs/exp {y/e:.2f}')
