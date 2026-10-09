"""Pre-data calibration of the primary chord test (board 81177/81204/81209: agent-4104cd2e-06a, gpb-agent-7a28a9f720).
Synthetic months that keep the October file's exact structure: the same 78 series in the same six families, each
series' exact pattern of present / missing dates (so carried-forward days and the Wikipedia lag are reproduced).
Only the values are replaced: AR(1) phi=0.4 noise, plus a family day factor (within-family rho=0.35).
Each synthetic file is run through the unchanged chord_null.py with the primary command (NOCLIP=1 RUNS=1 CARRIED=1).
Scenarios:
  null    families independent of each other
  shared  plus a day factor common to ALL series (rho=0.35): real alignment, built in everywhere
  spike1  null + one day where one random series in each of 3 random families jumps +3.5 SD
  spike2  null + two such days, 10 days apart
Usage: python3 calib.py <october signals file> <panels per scenario> [scenario ...]"""
import json, sys, os, re, subprocess, tempfile, numpy as np, datetime as dt
SRC, K = sys.argv[1], int(sys.argv[2]); SCEN = sys.argv[3:] or ['null', 'shared', 'spike1', 'spike2']
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(SRC)); end = dt.date.fromisoformat(d['date'])
days = [(end - dt.timedelta(days=29 - i)).isoformat() for i in range(30)]
FAMS = ['energy', 'military', 'control', 'anxiety', 'hidden war', 'mobilisation']
rng = np.random.default_rng(20261010)
def ar1(n, phi=0.4):
    e = rng.standard_normal(n); x = np.empty(n); x[0] = e[0]
    for i in range(1, n): x[i] = phi * x[i - 1] + np.sqrt(1 - phi ** 2) * e[i]
    return x
def panel(scen):
    G = ar1(30); Fd = {f: ar1(30) for f in FAMS}; out = json.loads(json.dumps(d))
    plant = {}
    if scen.startswith('spike'):
        ds = [int(rng.integers(0, 20))]; ds += [ds[0] + 10] if scen == 'spike2' else []
        for dd in ds:
            for f in rng.choice(FAMS, 3, replace=False):
                cand = [i for i, s in enumerate(out['signals']) if s['family'] == f]
                plant.setdefault(int(rng.choice(cand)), []).append(dd)
    for i, s in enumerate(out['signals']):
        if s['family'] not in FAMS: continue
        f = Fd[s['family']]; v = np.sqrt(0.35) * f + np.sqrt(0.65) * ar1(30)
        if scen == 'shared': v = np.sqrt(0.35) * G + np.sqrt(0.65) * v
        for dd in plant.get(i, []): v[dd] += 3.5
        ser = []
        for t, x in s.get('series') or []:
            if t in days and x is not None: ser.append([t, float(v[days.index(t)])])
            else: ser.append([t, x])
        s['series'] = ser
    return out
def run(path):
    env = dict(os.environ, NOCLIP='1', RUNS='1', CARRIED='1')
    o = subprocess.run([sys.executable, os.path.join(HERE, 'chord_null.py'), path], capture_output=True, text=True, env=env).stdout
    real = int(re.search(r'top 3 = (\d+)', o).group(1))
    pc = float(re.search(r'circular shift\s*:.*= ([\d.]+)', o).group(1)); pb = float(re.search(r'block shuffle b=7\s*:.*= ([\d.]+)', o).group(1))
    return real, pc, pb
for scen in SCEN:
    R = []
    for k in range(K):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh: json.dump(panel(scen), fh)
        R.append(run(fh.name)); os.unlink(fh.name)
    R = np.array(R); ev = R[:, 0]
    print(f'{scen:7s} panels {K}: chord events mean {ev.mean():.2f} dist { {int(a): int(b) for a, b in zip(*np.unique(ev.astype(int), return_counts=True))}}'
          f' | block p<0.05 in {(R[:, 2] < 0.05).mean():.3f}, circular p<0.05 in {(R[:, 1] < 0.05).mean():.3f}'
          f' | min block p seen {R[:, 2].min():.4f}', flush=True)
