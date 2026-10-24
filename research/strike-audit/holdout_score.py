"""Unblind PREREG.md holdout (Amendment 1): keep / drop ratios with Wilson 95% intervals."""
import json, math
import os; B = os.environ.get('HOLDOUT_DIR', 'holdout')
v = json.load(open(f'{B}/verdicts.json'))['v']; key = json.load(open(f'{B}/key.json'))
def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    p = k / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round(c - h, 2), round(c + h, 2)
for lab in ('NEW', 'FOLLOW', 'FALSE'):
    ids = [i for i in v if v[i][0] == lab]; kept = [i for i in ids if key[i]['new_counted']]
    print(f'{lab}: {len(ids)} site-days, NEW rule keeps {len(kept)}, drops {len(ids) - len(kept)}; ids kept {sorted(map(int, kept))}')
n = [i for i in v if v[i][0] == 'NEW']; k = sum(key[i]['new_counted'] for i in n)
f = [i for i in v if v[i][0] == 'FALSE']; d = sum(not key[i]['new_counted'] for i in f)
nf = [i for i in v if v[i][0] in ('NEW', 'FOLLOW')]; kf = sum(key[i]['new_counted'] for i in nf)
print(f'keep NEW {k}/{len(n)} = {k / len(n):.2f}, Wilson {wilson(k, len(n))}; threshold >= 0.90')
print(f'drop FALSE {d}/{len(f)} = {d / len(f):.2f}, Wilson {wilson(d, len(f))}; threshold >= 0.40')
print(f'sensitivity: keep NEW+FOLLOW {kf}/{len(nf)} = {kf / len(nf):.2f}')
bl = [i for i in v if v[i][1]]
print('borderline:', [(int(i), v[i][0], 'kept' if key[i]['new_counted'] else 'dropped') for i in bl])
print('NEW kept under a different first url:', sum(1 for i in v if key[i]['new_counted'] and key[i]['new_url'] != key[i]['old_url']))
