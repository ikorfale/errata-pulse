"""A month of the world, played: Chaos Pulse hard signals (30-day series) -> audio + video.
Each family is one voice. Each signal gets a robust z against its own 30 days (z = (x - median) / (1.4826*MAD)).
Daily family value = how much further out its most unusual signal is than the family's usual
most-unusual signal (the max is itself normalised by its own 30-day median and MAD, clipped +-3):
with 24 signals one is always far out, so the raw max would sit high every day.
Pitch follows z on a pentatonic scale; |z| > 4 on any single signal rings a bell.
v4 (2026-10-09, board 80982): a family is silent on a day when none of its series has a real value (only values
carried forward from an earlier day, e.g. Wikipedia's one-day lag), and bells ring only on real values.
v5 (2026-10-09, board 80996/80999): each row names the series that drives the voice that day and the date of the
value it plays; a family can be observed while its loudest series is a carried copy (ties: every driver listed)."""
import json, sys, wave, os, subprocess, datetime as dt
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

SRC = sys.argv[1] if len(sys.argv) > 1 else 'pulse/signals/2026-10-08.json'
OUT = os.environ.get('OUT', 'lab/sonify/out'); os.makedirs(OUT, exist_ok=True)
FAM = [('energy', 'Energy', '#3987e5', 220.0), ('military', 'Military', '#d95926', 146.83),
       ('control', 'Control of society', '#199e70', 293.66), ('anxiety', 'Public anxiety (Wikipedia)', '#c98500', 392.0),
       ('hidden war', 'Hidden war (cyber)', '#d55181', 110.0),
       ('mobilisation', 'Mobilisation (Wikipedia)', '#008300', 329.63)]
# English glosses for page titles in scripts the chart font cannot draw (and matplotlib cannot shape right-to-left)
GLOSS = {'מרחב_מוגן_דירתי': 'home safe room', 'جنگ_جهانی_سوم': 'World War III', '第三次世界大战': 'World War III',
         'צו_8': 'Tzav 8 call-up', 'שירות_המילואים_בישראל': 'reserve service in Israel', '後備軍事動員': 'reserve mobilisation',
         '民役': 'civilian service', 'خدمت_نظامی': 'military service'}
def short(sid):
    parts = sid.split(':'); name = parts[-1]
    lang = parts[-2] + ' ' if len(parts) > 2 and len(parts[-2]) == 2 else ''
    return (lang + GLOSS.get(name, name).replace('_', ' '))[:34]
d = json.load(open(SRC))
end = dt.date.fromisoformat(d['date']); days = [end - dt.timedelta(days=29 - i) for i in range(30)]
idx = {x.isoformat(): i for i, x in enumerate(days)}

def zser(series):
    v = np.full(30, np.nan)
    for t, x in series:
        if t in idx and x is not None: v[idx[t]] = float(x)
    for i in range(1, 30):               # carry the last value over gaps (data lags, weekends)
        if np.isnan(v[i]): v[i] = v[i - 1]
    ok = ~np.isnan(v)
    if ok.sum() < 20: return None
    med = np.median(v[ok]); mad = 1.4826 * np.median(np.abs(v[ok] - med))
    if mad == 0: mad = np.std(v[ok]) or 1.0
    return (v - med) / mad

def observed(series):
    o = np.zeros(30, bool)
    for t, x in series:
        if t in idx and x is not None: o[idx[t]] = True
    return o

