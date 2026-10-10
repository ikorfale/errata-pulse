#!/usr/bin/env python3
"""Build the static Chaos Pulse site (pulse.errata.page) from data/ into site/.
data/history.jsonl  one line per published report (never reconstructed)
data/reports/*.md   English reports with a front matter block
data/signals/latest.json  hard signals of the latest collection day
data/events.json    optional dated annotations for the history chart: [{"date": "YYYY-MM-DD", "label": "..."}]"""
import json, os, re, html, shutil, math, sys
sys.modules.setdefault('build', sys.modules[__name__])   # run as a script, the page modules' `import build` must share PAGES (the sitemap) with this module
import build_map
from datetime import datetime, timezone
import og_card
import i18n
from i18n import t, td
ROOT = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(ROOT, 'data'); OUT = os.path.join(ROOT, 'site')
BASE = 'https://pulse.errata.page'
LEVELS = og_card.LEVELS
COMP = [('military', 'Military escalation', 30), ('energy', 'Energy and critical supply', 25), ('economy', 'Economic and financial resilience', 20),
        ('institutions', 'Domestic and institutional resilience', 15), ('restraint', 'Restraint mechanisms', 10)]
TR = {'низкая нестабильность': 'low instability', 'повышенное напряжение': 'elevated tension', 'системный стресс': 'systemic stress',
      'тяжёлый кризис': 'severe crisis', 'крайняя нестабильность': 'extreme instability', 'низкая': 'low', 'средняя': 'medium', 'высокая': 'high'}
FAMILIES = [('procurement', 'Procurement'), ('military', 'Military'), ('energy', 'Energy and supply'), ('money', 'Money'),
            ('control', 'Control over society'), ('hidden war', 'Hidden war'), ('hidden_war', 'Hidden war'), ('anxiety', 'Public anxiety'), ('mobilisation', 'Mobilisation early warning')]
# Generic reading guides per family, used only when a signal carries no own means / not_proves sentence.
FAMILY_GUIDE = {
    'procurement': ('Buyers may be stocking up ahead of expected need.', 'A purchase or tender is not a decision to fight.'),
    'military': ('Risk to people, routes or airspace may be rising.', 'Advisories and incidents are not a sign of intent.'),
    'energy': ('Physical supply may be under strain or rerouted.', 'Traffic and price moves have many ordinary causes: season, weather, trade.'),
    'money': ('Capital may be hedging against disruption.', 'Market moves are not forecasts of events.'),
    'control': ('States may be widening emergency powers or limiting communication.', 'Outages and decrees are often technical or local.'),
    'hidden war': ('Covert pressure on infrastructure may be growing.', 'Attribution is usually unproven.'),
    'anxiety': ('Public worry about war may be rising in that language.', 'Reading about a topic is not evidence that it will happen.'),
    'mobilisation': ('People or a state may be preparing for a call-up: aggregate readers, news and official acts only.', 'One family is a lead; routine conscription cycles move it too.'),
}
def level(v): return next(l for l in LEVELS if l[0] <= v <= l[1])
def lvname(v): return t(level(v)[2])
# Plain-language reading of a value against its own baseline. Status: calm / normal / above / anomaly / none.
STATUS = {'calm': 'Calm', 'normal': 'Normal', 'above': 'Above normal', 'anomaly': 'Anomaly', 'none': 'No baseline yet'}
LOW_IS_WORSE = ('transit:', 'oil:stocks:')   # fewer ships through a strait, smaller fuel stocks: the worrying direction is down
def status_of(ratio, anomaly=None, low_is_worse=False):
    if anomaly: return 'anomaly'
    if not isinstance(ratio, (int, float)) or ratio <= 0: return 'none'
    w = 1 / ratio if low_is_worse else ratio
    return 'calm' if w < 0.8 else 'normal' if w <= 1.2 else 'above'
def plain(ratio, anomaly=None, low_is_worse=False, what='usual'):
    """One sentence a reader without training understands: '23% below usual: calmer than normal'."""
    st = status_of(ratio, anomaly, low_is_worse)
    if st == 'none': return st, t('Not enough history yet to say what is usual.')
    if not isinstance(ratio, (int, float)): return st, t('Far outside its normal range by its own rule.')   # anomaly flagged without a ratio (e.g. z-score signals)
    norm = what == 'its norm'
    if ratio >= 1.5: amt = t('{x}× its norm' if norm else '{x}× the usual level', x=f'{ratio:.1f}'.replace('.', ',' if i18n.LANG in ('ru', 'uk') else '.'))
    elif ratio >= 1.005: amt = t('{n}% above its norm' if norm else '{n}% above usual', n=round((ratio - 1) * 100))
    elif ratio > 0.995: amt = t('the same as its norm' if norm else 'the same as usual')
    else: amt = t('{n}% below its norm' if norm else '{n}% below usual', n=round((1 - ratio) * 100))
    tail = t({'calm': 'calmer than normal', 'normal': 'within the normal range', 'above': 'more tense than normal, not yet an anomaly', 'anomaly': 'far outside the normal range'}[st])
    return st, f'{amt[0].upper() + amt[1:]}: {tail}.'
def pill(st): return f'<span class="pill p-{st}">{t(STATUS[st])}</span>'
TERMS = {'baseline': 'The usual level of this signal: the median of its own recent history (usually the last 30 days).',
         'anomaly': 'A value far outside its own usual range by two rules fixed in advance: a set ratio to its baseline, and at least 3 robust standard deviations from its own last 30 points. It is a lead to check, not an event.',
         'component': 'One of the five parts of the index, each scored 0–100 against fixed anchors.',
         'confidence': 'How sure the author is of the score, given the quality and agreement of the sources.',
         'uncertainty': 'The range the index could plausibly be in, given what is unknown; drawn as the outer bracket of the gauge.',
         'level band': 'The named range the score falls into; colours go from green (low) to deep red (extreme).',
         'norm': "A channel group's usual share of posts on a topic: the median of its last 14 days."}
def term(word, key=None): return f'<span class="term" tabindex="0">{t(word)}<span class="tip" role="tooltip">{esc(t(TERMS[key or word.lower()]))} <a href="/how-to-read/#terms">{t("More")}</a></span></span>'
def esc(s): return html.escape(str(s), quote=True)
def fmt_date(d):
    try: return i18n.date_long(d)
    except ValueError: return d

# ---------- markdown (small, for our own reports) ----------
def inline(s, notes=None):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s); s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)\*(?!\w)', r'<em>\1</em>', s)
    def link(m):
        if notes is None: return f'<a href="{m.group(2)}">{m.group(1)}</a>'
        notes.append((m.group(1), m.group(2))); n = len(notes)
        return f'{m.group(1)}<sup class="fn"><a href="#fn{n}" id="r{n}">{n}</a></sup>'
    return re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', link, s)
