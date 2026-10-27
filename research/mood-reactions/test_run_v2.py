"""Synthetic tests for run_v2.py (no real reaction data): exact null, mid-ranks, block edges, floor order, planted effect."""
import json, os, random, tempfile, datetime as dt, io, contextlib
from fractions import Fraction
import run_v2 as R

p, _ = R.p_value([Fraction(1)], [15]); assert abs(p - 1/15) < 1e-12, p
p, _ = R.p_value([Fraction(8)], [15]); assert abs(p - 8/15) < 1e-12
p, _ = R.p_value([Fraction(3, 2)], [2]); assert abs(p - 1/2) < 1e-12    # tie at top of 2: S=1.5, P(S<=1.5)=P(1)
p, _ = R.p_value([Fraction(1), Fraction(1)], [15, 15]); assert abs(p - 1/225) < 1e-12
assert R.midrank_top(0.5, [0.1, 0.2]) == 1 and R.midrank_top(0.1, [0.1, 0.5]) == Fraction(5, 2)
h0 = R.T('2026-07-20T12:11:46Z')
assert R.block_of(h0, h0) == 0 and R.block_of(h0 - dt.timedelta(seconds=1), h0) == -1
assert R.block_of(h0 + dt.timedelta(hours=24) - dt.timedelta(seconds=1), h0) == 0 and R.block_of(h0 + dt.timedelta(hours=24), h0) == 1
assert R.classify('Всю информацию по атакам на Ростов публикуем тут max.ru/x') == 'excluded'
assert R.classify('Сегодня в городе открыли новый парк, приходите гулять всей семьёй') == 'other'
assert R.classify('Обломки БПЛА упали на крышу') == 'strike'

def synth(d, effect, seed):
    rnd = random.Random(seed)
    for i, reg, h in R.EVENTS:
        ch = R.CHANNELS[reg]; h0 = R.T(h); rows = []
        for k in range(-31, 2):
            for j in range(6):
                t = h0 + dt.timedelta(hours=24 * k + 4 * j + 1)
                base = rnd.randint(40, 200); al = rnd.binomial if False else int(base * rnd.uniform(0.02, 0.08))
                if k == 0 and effect: al = int(base * 0.3)
                rows.append({'id': len(rows), 'time': t.isoformat(), 'views': 1000, 'unparsed_reactions': 0,
                             'reacts': {'👍': base, '😱': al, 'custom:1': 3},
                             'text': 'Обломки БПЛА упали на крышу дома' if j == 0 else 'Обычная городская новость про ремонт дороги и парк'})
        with open(f'{d}/{ch}.jsonl', 'a') as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')

for eff in (True, False):
    d = tempfile.mkdtemp(); synth(d, eff, 1)
    out = io.StringIO()
    with contextlib.redirect_stdout(out): R.run(d, R.CHANNELS)
    s = out.getvalue()
    v = [l for l in s.splitlines() if l.strip().startswith('alarm:')][0]
    print('effect' if eff else 'null  ', '|', v.strip())
    if eff: assert 'effect claimed' in v
    else: assert 'effect claimed' not in v
print(s[-1600:])
print('ALL TESTS PASSED')
