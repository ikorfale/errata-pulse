#!/usr/bin/env python3
"""Build the static Chaos Pulse site (pulse.errata.page) from data/ into site/.
data/history.jsonl  one line per published report (never reconstructed)
data/reports/*.md   English reports with a front matter block
data/signals/latest.json  hard signals of the latest collection day
data/events.json    optional dated annotations for the history chart: [{"date": "YYYY-MM-DD", "label": "..."}]"""
import json, os, re, html, shutil, math
from datetime import datetime, timezone
import og_card
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
    if st == 'none': return st, 'Not enough history yet to say what is usual.'
    if ratio >= 1.5: amt = f'{ratio:.1f}× the {what} level'
    elif ratio >= 1.005: amt = f'{round((ratio - 1) * 100)}% above {what}'
    elif ratio > 0.995: amt = f'the same as {what}'
    else: amt = f'{round((1 - ratio) * 100)}% below {what}'
    tail = {'calm': 'calmer than normal', 'normal': 'within the normal range', 'above': 'more tense than normal, not yet an anomaly', 'anomaly': 'far outside the normal range'}[st]
    return st, f'{amt[0].upper() + amt[1:]}: {tail}.'
def pill(st): return f'<span class="pill p-{st}">{STATUS[st]}</span>'
TERMS = {'baseline': 'The usual level of this signal: the median of its own recent history (usually the last 30 days).',
         'anomaly': 'A value far outside its own usual range, by a rule fixed in advance. It is a lead to check, not an event.',
         'component': 'One of the five parts of the index, each scored 0–100 against fixed anchors.',
         'confidence': 'How sure the author is of the score, given the quality and agreement of the sources.',
         'uncertainty': 'The range the index could plausibly be in, given what is unknown; drawn as the outer bracket of the gauge.',
         'level band': 'The named range the score falls into; colours go from green (low) to deep red (extreme).',
         'norm': "A channel group's usual share of posts on a topic: the median of its last 14 days."}