fam_z, fam_n, fam_top, fam_raw, bells, fam_obs, fam_drv = {}, {}, {}, {}, np.zeros(30), {}, {}
for key, *_ in FAM:
    pairs = [(s['id'], z, observed(s['series'])) for s in d['signals'] if s['family'] == key and (z := zser(s.get('series') or [])) is not None]
    sigs = [a for a, _, _ in pairs]; zs = [z for _, z, _ in pairs]
    fam_n[key] = len(zs)
    if zs:
        Z = np.nan_to_num(np.vstack(zs)); j = np.abs(Z).argmax(axis=0)
        m = np.abs(Z[j, np.arange(30)]); fam_top[key] = [sigs[k] for k in j]
        # a family of 24 signals always has some signal far out: compare today's maximum with the family's own usual maximum
        mad = 1.4826 * np.median(np.abs(m - np.median(m))) or 1.0
        fam_z[key] = np.clip((m - np.median(m)) / mad, -3, 3); fam_raw[key] = m
        O = np.vstack([o for _, _, o in pairs]); fam_obs[key] = O.any(axis=0)
        A = np.abs(Z); fam_drv[key] = []
        for i in range(30):              # every series at the day's max, with the date of the value it plays
            drv = []
            for k in np.nonzero(A[:, i] >= A[:, i].max() - 1e-9)[0]:
                seen = np.nonzero(O[k, :i + 1])[0]
                drv.append((sigs[k], days[seen[-1]] if len(seen) else None, int(i - seen[-1]) if len(seen) else None))
            fam_drv[key].append(drv)
        bells += ((np.abs(np.nan_to_num(Z)) > 4) & O).sum(axis=0)
fams = [f for f in FAM if f[0] in fam_z]

# ---- audio
SR, BEAT = 22050, 1.2
PENTA = [0, 2, 4, 7, 9]
def step_ratio(z):                       # z -> pentatonic step, 1 step per 0.5 sigma
    k = int(round(z * 2)); o, r = divmod(k, 5)
    return 2 ** ((12 * o + PENTA[r]) / 12)
t = np.arange(int(SR * BEAT)) / SR
env = np.minimum(1, t / 0.03) * np.exp(-t * 2.2)
audio = np.zeros(int(SR * BEAT * 30) + SR)
for i in range(30):
    a = i * len(t)
    for key, _, _, base in fams:
        z = fam_z[key][i]
        if np.isnan(z) or not fam_obs[key][i]: continue      # not measured that day: a rest, not an echo
        f = base * step_ratio(z); amp = 0.10 + 0.08 * min(abs(z), 3)
        tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
        audio[a:a + len(t)] += amp * env * tone
    for b in range(int(min(bells[i], 6))):  # one bell per anomalous signal that day, staggered
        s0 = a + int(SR * (0.15 + 0.14 * b)); tb = t[:int(SR * 0.6)]
        audio[s0:s0 + len(tb)] += 0.12 * np.exp(-tb * 7) * np.sin(2 * np.pi * 1760 * tb) * np.sin(2 * np.pi * 2.5 * tb + 1)
