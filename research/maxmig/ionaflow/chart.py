#!/usr/bin/env python3
"""Three panels: Max vs Telegram posts per governor in each IONAFLOW week. Same population as shift.py."""
import csv, os, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'per_governor.csv'), encoding='utf-8')))
P = ['2026-04-06_2026-04-12', '2026-07-15_2026-07-21', '2026-10-24_2026-10-30']
T = ['6–12 April', '15–21 July', '24–30 October']
EXCL = {'Александр Дрозденко'}
LAT = {'Андрей Клычков': 'Oryol', 'Михаил Ведерников': 'Pskov', 'Александр Хинштейн': 'Kursk',
       'Казбек Коков': 'Kabardino-Balkaria', 'Вячеслав Федорищев': 'Samara', 'Вадим Шумков': 'Kurgan',
       'Сергей Собянин': 'Moscow', 'Александр Гусев': 'Voronezh', 'Руслан Кухарук': 'Khanty-Mansi',
       'Дмитрий Артюхов': 'Yamal', 'Егор Ковальчук': 'Bryansk', 'Игорь Бабушкин': 'Astrakhan', 'Владимир Мазур': 'Tomsk',
       'Владислав Шапша': 'Kaluga', 'Игорь Артамонов': 'Lipetsk', 'Алексей Цыденов': 'Buryatia', 'Артур Парфенчиков': 'Karelia'}
def g(r, p, t):
    if r['governor_key'] == 'Вячеслав Федорищев' and p == P[2] and t == 'telegram':
        return None
    v = r[f'{p}_{t}']
    return None if v == '' else int(v)
both = [r for r in rows if g(r, P[0], 'max') is not None and g(r, P[0], 'telegram') is not None and r['governor_key'] not in EXCL]
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.9), sharex=True, sharey=True)
fig.patch.set_facecolor('#fbfaf7')
for ax, p, t in zip(axes, P, T):
    ok = [r for r in both if g(r, p, 'telegram') is not None]
    xs = [g(r, p, 'telegram') for r in ok]; ys = [g(r, p, 'max') for r in ok]
    heavy = [(x, y, r) for x, y, r in zip(xs, ys, ok) if x + y >= 5 and (y >= 1.5 * x or x >= 1.5 * y)]
    ax.set_facecolor('#fbfaf7')
    ax.plot([0, 110], [0, 110], color='#9a9a9a', lw=1, ls='--', zorder=1)
    ax.fill_between([0, 110], [0, 110 / 1.5], [0, 110 * 1.5], color='#d9d4c7', alpha=0.35, lw=0, zorder=0)
    ax.scatter(xs, ys, s=26, color='#2b4c7e', alpha=0.75, lw=0, zorder=3)
    for x, y, r in heavy:
        ax.scatter([x], [y], s=34, color='#b23a3a', lw=0, zorder=4)
        name = LAT.get(r['governor_key'])
        if name:
            off = {('Lipetsk', 59): (4, 6), ('Kabardino-Balkaria', 54): (4, -11), ('Kaluga', 52): (4, -4), ('Tomsk', 15): (4, 4), ('Astrakhan', 12): (4, -9)}.get((name, y), (4, 3 if (y % 2 == 0) else -9))
            ax.annotate(name, (x, y), xytext=off, textcoords='offset points', fontsize=7.5, color='#b23a3a')
    eq = sum(1 for x, y in zip(xs, ys) if x == y and x + y >= 5)
    ax.set_title(f'{t} 2026  ·  n={len(ok)}  ·  identical totals: {eq}', fontsize=10, loc='left')
    ax.set_xlim(-2, 110); ax.set_ylim(-2, 110); ax.set_aspect('equal')
    ax.grid(color='#e6e2d8', lw=0.6); ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlabel('posts on Telegram in the week')
axes[0].set_ylabel('posts on MAX in the week')
fig.suptitle("Russian governors' weekly posts on MAX vs Telegram (IONAFLOW counts; grey band = within 1.5×; red = outside it)", fontsize=11, x=0.01, ha='left')
fig.text(0.01, 0.005, 'Data: IONAFLOW (ionaflow.com), 80 heads of regions listed on both platforms; Leningrad excluded (Telegram not collected); Samara Telegram missing in October. Chart: errata.page', fontsize=7.5, color='#555')
plt.tight_layout(rect=(0, 0.07, 1, 0.95))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'three_weeks.png')
plt.savefig(out, dpi=130); print('wrote', out)