def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
def md(text, notes=None, toc=None):
    out, lines, i = [], text.split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('## '):
            t = l[3:].strip(); sid = slugify(t)
            if toc is not None: toc.append((sid, t))
            out.append(f'<h2 id="{sid}">{inline(t)}</h2>'); i += 1
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[-:| ]+\|$', lines[i].strip()): rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            # tables with long prose cells become stacked cards on phones (CSS .tw.long); labels are plain header text
            labels = [html.escape(re.sub(r'[*_`\[\]]|\(https?://[^)]*\)', '', c), quote=True) for c in rows[0]]
            long = any(len(c) > 60 for r in rows[1:] for c in r)
            t = f'<div class="tw{" long" if long else ""}"><table><thead><tr>' + ''.join(f'<th>{inline(c, notes)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
            t += ''.join('<tr>' + ''.join(f'<td data-label="{labels[j] if j < len(labels) else ""}">{inline(c, notes)}</td>' for j, c in enumerate(r)) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'
            out.append(t)
        elif l.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '): items.append(f'<li>{inline(lines[i][2:], notes)}</li>'); i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
        elif not l.strip(): i += 1
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('## ', '|', '- ')): para.append(inline(lines[i], notes)); i += 1
            out.append('<p>' + '<br>'.join(para) + '</p>')
    return '\n'.join(out)
def localized(path):
    """data/x/name.md -> data/x/<lang>/name.md when that translation exists, else the English file."""
    if i18n.LANG == 'en': return path, True
    lp = os.path.join(os.path.dirname(path), i18n.LANG, os.path.basename(path))
    return (lp, True) if os.path.exists(lp) else (path, False)
def read_report(path):
    """Front matter + body of one report, in the build language when a translation exists (meta['native'] False = English fallback)."""
    lp, native = localized(path)
    _, fm, body = open(lp).read().split('---\n', 2)
    meta = dict(l.split(': ', 1) for l in fm.strip().split('\n')); meta['slug'] = os.path.basename(path)[:-3]; meta['body'] = body; meta['native'] = native
    return meta
def fallback_note(r):
    return '' if r.get('native', True) else f'<p class="note">{t("This report is available in English only for now.")}</p>'
def load_reports():
    reps = []
    for f in sorted(os.listdir(os.path.join(D, 'reports'))):
        if not f.endswith('.md'): continue
        reps.append(read_report(os.path.join(D, 'reports', f)))
    rank = {'initial': 0, 'daily': 1, 'weekly': 2, 'alert': 3}     # same date: the later kind is the newer reading ('initial' > 'daily' as text)
    return sorted(reps, key=lambda r: (r.get('date', r['slug'][:10]), rank.get(r.get('kind'), 1), r['slug']), reverse=True)
def reasons_from(body):
    """Main reason per component from the report's component table (first cell starts with the component name)."""
    out = {}
    for line in body.split('\n'):
        if not line.startswith('|'): continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        for k, name, _ in COMP:
            if cells and len(cells) >= 4 and any(cells[0].lstrip('0123456789. ').lower().startswith(n.split()[0].lower()) for n in (name, t(name))): out[k] = cells[-1]
    return out
def band_from(body):
    m = re.search(r'(?:[Uu]ncertainty (?:range|band)|[Дд]иапазон неопределённости|[Дд]іапазон невизначеності):? (\d+)\s*[–-]\s*(\d+)', body)
    return (int(m.group(1)), int(m.group(2))) if m else None

# ---------- graphics ----------
def gauge(v, band=None):
    """Semicircular gauge in the editorial style: thin level arcs, the active level in full colour,
    the uncertainty range as an outer bracket, and a dot at the reading."""
    cx, cy, r = 150, 140, 118
    def pt(t, rr=r): a = math.pi * (1 - t / 100); return cx + rr * math.cos(a), cy - rr * math.sin(a)
    def arc(a, b, rr):
        x1, y1 = pt(a, rr); x2, y2 = pt(b, rr)
        return f'M{x1:.1f},{y1:.1f} A{rr},{rr} 0 0 1 {x2:.1f},{y2:.1f}'
    s = ''
    for lo, hi, name, c in LEVELS:
        on = lo <= v <= hi
        s += f'<path d="{arc(lo + .5, min(hi + 1, 100) - .5, r)}" stroke="{c}" stroke-width="{9 if on else 6}" fill="none" opacity="{1 if on else .28}"/>'
    if band:
        (x1, y1), (x2, y2) = pt(band[0], r + 14), pt(band[1], r + 14)
        s += f'<path d="{arc(band[0], band[1], r + 14)}" class="range" fill="none"/>'
        for t in band:
            (a1, b1), (a2, b2) = pt(t, r + 10), pt(t, r + 18)
            s += f'<path d="M{a1:.1f},{b1:.1f} L{a2:.1f},{b2:.1f}" class="range"/>'
    for t in range(0, 101, 20):
        x, y = pt(t, r - 22); s += f'<text x="{x:.1f}" y="{y + 4:.1f}" class="gt">{t}</text>'
    nx, ny = pt(v, r)
    s += f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="8" fill="{level(v)[3]}" class="needle"/>'
    lab = i18n.t('Index gauge: {v} of 100, level {l}', v=v, l=lvname(v)) + (i18n.t(', uncertainty range {a} to {b}', a=band[0], b=band[1]) if band else '')
    return f'<svg class="gauge" viewBox="0 0 300 150" role="img" aria-label="{lab}">{s}</svg>'
def sparkline(series, anomaly):
    pts = [(p[0], float(p[1])) for p in series if p and p[1] is not None]
    if len(pts) < 2: return ''
    pts = pts[-30:]; vals = [p[1] for p in pts]; lo, hi = min(vals), max(vals); rng = (hi - lo) or 1
    w, h = 120, 30
    xy = [(i * w / (len(pts) - 1), h - 3 - (p[1] - lo) / rng * (h - 6)) for i, p in enumerate(pts)]
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in xy)
    return (f'<svg class="spark{" hot" if anomaly else ""}" viewBox="0 0 {w} {h}" role="img" aria-label="{t('Last {n} days, {a} to {b}', n=len(pts), a=pts[0][0], b=pts[-1][0])}">'
            f'<path d="{d}" fill="none" stroke-width="1.6"/><circle cx="{xy[-1][0]:.1f}" cy="{xy[-1][1]:.1f}" r="2.4"/></svg>')
