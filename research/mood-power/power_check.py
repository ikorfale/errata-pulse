"""Plan #349 power check: can the FOM weekly 'anxious' share see shocks? Shock list fixed before looking at the series
(20.10 11:35 UTC). Week used = first FOM wave whose last fieldwork day (the series date, a Sunday) is >= shock + 2 days.
Effect = anxious(that wave) - mean(anxious of the 4 waves before the shock); peak = max over the first 3 waves after.
Null: the same statistic at every week of the series (weeks within 4 of a listed shock excluded), as a percentile."""
import json, datetime as dt, numpy as np
S = json.load(open('fom/archive.json'))['series']
D = [dt.date.fromisoformat(r['date']) for r in S]; A = np.array([r['anxious'] for r in S], float); K = np.array([r['dk'] for r in S], float)
SHOCKS = [('2022-02-24', 'big', 'invasion of Ukraine'), ('2022-09-21', 'big', 'partial mobilisation'),
          ('2023-06-24', 'big', 'Prigozhin mutiny'), ('2024-03-22', 'big', 'Crocus City Hall attack'),
          ('2024-08-06', 'big', 'Ukrainian incursion into Kursk'),
          ('2023-05-30', 'strike', 'drone attack on Moscow (first on residential Moscow)'),
          ('2023-12-30', 'strike', 'Belgorod city centre shelling, 25 dead'),
          ('2025-03-11', 'strike', 'largest drone raid on Moscow to date (337 drones claimed)')]
def stat(i):
    if i < 4 or i + 3 > len(A): return None
    base = A[i - 4:i].mean(); return A[i] - base, A[i:i + 3].max() - base, K[i] - K[i - 4:i].mean()
null_idx = [i for i in range(len(A)) if stat(i) and all(abs((D[i] - dt.date.fromisoformat(s)).days) > 35 for s, *_ in SHOCKS)]
nul = np.array([stat(i) for i in null_idx])
d1 = np.diff(A); print(f"{len(A)} waves {D[0]}..{D[-1]}; week-to-week change of 'anxious': sd {d1.std(ddof=1):.2f} pts, |change|>=5 in {np.mean(abs(d1)>=5)*100:.1f}% of weeks")
print(f"null (non-shock weeks, n={len(nul)}): effect 95th pct {np.percentile(nul[:,0],95):+.1f}, 99th {np.percentile(nul[:,0],99):+.1f}; peak-3w 95th {np.percentile(nul[:,1],95):+.1f}")
print(f"{'shock':52s} {'wave':>10} {'effect':>7} {'pct':>5} {'peak3w':>7} {'pct':>5} {'dk':>5}")
for s, kind, name in SHOCKS:
    sd = dt.date.fromisoformat(s); i = next(j for j, d in enumerate(D) if d >= sd + dt.timedelta(days=2))
    e, p, k = stat(i)
    print(f"{kind:6s} {s} {name[:33]:33s} {D[i]} {e:+7.1f} {np.mean(nul[:,0] < e)*100:5.0f} {p:+7.1f} {np.mean(nul[:,1] < p)*100:5.0f} {k:+5.1f}")
# pooled single strikes: chance that the mean effect of 3 random non-shock weeks reaches theirs; strikes needed for 80% power
rng = np.random.default_rng(349); st = [stat(next(j for j, d in enumerate(D) if d >= dt.date.fromisoformat(s) + dt.timedelta(days=2)))[0] for s, k, _ in SHOCKS if k == 'strike']
m = np.mean(st); draws = rng.choice(nul[:, 0], (100000, len(st))).mean(1)
sd0 = nul[:, 0].std(ddof=1); n80 = int(np.ceil(((1.645 + 0.84) * sd0 / m) ** 2))
print(f"pooled strikes: mean effect {m:+.2f} (n={len(st)}), one-sided p vs random weeks {np.mean(draws >= m):.3f}; null sd {sd0:.2f}; "
      f"if the true strike effect were {m:+.1f}, ~{n80} independent strike weeks for 80% power (one-sided 5%)")

# v2 after Fable's review (20.10): treatment wave = first wave whose fieldwork start (series date - 2 d) is 1..9 days after
# the shock, else the shock is unmeasurable; baseline = mean of the 2 preceding waves; placebo = all waves of the same
# calendar year, excluding +-5 weeks around every listed shock. Percentile within the year, not pooled across eras.
print("\nv2 (Fable review): 2-wave baseline, fieldwork start 1..9 d after shock, same-year placebo")
def stat2(i): return A[i] - A[i - 2:i].mean() if i >= 2 else None
near = lambda i: any(abs((D[i] - dt.date.fromisoformat(s)).days) <= 35 for s, *_ in SHOCKS)
for s, kind, name in SHOCKS:
    sd = dt.date.fromisoformat(s)
    i = next((j for j, d in enumerate(D) if 1 <= (d - dt.timedelta(days=2) - sd).days <= 9), None)
    if s == '2023-06-24': i = next(j for j, d in enumerate(D) if d == dt.date(2023, 6, 25))   # wave fielded during the mutiny
    if i is None: print(f"{kind:6s} {s} {name[:33]:33s} no wave within 9 days: unmeasurable"); continue
    pl = np.array([stat2(j) for j in range(2, len(A)) if D[j].year == D[i].year and not near(j)])
    e = stat2(i); print(f"{kind:6s} {s} {name[:33]:33s} {D[i]} {e:+6.1f}  pct in {D[i].year} {np.mean(pl < e)*100:4.0f} (placebo n={len(pl)}, 95th {np.percentile(pl,95):+.1f})")
