"""#207 follow-up: gate the site's ratio flags with the series' own month.
z_last = robust z of the newest series point against all points of its series (>=20 points), as the collector would compute it.
A flag survives if |z_last| >= CUT. Prints every flag with z_last, and survivors for several cuts (is the result cut-robust?)."""
import json, numpy as np, sys
def z_last(ser):
    v = np.array([float(x) for _, x in ser if x is not None])
    if len(v) < 20: return None
    med = np.median(v); mad = 1.4826 * np.median(np.abs(v - med)) or (np.std(v) or 1.0)
    return (v[-1] - med) / mad
flags = []
for day in sys.argv[1:] or ['2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08']:
    for s in json.load(open(f'pulse/signals/{day}.json'))['signals']:
        if s.get('anomaly'):
            z = z_last(s.get('series') or []); flags.append((day, s['id'], z, s.get('series_kind') or ''))
            print(day, s['id'][:38].ljust(38), 'z_last', 'n/a' if z is None else f'{z:6.1f}', '|', (s.get('series_kind') or '')[:50])
for cut in (2, 3, 4, 5):
    print(f'cut {cut}: {sum(1 for f in flags if f[2] is None or abs(f[2]) >= cut)} of {len(flags)} kept (n/a kept)')