audio /= np.max(np.abs(audio)) * 1.05
with wave.open(f'{OUT}/month.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((audio * 32767).astype('<i2').tobytes())

# ---- frames: small multiples, one row per voice, cursor on the day being played
BG, INK, MUTED, GRID = '#1a1a19', '#ffffff', '#c3c2b7', '#3a3a37'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': MUTED})
x = np.arange(30)
for i in range(30):
    fig, axs = plt.subplots(len(fams) + 1, 1, figsize=(12.8, 7.2), dpi=100, sharex=True,
                            gridspec_kw={'height_ratios': [1] * len(fams) + [0.55]}, facecolor=BG)
    fig.subplots_adjust(left=0.2, right=0.97, top=0.86, bottom=0.08, hspace=0.25)
    fig.text(0.03, 0.94, 'A month of the world, played', fontsize=22, weight='bold')
    fig.text(0.03, 0.895, f'Chaos Pulse hard signals, {days[0]:%d %b} to {days[-1]:%d %b %Y}. Each line is one voice: the strongest outlier in a family, '
             'measured against that family\'s usual strongest outlier.', fontsize=11, color=MUTED)
    for ax, (key, label, col, _) in zip(axs, fams):
        ax.set_facecolor(BG); z = fam_z[key]
        ax.axhline(0, color=GRID, lw=1); ax.set_ylim(-3.3, 3.3); ax.set_yticks([]); ax.tick_params(axis='x', length=0)
        ax.plot(x, z, color=col, lw=2, alpha=0.35)
        ax.plot(x[:i + 1], z[:i + 1], color=col, lw=2)
        un = ~fam_obs[key]
        if un.any(): ax.scatter(x[un], z[un], s=40, facecolor=BG, edgecolor=MUTED, linewidth=1.2, zorder=4)
        ax.scatter([i], [z[i]], s=70, color=col if fam_obs[key][i] else BG, edgecolor=BG if fam_obs[key][i] else col, linewidth=2, zorder=5)
        ax.axvline(i, color=MUTED, lw=1, alpha=0.5)
        dv = fam_drv[key][i]; nm = short(dv[0][0]) + (f' +{len(dv) - 1} tied' if len(dv) > 1 else '')
        fresh = 'observed today' if dv[0][2] == 0 else (f'copy of {dv[0][1]:%d %b} ({dv[0][2]} d old)' if dv[0][1] else 'no value yet')
        ax.text(1.0, 1.0, f'{nm} · {fresh}', transform=ax.transAxes, ha='right', va='bottom', fontsize=8.5,
                color=MUTED if dv[0][2] == 0 else '#f0b429')
        ax.text(-0.02, 0.5, f'{label}\n{fam_n[key]} signal' + ('s' if fam_n[key] != 1 else ''), transform=ax.transAxes, ha='right', va='center', fontsize=10.5, color=INK)
        for s in ax.spines.values(): s.set_visible(False)
    ax = axs[-1]; ax.set_facecolor(BG)
    ax.bar(x, bells, color='#86b6ef', width=0.6); ax.bar([i], [bells[i]], color=INK, width=0.6)
    ax.set_yticks([]); ax.text(-0.02, 0.5, 'Bells: signals\nbeyond 4 robust σ', transform=ax.transAxes, ha='right', va='center', fontsize=10.5)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks(x[::5]); ax.set_xticklabels([f'{days[k]:%d %b}' for k in x[::5]])
    fig.text(0.03, 0.02, 'Hollow dot: no new data that day (source lag), silent. Amber label: the loudest series plays a copied value', fontsize=9, color=MUTED)
    fig.text(0.97, 0.02, 'errata.page  ·  pulse.errata.page  ·  real data, sound and chart generated by code', fontsize=9, color=MUTED, ha='right')
    fig.savefig(f'{OUT}/f{i:02d}.png', facecolor=BG); plt.close(fig)
lst = ''.join(f"file 'f{i:02d}.png'\nduration {BEAT}\n" for i in range(30)) + "file 'f29.png'\n"
open(f'{OUT}/frames.txt', 'w').write(lst)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-i', f'{OUT}/frames.txt', '-i', f'{OUT}/month.wav',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '10', '-c:a', 'aac', '-b:a', '128k', '-shortest', f'{OUT}/month.mp4'], check=True)
summary = {k: {'n': fam_n[k], 'z_min': round(float(np.nanmin(fam_z[k])), 2), 'z_max': round(float(np.nanmax(fam_z[k])), 2),
               'argmax': days[int(np.nanargmax(fam_z[k]))].isoformat(), 'top_at_max': fam_top[k][int(np.nanargmax(fam_z[k]))], 'raw_at_max': round(float(fam_raw[k][int(np.nanargmax(fam_z[k]))]), 1), 'last': round(float(fam_z[k][-1]), 2),
               'silent_days': [days[i].isoformat() for i in np.where(~fam_obs[k])[0]],
               'played_but_driver_carried': [[days[i].isoformat(), [(a, b.isoformat() if b else None, g) for a, b, g in fam_drv[k][i]]]
                                             for i in range(30) if fam_obs[k][i] and all(g != 0 for _, _, g in fam_drv[k][i])]} for k, *_ in fams}
summary['bells'] = {days[i].isoformat(): int(bells[i]) for i in range(30) if bells[i]}
json.dump(summary, open(f'{OUT}/summary.json', 'w'), indent=1); print(json.dumps(summary, indent=1))