def term(word, key=None): return f'<span class="term" tabindex="0">{word}<span class="tip" role="tooltip">{esc(TERMS[key or word.lower()])} <a href="/how-to-read/#terms">More</a></span></span>'
def esc(s): return html.escape(str(s), quote=True)
def fmt_date(d):
    try: return datetime.strptime(d[:10], '%Y-%m-%d').strftime('%-d %B %Y')
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
            t = '<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inline(c, notes)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
            t += ''.join('<tr>' + ''.join(f'<td>{inline(c, notes)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'
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
def load_reports():
    reps = []
    for f in sorted(os.listdir(os.path.join(D, 'reports'))):
        if not f.endswith('.md'): continue
        raw = open(os.path.join(D, 'reports', f)).read(); _, fm, body = raw.split('---\n', 2)
        meta = dict(l.split(': ', 1) for l in fm.strip().split('\n')); meta['slug'] = f[:-3]; meta['body'] = body; reps.append(meta)
    rank = {'initial': 0, 'daily': 1, 'weekly': 2, 'alert': 3}     # same date: the later kind is the newer reading ('initial' > 'daily' as text)
    return sorted(reps, key=lambda r: (r.get('date', r['slug'][:10]), rank.get(r.get('kind'), 1), r['slug']), reverse=True)
def reasons_from(body):
    """Main reason per component from the report's component table (first cell starts with the component name)."""
    out = {}
    for line in body.split('\n'):
        if not line.startswith('|'): continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        for k, name, _ in COMP:
            if cells and cells[0].lower().startswith(name.split()[0].lower()) and len(cells) >= 4: out[k] = cells[-1]
    return out
def band_from(body):
    m = re.search(r'[Uu]ncertainty (?:range|band) (\d+)\s*[–-]\s*(\d+)', body)
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
    lab = f'Index gauge: {v} of 100, level {level(v)[2]}' + (f', uncertainty range {band[0]} to {band[1]}' if band else '')
    return f'<svg class="gauge" viewBox="0 0 300 150" role="img" aria-label="{lab}">{s}</svg>'
def sparkline(series, anomaly):
    pts = [(p[0], float(p[1])) for p in series if p and p[1] is not None]
    if len(pts) < 2: return ''
    pts = pts[-30:]; vals = [p[1] for p in pts]; lo, hi = min(vals), max(vals); rng = (hi - lo) or 1
    w, h = 120, 30
    xy = [(i * w / (len(pts) - 1), h - 3 - (p[1] - lo) / rng * (h - 6)) for i, p in enumerate(pts)]
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in xy)
    return (f'<svg class="spark{" hot" if anomaly else ""}" viewBox="0 0 {w} {h}" role="img" aria-label="Last {len(pts)} days, {pts[0][0]} to {pts[-1][0]}">'
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
        s += f'<text x="{W - R - 6}" y="{Y(min(hi + 1, 100)) + 13:.1f}" class="bandlab" text-anchor="end">{name}</text>'
    for v in range(0, 101, 20): s += f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" class="ax" text-anchor="end">{v}</text>'
    # x ticks: weekly
    from datetime import timedelta
    t = t0
    while t <= t1:
        s += f'<text x="{X(t):.1f}" y="{H - 10}" class="ax" text-anchor="middle">{t.strftime("%-d %b")}</text>'; t += timedelta(days=max(1, span // 6))
    for e in events:
        try: et = datetime.strptime(e['date'][:10], '%Y-%m-%d')
        except (KeyError, ValueError): continue
        if t0 <= et <= t1:
            s += f'<line x1="{X(et):.1f}" x2="{X(et):.1f}" y1="{T}" y2="{H - B}" class="ev"/><text x="{X(et) + 4:.1f}" y="{T + 12}" class="evlab">{esc(e.get("label", ""))}</text>'
    if len(pts) > 1: s += '<path d="M' + ' L'.join(f'{X(t):.1f},{Y(v):.1f}' for t, v, _ in pts) + '" class="line"/>'
    for t, v, h in pts:
        s += f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="5.5" fill="{level(v)[3]}" class="pt"><title>{t.strftime("%Y-%m-%d")} {h["kind"]}: {v}</title></circle>'
    t, v, h = pts[-1]
    s += f'<text x="{X(t) + 10:.1f}" y="{Y(v) - 10:.1f}" class="ptlab">{v} · {t.strftime("%-d %b")}</text>'
    if len(pts) == 1: s += f'<text x="{X(t) + 10:.1f}" y="{Y(v) + 20:.1f}" class="ax">first reading; the line grows with each report</text>'
    return f'<svg class="hist" viewBox="0 0 {W} {H}" role="img" aria-label="Chaos Pulse values from {len(pts)} published report(s)">{s}</svg>'

# ---------- signals ----------
def fam_name(f): return dict(FAMILIES).get(f, f.replace('_', ' ').capitalize())
def fam_order(f):
    keys = [k for k, _ in FAMILIES]; return keys.index(f) if f in keys else len(keys)
def sig_sort(s): return (0 if s.get('anomaly') else 1, -abs((s.get('ratio') or 1) - 1))
def num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)): return esc(v)
    if v == 0: return '0'
    if abs(v) >= 100: return f'{v:,.0f}'
    if abs(v) >= 1: return f'{v:.1f}'.rstrip('0').rstrip('.')
    return f'{v:.2g}'
def sig_card(s):
    an = s.get('anomaly'); fam = s.get('family', '')
    badge = ('<span class="badge hot">Anomaly</span>' if an else '<span class="badge">Within baseline</span>' if an is False else '<span class="badge na">No baseline</span>')
    r = s.get('ratio'); val = s.get('value')
    st, phrase = plain(r, an, str(s.get('id', '')).startswith(LOW_IS_WORSE))
    if st == 'none' and an is False and not isinstance(r, (int, float)): st, phrase = 'normal', 'No alarm by its own rule; too little history for a percentage.'
    badge = pill(st)
    ratio = f'<span class="plain">{esc(phrase)}</span>'
    base = f'usual level ({term("baseline")}): {num(s["baseline"])}' if s.get('baseline') not in (None, '') else ''
    unit = esc(s.get('unit', '') or '')
    if isinstance(val, list): val = len(val)
    means, notp = s.get('means'), s.get('not_proves')
    g = FAMILY_GUIDE.get(fam.replace('_', ' '), (None, None))
    means = means or g[0]; notp = notp or g[1]
    comp = s.get('component'); compname = dict((k, n) for k, n, _ in COMP).get(comp, comp)
    lst = s.get('list'); extra = ''
    if isinstance(lst, list) and lst: extra = '<p class="sn">' + esc(', '.join(map(str, lst[:12]))) + (' …' if len(lst) > 12 else '') + '</p>'
    note = f'<p class="sn">{esc(s["note"])}</p>' if s.get('note') else ''
    return f"""<article class="sig{' is-hot' if an else ''}" data-anomaly="{'1' if an else '0'}"><div class="sh">{badge}{f'<span class="comp">feeds: {esc(compname)}</span>' if comp else ''}</div>
<h4>{esc(s.get('label', s.get('id', '')))}</h4><div class="sv"><span class="val">{num(val) if val is not None else '—'}</span> <span class="unit">{unit}</span>{sparkline(s.get('series') or [], an)}</div>
<p class="sb">{ratio}</p>{f'<p class="sn">{base}</p>' if base else ''}{note}{extra}
<details class="signal-context"><summary>Interpretation &amp; limits</summary>{f'<p class="mm"><b>May mean:</b> {esc(means)}</p>' if means else ''}{f'<p class="mm"><b>Does not prove:</b> {esc(notp)}</p>' if notp else ''}</details>
<p class="src">Source: {esc(s.get('source', '—'))}</p></article>"""
def signals_html(sig, per_family=None, heading=3):
    sigs = sig.get('signals', []); fams = sorted({s.get('family', 'other') for s in sigs}, key=fam_order)
    out = ''
    for f in fams:
        ss = sorted([s for s in sigs if s.get('family', 'other') == f], key=sig_sort)
        nhot = sum(1 for s in ss if s.get('anomaly')); shown = ss if per_family is None else [s for s in ss if s.get('anomaly')] or ss[:per_family]
        if per_family is not None and len(shown) < per_family: shown = ss[:max(per_family, nhot)]
        out += (f'<section class="fam" id="signals-{slugify(f)}" data-hot="{nhot}"><h{heading}>{esc(fam_name(f))} <span class="cnt">{len(ss)} signal{"s" if len(ss) != 1 else ""}'
                f'{f", {nhot} anomalous" if nhot else ""}</span></h{heading}><div class="cards">' + ''.join(sig_card(s) for s in shown) + '</div></section>')
    return out

# ---------- page shell ----------
CSS = open(os.path.join(ROOT, 'style.css')).read() if os.path.exists(os.path.join(ROOT, 'style.css')) else ''
def page(path, title, desc, body, typ='WebPage', extra_ld=None, image='/og.png', active=''):
    url = BASE + path
    ld = extra_ld or {"@context": "https://schema.org", "@type": typ, "name": title, "description": desc, "url": url,
                      "publisher": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}}
    nav = ''.join(f'<a href="{h}"{" aria-current=page" if active == k else ""}>{n}</a>' for k, h, n in
                  [('home', '/', 'Index'), ('signals', '/signals/', 'Signals'), ('mobil', '/mobilization/', 'Mobilisation'), ('telegram', '/telegram/', 'Telegram'), ('archive', '/archive/', 'Archive'), ('howto', '/how-to-read/', 'How to read'), ('method', '/methodology/', 'Methodology')])
    h = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta name="color-scheme" content="light dark"><meta name="theme-color" content="#f6f4ef" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#1c201b" media="(prefers-color-scheme: dark)">
<meta property="og:site_name" content="Chaos Pulse"><meta property="og:type" content="{'article' if typ == 'Article' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}{image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{BASE}{image}">
<link rel="alternate" type="application/rss+xml" title="Chaos Pulse reports" href="{BASE}/feed.xml"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{CSS}</style><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap"><div class="mast-top"><a class="brand" href="/">Chaos Pulse<span aria-hidden="true">.</span></a><span class="tag">An index of global systemic crisis</span><span class="byline"><a href="https://t.me/chaos_pulse">Telegram ↗</a> · By <a href="https://errata.page">errata ↗</a></span></div><nav aria-label="Main navigation">{nav}</nav></div></header>
<main class="wrap" id="main">{body}</main>
<footer><div class="wrap footer-grid"><p><strong>Chaos Pulse</strong> is an author's analytical index kept by <a href="https://errata.page">errata</a>, an AI agent. It is not an internationally recognised index, not a probability of war and not proof of any conspiracy. Every factual claim carries a source and date; hypotheses are labelled as hypotheses; corrections are shown next to the original. Checks run once a day plus hourly web monitors; this is not continuous watching.</p>
<p class="footer-links"><a href="https://t.me/chaos_pulse">Every report on Telegram: @chaos_pulse ↗</a><a href="https://t.me/errata_ai">errata on Telegram ↗</a><a href="https://github.com/ikorfale/errata-pulse">Source ↗</a><a href="/feed.xml">RSS</a><a href="/history.jsonl">Data</a><a class="email" href="mailto:errata@agentmail.to">errata@agentmail.to</a></p></div></footer></body></html>"""
    if path.endswith('.html'): open(os.path.join(OUT, path.strip('/')), 'w').write(h); return
    d = os.path.join(OUT, path.strip('/')); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(h)

def comp_rows(cur, prev, reasons):
    rows = ''
    for k, name, w in COMP:
        v = cur['components'][k]; c = level(v)[3]
        if prev: d = v - prev['components'][k]; ch = f'<span class="d{"u" if d > 0 else "n" if d < 0 else "z"}">{"▲" if d > 0 else "▼" if d < 0 else "►"} {d:+d}</span>' if d else '<span class="dz">unchanged</span>'
        else: ch = '<span class="dz">first reading</span>'
        rows += f"""<div class="crow"><div class="cname">{name}<span class="w">{w}%</span>{'<span class="w">higher = weaker</span>' if k == 'restraint' else ''}</div>
<div class="cbar" role="img" aria-label="{name}: {v} of 100"><span style="width:{v}%;background:{c}"></span><i style="left:20%"></i><i style="left:40%"></i><i style="left:60%"></i><i style="left:80%"></i></div>
<div class="cval" style="color:{c}">{v}</div><div class="cch">{ch}</div>{f'<p class="crs">{inline(reasons[k])}</p>' if reasons.get(k) else ''}</div>"""
    return f'<div class="comps">{rows}</div>'

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); os.makedirs(os.path.join(OUT, 'og'))
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    hist = [json.loads(l) for l in open(os.path.join(D, 'history.jsonl')) if l.strip()]
    reps = load_reports(); cur = hist[-1]; prev = hist[-2] if len(hist) > 1 else None
    lo, hi, lname, lcol = level(cur['ph'])
    sigf = os.path.join(D, 'signals', 'latest.json'); sig = json.load(open(sigf)) if os.path.exists(sigf) else {'signals': []}
    evf = os.path.join(D, 'events.json'); events = json.load(open(evf)) if os.path.exists(evf) else []
    shutil.copy(os.path.join(D, 'favicon.svg'), OUT)
    with open(os.path.join(OUT, 'history.jsonl'), 'w') as f:
        for h in hist: f.write(json.dumps(dict(h, level=TR.get(h['level'], h['level']), confidence=TR.get(h['confidence'], h['confidence'])), ensure_ascii=False) + '\n')
    if sig.get('signals'): json.dump(sig, open(os.path.join(OUT, 'signals.json'), 'w'), ensure_ascii=False)
    # share cards: latest + one per report
    og_card.render(cur, prev, os.path.join(OUT, 'og.png'))
    for r in reps:
        try: c, p = og_card.pick(hist, r['slug']); og_card.render(c, p, os.path.join(OUT, 'og', r['slug'] + '.png')); r['og'] = f"/og/{r['slug']}.png"
        except SystemExit: r['og'] = '/og.png'
    latest = reps[0]; reasons = reasons_from(latest['body']); band = band_from(latest['body'])
    conf = TR.get(cur['confidence'], cur['confidence'])
    if prev: d = cur['ph'] - prev['ph']; dtxt = (f'<span class="du">▲ +{d}</span>' if d > 0 else f'<span class="dn">▼ {d}</span>' if d < 0 else '<span class="dz">► unchanged</span>') + f' <span class="small">since {fmt_date(prev["ts"])}</span>'
    else: dtxt = '<span class="dz">First reading</span> <span class="small">no previous report to compare</span>'
    import build_telegram
    nsig = len(sig.get('signals', [])); nhot = sum(1 for s in sig.get('signals', []) if s.get('anomaly'))
    hero = f"""<section class="hero"><div class="gwrap"><p class="glabel">Current index</p><div class="gbox">{gauge(cur['ph'], band)}<div class="gnum"><span class="big">{cur['ph']}</span><span class="of">/100</span></div></div><p class="small">0 = low instability · 100 = extreme</p></div>
<div class="htext"><p class="kicker">Reading of {fmt_date(cur['ts'])} · {esc(cur['kind'])} report</p><h1 class="lvl">{lname.capitalize()}</h1>
<p class="delta">{dtxt}</p><dl class="facts"><div><dt>{term('Confidence')}</dt><dd>{esc(conf)}</dd></div>{f'<div><dt>{term('Uncertainty')}</dt><dd>{band[0]}–{band[1]}</dd></div>' if band else ''}<div><dt>{term('Level band')}</dt><dd>{lo}–{hi}</dd></div><div><dt>Reports</dt><dd>{len(hist)}</dd></div></dl>
<p class="lede">{esc(latest['summary'])}</p><p><a class="btn" href="/reports/{latest['slug']}/">Read the full report →</a></p></div></section>
<p class="note">An author's analytical index by errata, an AI agent: scores are judgements against fixed anchors after reading dated sources. It is <strong>not a probability of war</strong> and <strong>not proof of any conspiracy</strong>. <a href="/how-to-read/">How to read this page</a> · <a href="/methodology/">How it is computed</a>.</p>"""
    sig_intro = (f'<p class="meta">{nsig} hard signals collected on {fmt_date(sig.get("date", ""))}, each compared with its own baseline. '
                 + (f'<strong>{nhot} anomalous.</strong>' if nhot else 'None is anomalous against its own baseline today.') + ' Signals are evidence for the components, never a formula of their own.</p>')
    body = hero + f"""<h2 class="sec">Five components</h2><p class="meta">Each {term('component')} is scored 0–100 against fixed anchors; colour shows the level band of each score. Reasons quoted from the latest report.</p>{comp_rows(cur, prev, reasons)}
<h2 class="sec">Signals</h2>{sig_intro}<div class="signals-preview">{signals_html(sig, per_family=1) if nsig else '<p>No signal data yet.</p>'}</div><p><a class="btn" href="/signals/">All {nsig} signals →</a></p>{build_telegram.home_block()}
<h2 class="sec">History</h2><div class="chart" tabindex="0" role="region" aria-label="Index history chart">{history_svg(hist, events)}</div><p class="meta">Only values from reports that were actually written are shown; no past values are reconstructed. Raw data: <a href="/history.jsonl">history.jsonl</a>.</p>
<h2 class="sec">Latest report</h2><a class="rcard" href="/reports/{latest['slug']}/"><img src="{latest['og']}" alt="Share card of the report: index {cur['ph']}, {lname}" width="1200" height="630" loading="lazy"><span><strong>{esc(latest['title'])}</strong><br>{esc(latest['summary'])}</span></a>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Chaos Pulse index history", "description": "Author's analytical index (0–100) of global systemic crisis with five weighted components, one value per published report.",
          "url": BASE + "/", "license": "https://opensource.org/licenses/MIT", "creator": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
          "temporalCoverage": f"{hist[0]['ts'][:10]}/..", "distribution": [{"@type": "DataDownload", "encodingFormat": "application/x-ndjson", "contentUrl": BASE + "/history.jsonl"}]}
    page('/', f"Chaos Pulse {cur['ph']}/100: global systemic crisis index", 'An analytical index (0–100) of global instability: wars, energy supply, economy, institutions and restraint, with dated sources and hard signals. By errata, an AI agent.', body, 'WebSite', ld, active='home')
    signal_nav = '<nav class="signal-nav" aria-label="Signal families">' + ''.join(
        f'<a href="#signals-{slugify(f)}" data-hot="{sum(1 for s in sig.get("signals", []) if s.get("family", "other") == f and s.get("anomaly"))}">{esc(fam_name(f))} <span>{sum(1 for s in sig.get("signals", []) if s.get("family", "other") == f)}</span></a>'
        for f in sorted({s.get('family', 'other') for s in sig.get('signals', [])}, key=fam_order)) + '</nav>'
    sbody = f"""<h1 class="ptitle">Signals</h1><p class="lede">What states, armies, markets and people <em>do</em>, not what they say: shipping through chokepoints, travel advisories, internet outages, news volume on procurement and emergency powers, and what people read about war. Each signal is compared with its own baseline.</p>{sig_intro}{signal_nav}
<p class="filt" hidden><label><input type="checkbox" id="onlyhot"> Anomalies only</label></p>{signals_html(sig, heading=2)}
<p class="meta">Data of {esc(sig.get('date', ''))}: <a href="/signals.json">signals.json</a>. A badge "within baseline" means the latest value is inside its normal range; "no baseline" means there is not enough history yet.</p>
<script>(function(){{var f=document.querySelector('.filt'),c=document.getElementById('onlyhot');f.hidden=false;c.onchange=function(){{document.querySelectorAll('.sig').forEach(function(e){{e.hidden=c.checked&&e.dataset.anomaly!=='1'}});document.querySelectorAll('.fam,.signal-nav a').forEach(function(e){{e.hidden=c.checked&&e.dataset.hot==='0'}})}}}})()</script>"""
    page('/signals/', 'Chaos Pulse signals: shipping, advisories, outages, anxiety', 'Hard signals behind the Chaos Pulse index: chokepoint shipping, travel advisories, internet outages, procurement news and war-related reading, each against its own baseline.', sbody, 'CollectionPage', active='signals')
    for r in reps:
        notes, toc = [], []; content = md(r['body'], notes, toc)
        tochtml = '<nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>' + ''.join(f'<li><a href="#{i}">{inline(t)}</a></li>' for i, t in toc) + '</ol></nav>' if toc else ''
        fn = ('<section class="fns"><h2 id="notes">Notes</h2><ol>' + ''.join(f'<li id="fn{n}"><a href="{esc(u)}">{t}</a> <a href="#r{n}" class="back" aria-label="back to text">↩</a></li>' for n, (t, u) in enumerate(notes, 1)) + '</ol></section>') if notes else ''
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": r['title'], "datePublished": r['date'], "dateModified": r['date'], "description": r['summary'],
              "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}, "publisher": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
              "url": f"{BASE}/reports/{r['slug']}/", "image": BASE + r['og'], "isPartOf": {"@type": "WebSite", "name": "Chaos Pulse", "url": BASE + "/"}}
        rb = f"""<article class="report"><p class="kicker">{esc(r['kind']).capitalize()} report · {fmt_date(r['date'])}</p><h1 class="ptitle">{esc(r['title'])}</h1><p class="lede">{esc(r['summary'])}</p>
<img class="cover" src="{r['og']}" alt="Share card: Chaos Pulse gauge and five components for this report" width="1200" height="630">{tochtml}<div class="prose">{content}</div>{fn}
<p class="meta">This report is part of an author's analytical index by errata, an AI agent. It is not a probability of war and not proof of any conspiracy. <a href="/archive/">All reports</a> · <a href="/methodology/">Methodology</a></p></article>"""
        page(f"/reports/{r['slug']}/", r['title'][:70], r['summary'][:155], rb, 'Article', ld, image=r['og'])
    hmap = {(h['ts'][:10], h['kind']): h for h in hist}
    arch = ''
    for r in reps:
        h = hmap.get((r['date'], r['kind'])); v = h['ph'] if h else None
        arch += f"<li><a href='/reports/{r['slug']}/'><span class='av' style='background:{level(v)[3] if v is not None else '#888'}'>{v if v is not None else '–'}</span><span><strong>{esc(r['title'])}</strong><br><span class='meta'>{fmt_date(r['date'])} · {esc(r['kind'])}</span></span></a></li>"
    page('/archive/', 'Chaos Pulse report archive', 'All published Chaos Pulse reports, newest first, with the index value of each.', f"<h1 class='ptitle'>Archive</h1><p class='lede'>Every published report, newest first. Values are never revised silently; corrections appear next to the original.</p><ul class='arch'>{arch}</ul>", 'CollectionPage', active='archive')
    mtoc = []; mbody = md(open(os.path.join(D, 'methodology.md')).read(), None, mtoc)
    page('/methodology/', 'Chaos Pulse methodology: components, weights, anchors', 'How the Chaos Pulse index is computed: five weighted components, anchor points, level names, hard signals and honesty rules.',
         "<article class='report'><h1 class='ptitle'>Methodology</h1>" + ('<nav class="toc"><strong>Contents</strong><ol>' + ''.join(f'<li><a href="#{i}">{inline(t)}</a></li>' for i, t in mtoc) + '</ol></nav>') + f"<div class='prose'>{mbody}</div></article>", 'Article',
         {"@context": "https://schema.org", "@type": "Article", "headline": "Chaos Pulse methodology", "url": BASE + "/methodology/", "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}}, active='method')
    page('/404.html', 'Not found — Chaos Pulse', 'Page not found.', "<h1 class='ptitle'>Not found</h1><p class='lede'>This page does not exist. <a href='/'>Back to the current index</a> or the <a href='/archive/'>archive</a>.</p>")
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    urls = [('/', cur['ts'][:10]), ('/signals/', sig.get('date', now)), ('/archive/', cur['ts'][:10]), ('/methodology/', now), ('/how-to-read/', cur['ts'][:10])] + [(f"/reports/{r['slug']}/", r['date']) for r in reps]
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>' for u, d in urls) + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    items = ''.join(f"<item><title>{esc(r['title'])}</title><link>{BASE}/reports/{r['slug']}/</link><guid>{BASE}/reports/{r['slug']}/</guid><pubDate>{datetime.strptime(r['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate><description>{esc(r['summary'])}</description><enclosure url='{BASE}{r['og']}' type='image/png' length='0'/></item>" for r in reps)
    open(os.path.join(OUT, 'feed.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Chaos Pulse</title><link>{BASE}/</link><atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/><description>Reports of the Chaos Pulse index by errata, an AI agent.</description><language>en</language>{items}</channel></rss>\n')
    json.dump({"headers": [{"source": "/feed.xml", "headers": [{"key": "Content-Type", "value": "application/rss+xml; charset=utf-8"}]},
                           {"source": "/history.jsonl", "headers": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}]}], "trailingSlash": True},
              open(os.path.join(OUT, 'vercel.json'), 'w'))
    import build_howto; build_howto.build(hist, sig, reps)
    print('built', len(reps), 'reports,', nsig, 'signals')
    os.makedirs(os.path.join(OUT, 'telegram'), exist_ok=True); build_telegram.main()
    import build_mobilization; build_mobilization.main()  # companion index; build_mobilization imports this module
if __name__ == '__main__': main()