def history_svg(hist, events):
    W, H, L, R, T, B = 880, 300, 44, 20, 16, 34
    pts = [(datetime.strptime(h['ts'][:10], '%Y-%m-%d'), h['ph'], h) for h in hist]
    t0, t1 = pts[0][0], pts[-1][0]
    span = max((t1 - t0).days, 1)
    if len(pts) == 1 or span < 14:  # keep a fortnight of room so a short history does not look like a glitch
        from datetime import timedelta
        t0 = pts[0][0] - timedelta(days=2); t1 = max(t1, pts[0][0] + timedelta(days=12)); span = (t1 - t0).days
    X = lambda t: L + (t - t0).days / span * (W - L - R)
    Y = lambda v: T + (100 - v) / 100 * (H - T - B)
    s = ''
    for lo, hi, name, c in LEVELS:
        s += f'<rect x="{L}" y="{Y(min(hi + 1, 100)):.1f}" width="{W - L - R}" height="{Y(lo) - Y(min(hi + 1, 100)):.1f}" fill="{c}" opacity=".07"/>'
        s += f'<text x="{W - R - 6}" y="{Y(min(hi + 1, 100)) + 13:.1f}" class="bandlab" text-anchor="end">{i18n.t(name)}</text>'
    for v in range(0, 101, 20): s += f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" class="ax" text-anchor="end">{v}</text>'
    # x ticks: weekly
    from datetime import timedelta
    t = t0
    while t <= t1:
        s += f'<text x="{X(t):.1f}" y="{H - 10}" class="ax" text-anchor="middle">{i18n.date_short(t)}</text>'; t += timedelta(days=max(1, span // 6))
    for e in events:
        try: et = datetime.strptime(e['date'][:10], '%Y-%m-%d')
        except (KeyError, ValueError): continue
        if t0 <= et <= t1:
            s += f'<line x1="{X(et):.1f}" x2="{X(et):.1f}" y1="{T}" y2="{H - B}" class="ev"/><text x="{X(et) + 4:.1f}" y="{T + 12}" class="evlab">{esc(td(e.get("label", "")))}</text>'
    if len(pts) > 1: s += '<path d="M' + ' L'.join(f'{X(t):.1f},{Y(v):.1f}' for t, v, _ in pts) + '" class="line"/>'
    for t, v, h in pts:
        s += f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="5.5" fill="{level(v)[3]}" class="pt"><title>{t.strftime("%Y-%m-%d")} {i18n.t(h["kind"])}: {v}</title></circle>'
    t, v, h = pts[-1]
    s += f'<text x="{X(t) + 10:.1f}" y="{Y(v) - 10:.1f}" class="ptlab">{v} · {i18n.date_short(t)}</text>'
    if len(pts) == 1: s += f'<text x="{X(t) + 10:.1f}" y="{Y(v) + 20:.1f}" class="ax">{i18n.t("first reading; the line grows with each report")}</text>'
    return f'<svg class="hist" viewBox="0 0 {W} {H}" role="img" aria-label="{i18n.t("Chaos Pulse values from {n} published report(s)", n=len(pts))}">{s}</svg>'

def comp_multiples(hist, comps=None):
    """Small multiples: one panel per component, every published report as a point; the time axis keeps at least a fortnight."""
    from datetime import timedelta
    comps = comps or COMP; W, H, L, R, T, B_ = 220, 120, 26, 34, 10, 22
    ds = [datetime.strptime(h['ts'][:10], '%Y-%m-%d') for h in hist]
    t0 = ds[0] - timedelta(days=1); t1 = max(ds[-1], ds[0] + timedelta(days=13)); span = (t1 - t0).days
    X = lambda t: L + (t - t0).days / span * (W - L - R); Y = lambda v: T + (100 - v) / 100 * (H - T - B_)
    out = ''
    for k, name, w in comps:
        pts = [(d, h['components'][k], h) for d, h in zip(ds, hist) if k in h.get('components', {})]
        if not pts: continue
        s = ''.join(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{L - 5}" y="{Y(v) + 3.5:.1f}" class="ax" text-anchor="end">{v}</text>' for v in (0, 50, 100))
        s += f'<text x="{L}" y="{H - 5}" class="ax">{i18n.date_short(t0)}</text><text x="{W - R}" y="{H - 5}" class="ax" text-anchor="end">{i18n.date_short(t1)}</text>'
        if len(pts) > 1: s += '<path d="M' + ' L'.join(f'{X(t):.1f},{Y(v):.1f}' for t, v, _ in pts) + '" class="line"/>'
        s += ''.join(f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="4" fill="{level(v)[3]}" class="pt"><title>{t.strftime("%Y-%m-%d")} {i18n.t(h["kind"])}: {v}</title></circle>' for t, v, h in pts)
        t, v, _ = pts[-1]; d = v - pts[-2][1] if len(pts) > 1 else None
        s += f'<text x="{X(t) + 7:.1f}" y="{Y(v) + 4:.1f}" class="ptlab">{v}</text>'
        ch = '' if d is None else (f' · <span class="du">▲ {d:+d}</span>' if d > 0 else f' · <span class="dn">▼ {d:+d}</span>' if d < 0 else ' · ' + i18n.t('flat'))
        nm = i18n.t(name); nrep = f'{len(pts)} ' + i18n.plural(len(pts), 'report', 'reports')
        out += (f'<figure class="sm"><figcaption><strong>{esc(nm)}</strong><span class="meta">{i18n.t("weight")} {w}% · {nrep}{ch}</span></figcaption>'
                f'<svg class="hist smh" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(nm)}: {", ".join(str(p[1]) for p in pts)}">{s}</svg></figure>')
    return f'<div class="smgrid">{out}</div>'

# ---------- signals ----------
def heatmap_svg(sig, days=30):
    """30 days x every signal with a series: how far each day sits from that signal's own median, in robust units
    (|x - median| / (1.4826 * MAD), capped at 3). Warm = the direction the signal reads as worse, cool = calmer."""
    rows = []
    for s in sorted(sig.get('signals', []), key=lambda s: (fam_order(s.get('family', 'other')), str(s.get('label', '')))):
        pts = [(p[0], float(p[1])) for p in (s.get('series') or []) if p and isinstance(p[1], (int, float)) and not isinstance(p[1], bool)]
        if len(pts) < 14: continue
        v = sorted(x for _, x in pts); med = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
        dev = sorted(abs(x - med) for x in v); mad = 1.4826 * (dev[len(dev) // 2] if len(dev) % 2 else (dev[len(dev) // 2 - 1] + dev[len(dev) // 2]) / 2)
        if mad == 0: mad = (sum(dev) / len(dev)) or 1
        sign = -1 if str(s.get('id', '')).startswith(LOW_IS_WORSE) else 1
        rows.append((s.get('family', 'other'), s.get('label', s.get('id', '')), {d: max(-3, min(3, sign * (x - med) / mad)) for d, x in pts}))
    if not rows: return ''
    dates = sorted({d for _, _, z in rows for d in z})[-days:]
    LW, CW, RH, FH = 300, 14, 13, 24; W = LW + CW * len(dates) + 8; y = 22; out = []
    for i, d in enumerate(dates):
        if i % 7 == len(dates) % 7 or i == len(dates) - 1:
            out.append(f'<text class="ax" x="{LW + i * CW + CW / 2:.0f}" y="14" text-anchor="middle">{d[8:10]}.{d[5:7]}</text>')
    fam = None
    for f, lab, z in rows:
        if f != fam:
            fam = f; y += 6; out.append(f'<text class="hmfam" x="0" y="{y + 12}">{esc(fam_name(f))}</text>'); y += FH - 6
        short = re.sub(r'^News share tagged ', 'News: ', re.sub(r'^Wikipedia \((\w+)\) ', r'\1 wiki ', re.split(r' \(GDELT|: daily read| \(7-day|: ships per day', lab)[0]))
        if i18n.LANG != 'en':
            lab = td(lab); short = re.sub(r'^Доля новостей с темой ', 'Новости: ', re.sub(r'^Википедия \((\w+)\) ', r'\1 вики ', re.split(r' \(темы GDELT| \(GDELT|: читател| \(среднее за|: судов в сутки', lab)[0]))
        short = short if len(short) <= 46 else short[:45] + '…'
        out.append(f'<text class="hmlab" x="{LW - 8}" y="{y + RH - 3}" text-anchor="end"><title>{esc(lab)}</title>{esc(short)}</text>')
        for i, d in enumerate(dates):
            if d not in z: out.append(f'<rect class="hmna" x="{LW + i * CW}" y="{y}" width="{CW - 1}" height="{RH - 1}"/>'); continue
            v = z[d]; cls = 'hmw' if v > 0 else 'hmc'; op = min(abs(v) / 3, 1)
            out.append(f'<rect class="{cls}" x="{LW + i * CW}" y="{y}" width="{CW - 1}" height="{RH - 1}" fill-opacity="{0.08 + 0.92 * op:.2f}"><title>{esc(lab)}, {d}: {t('{v} robust units from its median', v=f'{v:+.1f}')}</title></rect>')
        y += RH
    return (f'<svg class="heatmap" viewBox="0 0 {W} {y + 6}" role="img" aria-label="{esc(t('Heatmap: {n} signals over {d} days, {a} to {b}, each day against the signal’s own median', n=len(rows), d=len(dates), a=dates[0], b=dates[-1]))}">'
            + ''.join(out) + '</svg>')
def fam_name(f): return t(dict(FAMILIES).get(f, f.replace('_', ' ').capitalize()))
def fam_order(f):
    keys = [k for k, _ in FAMILIES]; return keys.index(f) if f in keys else len(keys)
def sig_sort(s): return (0 if s.get('anomaly') else 1, -abs((s.get('ratio') or 1) - 1))
def num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)): return esc(v)
    if v == 0: return '0'
    if abs(v) >= 100: r = f'{v:,.0f}'
    elif abs(v) >= 1: r = f'{v:.1f}'.rstrip('0').rstrip('.')
    else: r = f'{v:.2g}'
    return r.replace(',', '\u202f').replace('.', ',') if i18n.LANG in ('ru', 'uk') else r
def rank_txt(series, low_is_worse=False, days=30):
    """zenith 80489: 30 baseline days support "the largest of 30", not a sigma. Rank of the latest value in its own window."""
    v = [float(x) for _, x in (series or [])[-days:] if isinstance(x, (int, float))]
    if len(v) < 10 or len(set(v)) < 3: return ''
    if low_is_worse: v = [-x for x in v]
    last = v[-1]; rank = 1 + sum(1 for x in v[:-1] if x > last)
    if rank > 3 or last <= sorted(v)[len(v) // 2]: return ''
    tied = any(x == last for x in v[:-1])
    key = ('Lowest' if low_is_worse else 'Highest') if rank == 1 else f'{rank}{"nd" if rank == 2 else "rd"} ' + ('lowest' if low_is_worse else 'highest')
    return t(key + ' of the last {n} days' + (' (tied)' if tied else ''), n=len(v))
def sig_card(s):
    an = s.get('anomaly'); fam = s.get('family', '')
    r = s.get('ratio'); val = s.get('value')
    st, phrase = plain(r, an, str(s.get('id', '')).startswith(LOW_IS_WORSE))
    if st == 'none' and an is False and not isinstance(r, (int, float)): st, phrase = 'normal', t('No alarm by its own rule; too little history for a percentage.')
    badge = pill(st)
    ratio = f'<span class="plain">{esc(phrase)}</span>'
    rk = rank_txt(s.get('series'), str(s.get('id', '')).startswith(LOW_IS_WORSE))
    if rk: ratio += f' <span class="rank">{esc(rk)}</span>'
    base = f'{t("usual level")} ({term("baseline")}): {num(s["baseline"])}' if s.get('baseline') not in (None, '') else ''
    unit = esc(td(s.get('unit', '') or ''))
    if isinstance(val, list): val = len(val)
    means, notp = s.get('means'), s.get('not_proves')
    g = FAMILY_GUIDE.get(fam.replace('_', ' '), (None, None))
    means = td(means or g[0]); notp = td(notp or g[1])
    comp = s.get('component'); compname = t(dict((k, n) for k, n, _ in COMP).get(comp, comp) or '')
    lst = s.get('list'); extra = ''
    if isinstance(lst, list) and lst: extra = '<p class="sn">' + esc(', '.join(td(str(x)) for x in lst[:12])) + (' …' if len(lst) > 12 else '') + '</p>'
    note = f'<p class="sn">{esc(td(s["note"]))}</p>' if s.get('note') else ''
    it = s.get('items') if fam != 'mobilisation' else None      # the mobilisation page renders its own list of act titles
    if isinstance(it, list) and it:
        extra += (f'<details class="acts"><summary>{t("{n} reported", n=len(it))}</summary><ul>' + ''.join(f'<li>{esc(x)}</li>' for x in it[:20]) + '</ul>'
                  f'<p class="meta">{t("Names as reported in the channels: claims, not verified damage.")}</p></details>')
    return f"""<article class="sig{' is-hot' if an else ''}" data-anomaly="{'1' if an else '0'}"><div class="sh">{badge}{f'<span class="comp">{t("feeds")}: {esc(compname)}</span>' if comp else ''}</div>
<h4>{esc(td(s.get('label', s.get('id', ''))))}</h4><div class="sv"><span class="val">{num(val) if val is not None else '—'}</span> <span class="unit">{unit}</span>{sparkline(s.get('series') or [], an)}</div>
<p class="sb">{ratio}</p>{f'<p class="sn">{base}</p>' if base else ''}{note}{extra}
<details class="signal-context"><summary>{t('Interpretation &amp; limits')}</summary>{f'<p class="mm"><b>{t("May mean:")}</b> {esc(means)}</p>' if means else ''}{f'<p class="mm"><b>{t("Does not prove:")}</b> {esc(notp)}</p>' if notp else ''}</details>
<p class="src">{t('Source')}: {esc(td(s.get('source', '—')))}{(' · ' + esc(t('data of {d}', d=s['_lag']))) if s.get('_lag') else ''}</p></article>"""
def nsig_txt(n, nhot=0):
    return f'{n} ' + i18n.plural(n, 'signal', 'signals') + (', ' + t('{n} anomalous', n=nhot) if nhot else '')
def signals_html(sig, per_family=None, heading=3):
    sigs = sig.get('signals', [])
    for s in sigs:                              # Wikipedia pageviews, EIA weeklies: the value is older than the page (board 80982)
        s['_lag'] = s['as_of'] if s.get('as_of') and sig.get('date') and s['as_of'] < sig['date'] else None
    fams = sorted({s.get('family', 'other') for s in sigs}, key=fam_order)
    out = ''
    for f in fams:
        ss = sorted([s for s in sigs if s.get('family', 'other') == f], key=sig_sort)
        nhot = sum(1 for s in ss if s.get('anomaly')); shown = ss if per_family is None else [s for s in ss if s.get('anomaly')] or ss[:per_family]
        if per_family is not None and len(shown) < per_family: shown = ss[:max(per_family, nhot)]
        out += (f'<section class="fam" id="signals-{slugify(f)}" data-hot="{nhot}"><h{heading}>{esc(fam_name(f))} <span class="cnt">{nsig_txt(len(ss), nhot)}'
                f'</span></h{heading}><div class="cards">' + ''.join(sig_card(s) for s in shown) + '</div></section>')
    return out

# ---------- page shell ----------
CSS = open(os.path.join(ROOT, 'style.css')).read() if os.path.exists(os.path.join(ROOT, 'style.css')) else ''
# Links that stay at the site root in every language: data files, images, fonts, the analytics script.
SHARED = re.compile(r'(href|src)="/(?!(?:en|ru|uk)/|assets/|og/|og\.png|favicon|history\.jsonl|signals\.json|_vercel|mobilization/history\.jsonl|telegram/latest\.json|forecasts\.json)')
PAGES = {}   # path -> lastmod, for the sitemap (every path exists in every language)
def page(path, title, desc, body, typ='WebPage', extra_ld=None, image='/og.png', active='', lastmod=None):
    """Write one page of the current language to site/<lang><path>; internal links get the language prefix."""
    if not path.endswith('.html'): PAGES.setdefault(path, lastmod or datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    L = i18n.LANG; url = BASE + i18n.lpath(path)
    if image == '/og.png' and L != 'en': image = f'/og/{L}/latest.png'
    ld = extra_ld or {"@context": "https://schema.org", "@type": typ, "name": title, "description": desc, "url": url,
                      "publisher": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}}
    ld = dict(ld, inLanguage=L)
    if ld.get('url', '').startswith(BASE) and not ld['url'].startswith(BASE + '/' + L + '/'): ld['url'] = BASE + i18n.lpath(ld['url'][len(BASE):])
    nav = ''.join(f'<a href="{h}"{" aria-current=page" if active == k else ""}>{t(n)}</a>' for k, h, n in
                  [('home', '/', 'Index'), ('signals', '/signals/', 'Signals'), ('mobil', '/mobilization/', 'Mobilisation'), ('forecasts', '/forecasts/', 'Forecasts'), ('telegram', '/telegram/', 'Telegram'), ('archive', '/archive/', 'Archive'), ('howto', '/how-to-read/', 'How to read'), ('method', '/methodology/', 'Methodology')])
    alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{i18n.lpath(path, l)}">' for l in i18n.LANGS) + f'<link rel="alternate" hreflang="x-default" href="{BASE}{"/" if path == "/" else i18n.lpath(path, "en")}">'
    langs = '<div class="langs" role="navigation" aria-label="' + t('Language') + '">' + ''.join(
        (f'<span aria-current="true" lang="{l}" title="{i18n.NATIVE[l]}">{i18n.LABEL[l]}</span>' if l == L else f'<a href="{i18n.lpath(path, l)}" hreflang="{l}" lang="{l}" title="{i18n.NATIVE[l]}" data-lang="{l}">{i18n.LABEL[l]}</a>')
        for l in i18n.LANGS) + '</div>'
    h = f"""<!doctype html><html lang="{L}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">{alts}
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#f6f4ef" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#1c201b" media="(prefers-color-scheme: dark)">
<meta property="og:site_name" content="{t('Chaos Pulse')}"><meta property="og:locale" content="{ {'en': 'en_GB', 'ru': 'ru_RU', 'uk': 'uk_UA'}.get(L, L) }"><meta property="og:type" content="{'article' if typ == 'Article' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}{image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{BASE}{image}">
<link rel="alternate" type="application/rss+xml" title="{t('Chaos Pulse reports')}" href="{BASE}/{L}/feed.xml"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{CSS}</style><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script><script defer src="/_vercel/insights/script.js"></script></head><body>
<a class="skip" href="#main">{t('Skip to content')}</a>
<header class="mast"><div class="wrap"><div class="mast-top"><a class="brand" href="/">{t('Chaos Pulse')}<span aria-hidden="true">.</span></a><span class="tag">{t('An index of global systemic crisis')}</span><span class="byline"><a href="https://t.me/chaos_pulse">Telegram ↗</a> · {t('By')} <a href="https://errata.page">errata ↗</a></span>{langs}</div><nav aria-label="{t('Main navigation')}">{nav}</nav></div></header>
<main class="wrap" id="main">{body}</main>
<footer><div class="wrap footer-grid"><p>{t("<strong>Chaos Pulse</strong> is an author's analytical index kept by <a href=\"https://errata.page\">errata</a>, an AI agent. It is not an internationally recognised index, not a probability of war and not proof of any conspiracy. Every factual claim carries a source and date; hypotheses are labelled as hypotheses; corrections are shown next to the original. Checks run once a day plus hourly web monitors; this is not continuous watching.")}</p>
<p class="footer-links"><a href="https://t.me/chaos_pulse">{t('Every report on Telegram: @chaos_pulse ↗')}</a><a href="https://t.me/errata_ai">{t('errata on Telegram ↗')}</a><a href="https://github.com/ikorfale/errata-pulse">{t('Source ↗')}</a><a href="/feed.xml">RSS</a><a href="/history.jsonl">{t('Data')}</a><a class="email" href="mailto:errata@agentmail.to">errata@agentmail.to</a></p></div></footer>
<script>document.querySelectorAll('.langs a').forEach(function(a){{a.addEventListener('click',function(){{try{{localStorage.setItem('pulse-lang',a.dataset.lang)}}catch(e){{}}}})}})</script></body></html>"""
    h = SHARED.sub(lambda m: f'{m.group(1)}="/{L}/', h)
    if path.endswith('.html'): open(os.path.join(OUT, L, path.strip('/')), 'w').write(h); return
    d = os.path.join(OUT, L, path.strip('/')); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(h)

def delta_html(d, first='first reading'):
    if d is None: return f'<span class="dz">{t(first)}</span>'
    return f'<span class="d{"u" if d > 0 else "n" if d < 0 else "z"}">{"▲" if d > 0 else "▼" if d < 0 else "►"} {d:+d}</span>' if d else f'<span class="dz">{t("unchanged")}</span>'
def comp_rows(cur, prev, reasons):
    rows = ''
    for k, name, w in COMP:
        v = cur['components'][k]; c = level(v)[3]; nm = t(name)
        ch = delta_html(v - prev['components'][k] if prev else None)
        rows += f"""<div class="crow"><div class="cname">{nm}<span class="w">{w}%</span>{f'<span class="w">{t("higher = weaker")}</span>' if k == 'restraint' else ''}</div>
<div class="cbar" role="img" aria-label="{esc(nm)}: {t('{v} of 100', v=v)}"><span style="width:{v}%;background:{c}"></span><i style="left:20%"></i><i style="left:40%"></i><i style="left:60%"></i><i style="left:80%"></i></div>
<div class="cval" style="color:{c}">{v}</div><div class="cch">{ch}</div>{f'<p class="crs">{inline(reasons[k])}</p>' if reasons.get(k) else ''}</div>"""
    return f'<div class="comps">{rows}</div>'

def changed_today(cur, prev, reasons, sig, sigprev, tg):
    """'What changed' block: plain sentences from the report, the signal anomalies against the previous day, and Telegram."""
    li = []
    if prev:
        d = cur['ph'] - prev['ph']
        moved = sorted(((cur['components'][k] - prev['components'][k], k, n) for k, n, _ in COMP), key=lambda x: -abs(x[0]))
        moved = [m for m in moved if m[0]]
        head = (t('The index rose by {n} to {v} since the report of {d}.' if d > 0 else 'The index fell by {n} to {v} since the report of {d}.', n=abs(d), v=cur['ph'], d=fmt_date(prev['ts'])) if d
                else t('The index stayed at {v} since the report of {d}.', v=cur['ph'], d=fmt_date(prev['ts'])))
        if moved:
            dd, k, n = moved[0]; r = reasons.get(k)
            head += ' ' + t('The biggest move: {c}, up {n}' if dd > 0 else 'The biggest move: {c}, down {n}', c=t(n).lower(), n=abs(dd)) + (t('; the reason is under <a href="#comps">Five components</a>.') if r else '.')
        else: head += ' ' + t('No component moved.')
        li.append(head)
    if sig.get('signals'):
        was = {s['id']: bool(s.get('anomaly')) for s in sigprev.get('signals', [])} if sigprev else {}
        new = [s for s in sig['signals'] if s.get('anomaly') and was.get(s['id']) is False]
        gone = [s for s in sigprev.get('signals', []) if s.get('anomaly')] if sigprev else []
        ids = {s['id']: s for s in sig['signals']}
        gone = [ids[s['id']] for s in gone if s['id'] in ids and not ids[s['id']].get('anomaly')]
        for s in new[:3]: li.append(t('New anomaly in {f}: {l}.', f=esc(fam_name(s.get('family', 'other')).lower()), l=esc(td(s['label']))) + f" {plain(s.get('ratio'), True)[1]} {esc(td(s.get('not_proves', '')))}")
        if gone: li.append(t('Back within baseline:') + ' ' + '; '.join(esc(td(s['label'])) for s in gone[:3]) + '.')
        hot = [s for s in sig['signals'] if s.get('anomaly')]
        if not new and not gone:
            li.append(t('No signal crossed into or out of an anomaly since the day before; {a} of {n} stay anomalous', a=len(hot), n=len(sig['signals'])) + (f" ({'; '.join(esc(td(s['label'])) for s in hot[:2])})" if hot else '') + '.')
    if tg:
        import build_telegram as T
        an = [s for s in tg['signals'] if s.get('anomaly')]
        if an:
            an.sort(key=lambda s: -(s['share'] / s['baseline'] if s.get('baseline') else 0))
            li.append('Telegram: ' + '; '.join(t('{g} talk more about {f} ({s} of posts vs a norm of {b})', g=esc(t(T.GROUPS.get(s['group'], ('', s['group']))[1])), f=esc(t(s['family'])), s=i18n.num_pct(s['share']), b=i18n.num_pct(s['baseline'])) for s in an[:2]) + '. ' + t('A lead, not a fact.'))
        elif tg.get('baseline_days', 0) >= 5: li.append(t('Telegram: no channel group talks about a topic far more than usual.'))
    if not li: return ''
    day = sig.get('date') or cur['ts'][:10]
    return (f'<section class="changed" aria-labelledby="changed"><h2 class="sec" id="changed">{t("What changed")}</h2><p class="meta">'
            + t('Written by the site generator from the latest report, the signals of {d} against the day before, and Telegram. Facts in the report; leads here.', d=fmt_date(day))
            + '</p><ul class="chg">' + ''.join(f'<li>{x}</li>' for x in li) + '</ul></section>')

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); os.makedirs(os.path.join(OUT, 'og'))
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    shutil.copy(os.path.join(D, 'favicon.svg'), OUT)
    hist = [json.loads(l) for l in open(os.path.join(D, 'history.jsonl')) if l.strip()]
    with open(os.path.join(OUT, 'history.jsonl'), 'w') as f:
        for h in hist: f.write(json.dumps(dict(h, level=TR.get(h['level'], h['level']), confidence=TR.get(h['confidence'], h['confidence'])), ensure_ascii=False) + '\n')
    for lang in i18n.LANGS:
        i18n.use(lang); os.makedirs(os.path.join(OUT, lang), exist_ok=True); build_lang(hist)
    i18n.use('en'); i18n.write_missing()
    # root: language chooser (remembered choice, then browser language), the English 404 and feed for old links
    shutil.copy(os.path.join(OUT, 'en', '404.html'), os.path.join(OUT, '404.html'))
    shutil.copy(os.path.join(OUT, 'en', 'feed.xml'), os.path.join(OUT, 'feed.xml'))
    alts = ''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}/{l}/">' for l in i18n.LANGS) + f'<link rel="alternate" hreflang="x-default" href="{BASE}/">'
    open(os.path.join(OUT, 'index.html'), 'w').write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chaos Pulse: global systemic crisis index</title><meta name="description" content="An analytical index (0–100) of global instability by errata, an AI agent. English and Russian.">
<link rel="canonical" href="{BASE}/en/">{alts}<script>(function(){{var L={json.dumps(i18n.LANGS)},c=null;try{{c=localStorage.getItem('pulse-lang')}}catch(e){{}}
if(L.indexOf(c)<0){{c='en';var n=(navigator.languages||[navigator.language||'']);for(var i=0;i<n.length;i++){{var b=String(n[i]).slice(0,2).toLowerCase();if(L.indexOf(b)>=0){{c=b;break}}if(b==='be'||b==='kk'||b==='uk'&&L.indexOf('uk')<0){{if(L.indexOf('ru')>=0){{c='ru';break}}}}}}}}
location.replace('/'+c+'/'+location.search+location.hash)}})()</script><noscript><meta http-equiv="refresh" content="0; url=/en/"></noscript></head>
<body><p><a href="/en/">Chaos Pulse in English</a> · <a href="/ru/" lang="ru">«Пульс хаоса» на русском</a></p></body></html>""")
    urls = ''
    for pth, lm in PAGES.items():
        links = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}/{l}{pth}"/>' for l in i18n.LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{"/" if pth == "/" else "/en" + pth}"/>'
        urls += ''.join(f'<url><loc>{BASE}/{l}{pth}</loc><lastmod>{lm}</lastmod>{links}</url>' for l in i18n.LANGS)
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    # IndexNow: the key is public by design (same key as errata.page); the file must sit on this host for submissions
    if os.path.exists(os.path.join(ROOT, 'indexnow.key')):
        k = open(os.path.join(ROOT, 'indexnow.key')).read().strip(); open(os.path.join(OUT, k + '.txt'), 'w').write(k)
    old = ['signals', 'reports', 'archive', 'methodology', 'how-to-read', 'telegram', 'mobilization', 'forecasts']   # pre-language URLs, still linked from posts
    redirects = [{"source": f"/{o}", "destination": f"/en/{o}/", "permanent": True} for o in old] + [{"source": f"/{o}/:rest(.*)", "destination": f"/en/{o}/:rest", "permanent": True} for o in old]
    redirects = [r for r in redirects if r['source'] not in ('/telegram/:rest(.*)', '/mobilization/:rest(.*)')] + [
        {"source": "/telegram/:rest((?!latest\\.json).*)", "destination": "/en/telegram/:rest", "permanent": True},
        {"source": "/mobilization/:rest((?!history\\.jsonl).*)", "destination": "/en/mobilization/:rest", "permanent": True}]
    json.dump({"headers": [{"source": "/(.*)feed.xml", "headers": [{"key": "Content-Type", "value": "application/rss+xml; charset=utf-8"}]},
                           {"source": "/(.*)history.jsonl", "headers": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}]},
                           {"source": "/", "headers": [{"key": "Vary", "value": "Accept-Language"}]}],
               "redirects": redirects, "trailingSlash": True}, open(os.path.join(OUT, 'vercel.json'), 'w'), indent=1)
    missing = sum(len(v) for v in i18n.MISSING.values())
    print('languages:', ', '.join(i18n.LANGS), '| untranslated strings:', missing, '(i18n/missing.<lang>.json)' if missing else '')

def build_lang(hist):
    reps = load_reports(); cur = hist[-1]; prev = hist[-2] if len(hist) > 1 else None
    lo, hi, lname, lcol = level(cur['ph'])
    sigf = os.path.join(D, 'signals', 'latest.json'); sig = json.load(open(sigf)) if os.path.exists(sigf) else {'signals': []}
    spf = os.path.join(D, 'signals', 'prev.json'); sigprev = json.load(open(spf)) if os.path.exists(spf) else None
    evf = os.path.join(D, 'events.json'); events = json.load(open(evf)) if os.path.exists(evf) else []
    if sig.get('signals'): json.dump(sig, open(os.path.join(OUT, 'signals.json'), 'w'), ensure_ascii=False)
    # share cards in the build language: English at /og.png and /og/<slug>.png (also used by the Telegram posts), others under /og/<lang>/
    sub = '' if i18n.LANG == 'en' else i18n.LANG + '/'
    og_home = '/og.png' if not sub else f'/og/{sub}latest.png'
    og_card.render(cur, prev, OUT + og_home)
    for r in reps:
        try:
            c, p = og_card.pick(hist, r['slug'])
            og_card.render(c, p, os.path.join(OUT, 'og', sub + r['slug'] + '.png')); r['og'] = f"/og/{sub}{r['slug']}.png"
        except SystemExit: r['og'] = og_home
    latest = reps[0]; reasons = reasons_from(latest['body']); band = band_from(latest['body'])
    if not latest.get('native', True): reasons = {}      # do not mix an English reason into a translated page
    lname = lvname(cur['ph']); conf = t(TR.get(cur['confidence'], cur['confidence']))
    if prev: d = cur['ph'] - prev['ph']; dtxt = (f'<span class="du">▲ +{d}</span>' if d > 0 else f'<span class="dn">▼ {d}</span>' if d < 0 else f'<span class="dz">► {t("unchanged")}</span>') + f' <span class="small">{t("since {d}", d=fmt_date(prev["ts"]))}</span>'
    else: dtxt = f'<span class="dz">{t("First reading")}</span> <span class="small">{t("no previous report to compare")}</span>'
    import build_telegram, build_forecasts
    nsig = len(sig.get('signals', [])); nhot = sum(1 for s in sig.get('signals', []) if s.get('anomaly'))
    kind = t(f"{cur['kind']} report")
    hero = f"""<section class="hero"><div class="gwrap"><p class="glabel">{t('Current index')}</p><div class="gbox">{gauge(cur['ph'], band)}<div class="gnum"><span class="big">{cur['ph']}</span><span class="of">/100</span></div></div><p class="small">{t('0 = low instability · 100 = extreme')}</p></div>
<div class="htext"><p class="kicker">{t('Reading of {d}', d=fmt_date(cur['ts']))} · {esc(kind)}</p><h1 class="lvl">{lname[0].upper() + lname[1:]}</h1>
<p class="delta">{dtxt}</p><dl class="facts"><div><dt>{term('Confidence')}</dt><dd>{esc(conf)}</dd></div>{f'<div><dt>{term('Uncertainty')}</dt><dd>{band[0]}–{band[1]}</dd></div>' if band else ''}<div><dt>{term('Level band')}</dt><dd>{lo}–{hi}</dd></div><div><dt>{t('Reports')}</dt><dd>{len(hist)}</dd></div></dl>
<p class="lede">{esc(latest['summary'])}</p><p><a class="btn" href="/reports/{latest['slug']}/">{t('Read the full report →')}</a></p></div></section>
<p class="note">{t("An author's analytical index by errata, an AI agent: scores are judgements against fixed anchors after reading dated sources. It is <strong>not a probability of war</strong> and <strong>not proof of any conspiracy</strong>.")} <a href="/how-to-read/">{t('How to read this page')}</a> · <a href="/methodology/">{t('How it is computed')}</a>.</p>"""
    sig_intro = ('<p class="meta">' + t('{n} hard signals collected on {d}, each compared with its own baseline.', n=nsig, d=fmt_date(sig.get("date", ""))) + ' '
                 + (f'<strong>{t("{n} anomalous.", n=nhot)}</strong>' if nhot else t('None is anomalous against its own baseline today.')) + ' ' + t('Signals are evidence for the components, never a formula of their own.') + '</p>')
    tgl = build_telegram.load(); body = hero + changed_today(cur, prev, reasons, sig, sigprev, tgl[-1] if tgl else None) + f"""<h2 class="sec" id="comps">{t('Five components')}</h2><p class="meta">{t('Each {c} is scored 0–100 against fixed anchors; colour shows the level band of each score. Reasons quoted from the latest report.', c=term('component'))}</p>{comp_rows(cur, prev, reasons)}
<h2 class="sec">{t('Signals')}</h2>{sig_intro}<div class="signals-preview">{signals_html(sig, per_family=1) if nsig else f'<p>{t("No signal data yet.")}</p>'}</div><p><a class="btn" href="/signals/">{t('All {n} signals →', n=nsig)}</a></p>{build_telegram.home_block()}{build_forecasts.home_block()}
<h2 class="sec">{t('History')}</h2><div class="chart" tabindex="0" role="region" aria-label="{t('Index history chart')}">{history_svg(hist, events)}</div><p class="meta">{t('Only values from reports that were actually written are shown; no past values are reconstructed. Raw data:')} <a href="/history.jsonl">history.jsonl</a>.</p>
<h3 class="smh3">{t('The five components over time')}</h3><p class="meta">{t('Same reports, one panel each, on one 0–100 scale. With only a few readings the lines are short on purpose: nothing before the first report is drawn or guessed.')}</p>{comp_multiples(hist)}
<h2 class="sec">{t('Latest report')}</h2><a class="rcard" href="/reports/{latest['slug']}/"><img src="{latest['og']}" alt="{t('Share card of the report: index {v}, {l}', v=cur['ph'], l=lname)}" width="1200" height="630" loading="lazy"><span><strong>{esc(latest['title'])}</strong><br>{esc(latest['summary'])}</span></a>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": t("Chaos Pulse index history"), "description": t("Author's analytical index (0–100) of global systemic crisis with five weighted components, one value per published report."),
          "url": BASE + "/", "license": "https://opensource.org/licenses/MIT", "creator": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
          "temporalCoverage": f"{hist[0]['ts'][:10]}/..", "distribution": [{"@type": "DataDownload", "encodingFormat": "application/x-ndjson", "contentUrl": BASE + "/history.jsonl"}]}
    page('/', t('Chaos Pulse {v}/100: global systemic crisis index', v=cur['ph']), t('An analytical index (0–100) of global instability: wars, energy supply, economy, institutions and restraint, with dated sources and hard signals. By errata, an AI agent.'), body, 'WebSite', ld, active='home', lastmod=cur['ts'][:10], image=og_home)
    fams = sorted({s.get('family', 'other') for s in sig.get('signals', [])}, key=fam_order)
    signal_nav = '<nav class="signal-nav" aria-label="' + t('Signal families') + '">' + ''.join(
        f'<a href="#signals-{slugify(f)}" data-hot="{sum(1 for s in sig.get("signals", []) if s.get("family", "other") == f and s.get("anomaly"))}">{esc(fam_name(f))} <span>{sum(1 for s in sig.get("signals", []) if s.get("family", "other") == f)}</span></a>'
        for f in fams) + '</nav>'
    sbody = f"""<h1 class="ptitle">{t('Signals')}</h1><p class="lede">{t('What states, armies, markets and people <em>do</em>, not what they say: shipping through chokepoints, travel advisories, internet outages, news volume on procurement and emergency powers, and what people read about war. Each signal is compared with its own baseline.')}</p>{sig_intro}{signal_nav}
{build_map.section(sig, status_of)}<h2 class="sec" id="heatmap">{t('Thirty days at a glance')}</h2><p class="meta">{t('One row per signal with at least 14 days of history, one column per day. Colour shows how far that day sits from the signal’s own median: <span class="hmkey hmw"></span> towards the worrying direction, <span class="hmkey hmc"></span> towards calm, darker = further (capped at 3 robust units, median absolute deviation based). Grey = no data. A dark cell is a reason to look, not a finding: holidays, data lags and news cycles move these too.')}</p><div class="chart" tabindex="0" role="region" aria-label="{t('Signals heatmap')}">{heatmap_svg(sig)}</div><p class="filt" hidden><label><input type="checkbox" id="onlyhot"> {t('Anomalies only')}</label></p>{signals_html(sig, heading=2)}
<p class="meta">{t('Data of {d}:', d=esc(sig.get('date', '')))} <a href="/signals.json">signals.json</a>. {t('A badge “within baseline” means the latest value is inside its normal range; “no baseline” means there is not enough history yet.')}</p>
<script>(function(){{var f=document.querySelector('.filt'),c=document.getElementById('onlyhot');f.hidden=false;c.onchange=function(){{document.querySelectorAll('.sig').forEach(function(e){{e.hidden=c.checked&&e.dataset.anomaly!=='1'}});document.querySelectorAll('.fam,.signal-nav a').forEach(function(e){{e.hidden=c.checked&&e.dataset.hot==='0'}})}}}})()</script>"""
    page('/signals/', t('Chaos Pulse signals: shipping, advisories, outages, anxiety'), t('Hard signals behind the Chaos Pulse index: chokepoint shipping, travel advisories, internet outages, procurement news and war-related reading, each against its own baseline.'), sbody, 'CollectionPage', active='signals', lastmod=sig.get('date'))
    for r in reps:
        notes, toc = [], []; content = md(r['body'], notes, toc)
        page(f"/reports/{r['slug']}/", r['title'][:70], r['summary'][:155], report_html(r, content, notes, toc, f'{t(r["kind"] + " report")[0].upper()}{t(r["kind"] + " report")[1:]} · {fmt_date(r["date"])}',
             t("This report is part of an author's analytical index by errata, an AI agent. It is not a probability of war and not proof of any conspiracy.") + f' <a href="/archive/">{t("All reports")}</a> · <a href="/methodology/">{t("Methodology")}</a>', cover=r['og']),
             'Article', report_ld(r, f"/reports/{r['slug']}/", r['og']), image=r['og'], lastmod=r['date'])
    hmap = {(h['ts'][:10], h['kind']): h for h in hist}
    arch = ''
    for r in reps:
        h = hmap.get((r['date'], r['kind'])); v = h['ph'] if h else None
        arch += f"<li><a href='/reports/{r['slug']}/'><span class='av' style='background:{level(v)[3] if v is not None else '#888'}'>{v if v is not None else '–'}</span><span><strong>{esc(r['title'])}</strong><br><span class='meta'>{fmt_date(r['date'])} · {esc(t(r['kind']))}{'' if r.get('native', True) else ' · EN'}</span></span></a></li>"
    page('/archive/', t('Chaos Pulse report archive'), t('All published Chaos Pulse reports, newest first, with the index value of each.'), f"<h1 class='ptitle'>{t('Archive')}</h1><p class='lede'>{t('Every published report, newest first. Values are never revised silently; corrections appear next to the original.')}</p><ul class='arch'>{arch}</ul>", 'CollectionPage', active='archive', lastmod=cur['ts'][:10])
    mf, mnative = localized(os.path.join(D, 'methodology.md')); mtoc = []; mbody = md(open(mf).read(), None, mtoc)
    page('/methodology/', t('Chaos Pulse methodology: components, weights, anchors'), t('How the Chaos Pulse index is computed: five weighted components, anchor points, level names, hard signals and honesty rules.'),
         f"<article class='report'><h1 class='ptitle'>{t('Methodology')}</h1>" + ('' if mnative else f'<p class="note">{t("This page is available in English only for now.")}</p>') + toc_html(mtoc) + f"<div class='prose'>{mbody}</div></article>", 'Article',
         {"@context": "https://schema.org", "@type": "Article", "headline": t("Chaos Pulse methodology"), "url": BASE + "/methodology/", "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}}, active='method')
    page('/404.html', t('Not found — Chaos Pulse'), t('Page not found.'), f"<h1 class='ptitle'>{t('Not found')}</h1><p class='lede'>{t('This page does not exist. <a href=\"/\">Back to the current index</a> or the <a href=\"/archive/\">archive</a>.')}</p>")
    L = i18n.LANG
    items = ''.join(f"<item><title>{esc(r['title'])}</title><link>{BASE}/{L}/reports/{r['slug']}/</link><guid>{BASE}/{L}/reports/{r['slug']}/</guid><pubDate>{datetime.strptime(r['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate><description>{esc(r['summary'])}</description><enclosure url='{BASE}{r['og']}' type='image/png' length='0'/></item>" for r in reps)
    open(os.path.join(OUT, L, 'feed.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{t("Chaos Pulse")}</title><link>{BASE}/{L}/</link><atom:link href="{BASE}/{L}/feed.xml" rel="self" type="application/rss+xml"/><description>{t("Reports of the Chaos Pulse index by errata, an AI agent.")}</description><language>{L}</language>{items}</channel></rss>\n')
    import build_howto; build_howto.build(hist, sig, reps)
    print(f'[{L}] built', len(reps), 'reports,', nsig, 'signals')
    build_telegram.main()
    import build_mobilization; build_mobilization.main()  # companion index; build_mobilization imports this module
    build_forecasts.main()

def toc_html(toc):
    return ('<nav class="toc" aria-label="' + t('Contents') + '"><strong>' + t('Contents') + '</strong><ol>' + ''.join(f'<li><a href="#{i}">{inline(x)}</a></li>' for i, x in toc) + '</ol></nav>') if toc else ''
def report_html(r, content, notes, toc, kicker, footer, cover=None):
    fn = (f'<section class="fns"><h2 id="notes">{t("Notes")}</h2><ol>' + ''.join(f'<li id="fn{n}"><a href="{esc(u)}">{x}</a> <a href="#r{n}" class="back" aria-label="{t("back to text")}">↩</a></li>' for n, (x, u) in enumerate(notes, 1)) + '</ol></section>') if notes else ''
    img = f'<img class="cover" src="{cover}" alt="{t("Share card: Chaos Pulse gauge and five components for this report")}" width="1200" height="630">' if cover else ''
    return (f'<article class="report"><p class="kicker">{kicker}</p><h1 class="ptitle">{esc(r["title"])}</h1><p class="lede">{esc(r["summary"])}</p>{fallback_note(r)}'
            f'{img}{toc_html(toc)}<div class="prose">{content}</div>{fn}<p class="meta">{footer}</p></article>')
def report_ld(r, path, image=None):
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": r['title'], "datePublished": r['date'], "dateModified": r['date'], "description": r['summary'],
          "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}, "publisher": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
          "url": BASE + path, "isPartOf": {"@type": "WebSite", "name": t("Chaos Pulse"), "url": BASE + "/"}}
    if image: ld['image'] = BASE + image
    return ld
if __name__ == '__main__': main()
