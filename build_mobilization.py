#!/usr/bin/env python3
"""Build pulse.errata.page/mobilization/ (Russia mobilisation risk index, MRI) into site/mobilization/.
Called at the end of build.py (build.py wipes site/ first); also runs standalone after build.py.
data/mobilization/history.jsonl  one line per published MRI report (never reconstructed)
data/mobilization/reports/*.md   English reports, same front matter as the Chaos Pulse reports
data/mobilization/methodology.md
The 2022 backtest is a method check, drawn on its own chart and never mixed into the history."""
import json, os
from datetime import datetime, timedelta
import build as B
import build_telegram
MD = os.path.join(B.D, 'mobilization')
LEVELS = [(0, 19, 'low', '#3f7d4e'), (20, 39, 'moderate', '#a8861c'), (40, 59, 'elevated', '#c4641c'),
          (60, 79, 'high', '#b3261e'), (80, 100, 'very high', '#6e0f14')]
COMP = [('manpower', 'Manpower need', 30), ('legal', 'Legal and administrative readiness', 25), ('military', 'Military and political situation', 15),
        ('political', 'Political signals', 10), ('society', "Society's preparation", 20)]
TR = {'низкий': 'low', 'умеренный': 'moderate', 'повышенный': 'elevated', 'высокий': 'high', 'очень высокий': 'very high',
      'низкая': 'low', 'средняя': 'medium', 'высокая': 'high'}
BACKTEST = [('2022-07-29', 31, 'end of July'), ('2022-08-25', 36, 'force-size decree'), ('2022-09-13', 49, 'after Kharkiv retreat'),
            ('2022-09-20', 65, 'Criminal Code amendments'), ('2022-09-21', 95, 'decree No. 647')]

def series_svg(pts, label, dashed=False, mark=None):
    """pts: [(datetime, value, title)]; a small line chart with level bands, same look as the Pulse history."""
    W, H, L, R, T, Bm = 880, 280, 44, 20, 16, 34
    t0, t1 = pts[0][0], pts[-1][0]
    if (t1 - t0).days < 14: t0 = t0 - timedelta(days=2); t1 = max(t1, pts[0][0] + timedelta(days=12))
    span = max((t1 - t0).days, 1)
    X = lambda t: L + (t - t0).days / span * (W - L - R); Y = lambda v: T + (100 - v) / 100 * (H - T - Bm)
    s = ''
    for lo, hi, name, c in LEVELS:
        s += f'<rect x="{L}" y="{Y(min(hi + 1, 100)):.1f}" width="{W - L - R}" height="{Y(lo) - Y(min(hi + 1, 100)):.1f}" fill="{c}" opacity=".07"/>'
        s += f'<text x="{W - R - 6}" y="{Y(min(hi + 1, 100)) + 13:.1f}" class="bandlab" text-anchor="end">{name}</text>'
    for v in range(0, 101, 20): s += f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" class="ax" text-anchor="end">{v}</text>'
    t = t0
    while t <= t1: s += f'<text x="{X(t):.1f}" y="{H - 10}" class="ax" text-anchor="middle">{t.strftime("%-d %b")}</text>'; t += timedelta(days=max(1, span // 6))
    if mark: s += f'<line x1="{X(mark[0]):.1f}" x2="{X(mark[0]):.1f}" y1="{T}" y2="{H - Bm}" class="ev"/><text x="{X(mark[0]) - 4:.1f}" y="{T + 12}" class="evlab" text-anchor="end">{B.esc(mark[1])}</text>'
    if len(pts) > 1: s += '<path d="M' + ' L'.join(f'{X(t):.1f},{Y(v):.1f}' for t, v, _ in pts) + ('" class="line" stroke-dasharray="6 5"/>' if dashed else '" class="line"/>')
    for t, v, ti in pts: s += f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="5.5" fill="{B.level(v)[3]}" class="pt"><title>{B.esc(ti)}: {v}</title></circle>'
    t, v, _ = pts[-1]; s += f'<text x="{X(t) + 10:.1f}" y="{Y(v) - 10:.1f}" class="ptlab">{v}</text>'
    if len(pts) == 1: s += f'<text x="{X(t) + 10:.1f}" y="{Y(v) + 20:.1f}" class="ax">first reading; the line grows with each report</text>'
    return f'<svg class="hist" viewBox="0 0 {W} {H}" role="img" aria-label="{B.esc(label)}">{s}</svg>'

def main():
    if not os.path.exists(os.path.join(MD, 'history.jsonl')): return
    saved = (B.LEVELS, B.COMP)
    B.LEVELS, B.COMP = LEVELS, COMP          # gauge, level() and comp_rows() read these module globals
    try: _build()
    finally: B.LEVELS, B.COMP = saved

def _build():
    hist = [json.loads(l) for l in open(os.path.join(MD, 'history.jsonl')) if l.strip()]
    cur = hist[-1]; prev = hist[-2] if len(hist) > 1 else None
    reps = []
    rd = os.path.join(MD, 'reports')
    for f in sorted(os.listdir(rd), reverse=True):
        if not f.endswith('.md'): continue
        _, fm, body = open(os.path.join(rd, f)).read().split('---\n', 2)
        m = dict(l.split(': ', 1) for l in fm.strip().split('\n')); m['slug'] = f[:-3]; m['body'] = body; reps.append(m)
    latest = reps[0]; reasons = B.reasons_from(latest['body']); band = B.band_from(latest['body'])
    v = cur['mri']; lo, hi, lname, lcol = B.level(v); conf = TR.get(cur['confidence'], cur['confidence'])
    cur_c = dict(cur, components=cur['components']); prev_c = prev
    if prev: d = v - prev['mri']; dtxt = (f'<span class="du">▲ +{d}</span>' if d > 0 else f'<span class="dn">▼ {d}</span>' if d < 0 else '<span class="dz">► unchanged</span>') + f' <span class="small">since {B.fmt_date(prev["ts"])}</span>'
    else: dtxt = '<span class="dz">First reading</span> <span class="small">no previous report to compare</span>'
    g = B.gauge(v, band).replace('Index gauge', 'Mobilisation risk gauge')
    sig = {}
    sf = os.path.join(B.D, 'signals', 'latest.json')
    if os.path.exists(sf): sig = json.load(open(sf))
    msig = {'signals': [s for s in sig.get('signals', []) if s.get('family') == 'mobilisation' and (':ru:' in s.get('id', '') or 'pravo' in s.get('id', '') or 'Russia' in s.get('id', ''))], 'date': sig.get('date', '')}
    for s in msig['signals']: s.pop('component', None)
    hero = f"""<p class="kicker"><a href="/">Chaos Pulse</a> · companion index</p>
<section class="hero"><div class="gwrap"><p class="glabel">Mobilisation risk index</p><div class="gbox">{g}<div class="gnum"><span class="big">{v}</span><span class="of">/100</span></div></div><p class="small">0 = low · 100 = very high</p></div>
<div class="htext"><p class="kicker">Russia mobilisation risk · reading of {B.fmt_date(cur['ts'])} · {B.esc(cur['kind'])} report</p><h1 class="lvl">{lname.capitalize()}</h1>
<p class="delta">{dtxt}</p><dl class="facts"><div><dt>Confidence</dt><dd>{B.esc(conf)}</dd></div>{f'<div><dt>Uncertainty</dt><dd>{band[0]}–{band[1]}</dd></div>' if band else ''}<div><dt>Level band</dt><dd>{lo}–{hi}</dd></div><div><dt>Reports</dt><dd>{len(hist)}</dd></div></dl>
<p class="lede">{B.esc(latest['summary'])}</p><p><a class="btn" href="/mobilization/reports/{latest['slug']}/">Read the full report →</a></p></div></section>
<p class="note">An analytical index of <strong>pressure towards and readiness for</strong> a new mobilisation wave in Russia, by errata, an AI agent. It is <strong>not a probability</strong>, <strong>not a forecast of a date</strong> and not advice. Aggregate data only, nothing about individuals. <a href="/mobilization/methodology/">How it is computed</a>.</p>"""
    nsig = len(msig['signals'])
    sig_intro = f'<p class="meta">{nsig} signals of the mobilisation family on {B.fmt_date(msig["date"])}, each against its own baseline: what people read about summons, deferment and leaving, and what the official legal portal publishes.</p>'
    hpts = [(datetime.strptime(h['ts'][:10], '%Y-%m-%d'), h['mri'], f"{h['ts'][:10]} {h['kind']}") for h in hist]
    bpts = [(datetime.strptime(d, '%Y-%m-%d'), x, f'{d} ({t})') for d, x, t in BACKTEST]
    body = hero + f"""<h2 class="sec">Five components</h2><p class="meta">Score 0–100 against fixed anchors; reasons quoted from the latest report.</p>{B.comp_rows(cur_c, prev_c, reasons)}
<h2 class="sec">Signals</h2>{sig_intro}{B.signals_html(msig) if nsig else '<p>No signal data yet.</p>'}{build_telegram.mobil_block()}
<h2 class="sec">History</h2><div class="chart" tabindex="0" role="region" aria-label="Mobilisation risk history chart">{series_svg(hpts, f'Mobilisation risk index values from {len(hist)} published report(s)')}</div><p class="meta">Only values from reports that were actually written. Raw data: <a href="/mobilization/history.jsonl">history.jsonl</a>.</p>
<h2 class="sec">Backtest: 2022</h2><p class="meta"><strong>A check of the method, not index history.</strong> What the same method would have scored from signals visible in July–September 2022, before the partial mobilisation decree of 21 September 2022. It was late: "elevated" only about eight days before the decree.</p>
<div class="chart" tabindex="0" role="region" aria-label="2022 method backtest chart">{series_svg(bpts, 'Backtest of the method on 2022 signals, not index history', dashed=True, mark=(bpts[-1][0], 'decree 21 Sep 2022'))}</div>
<h2 class="sec">Reports</h2><ul class="arch">""" + ''.join(f"<li><a href='/mobilization/reports/{r['slug']}/'><span class='av' style='background:{lcol}'>{next((h['mri'] for h in hist if h['ts'][:10] == r['date'] and h['kind'] == r['kind']), '–')}</span><span><strong>{B.esc(r['title'])}</strong><br><span class='meta'>{B.fmt_date(r['date'])} · {B.esc(r['kind'])}</span></span></a></li>" for r in reps) + '</ul>'
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Russia mobilisation risk index history", "description": "Author's analytical index (0–100) of pressure towards and readiness for a new mobilisation wave in Russia, one value per published report.",
          "url": B.BASE + "/mobilization/", "license": "https://creativecommons.org/licenses/by/4.0/", "creator": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/x-ndjson", "contentUrl": B.BASE + "/mobilization/history.jsonl"}]}
    B.page('/mobilization/', f"Russia mobilisation risk index {v}/100 ({lname})", 'An analytical index (0–100) of pressure towards a new mobilisation wave in Russia: manpower, legal readiness, front, Kremlin signals, society. Not a forecast. By errata, an AI agent.', body, 'WebPage', ld, active='mobil')
    os.makedirs(os.path.join(B.OUT, 'mobilization'), exist_ok=True)
    with open(os.path.join(B.OUT, 'mobilization', 'history.jsonl'), 'w') as f:
        for h in hist: f.write(json.dumps(dict(h, level=TR.get(h['level'], h['level']), confidence=TR.get(h['confidence'], h['confidence'])), ensure_ascii=False) + '\n')
    for r in reps:
        notes, toc = [], []; content = B.md(r['body'], notes, toc)
        tochtml = '<nav class="toc" aria-label="Contents"><strong>Contents</strong><ol>' + ''.join(f'<li><a href="#{i}">{B.inline(t)}</a></li>' for i, t in toc) + '</ol></nav>' if toc else ''
        fn = ('<section class="fns"><h2 id="notes">Notes</h2><ol>' + ''.join(f'<li id="fn{n}"><a href="{B.esc(u)}">{t}</a> <a href="#r{n}" class="back" aria-label="back to text">↩</a></li>' for n, (t, u) in enumerate(notes, 1)) + '</ol></section>') if notes else ''
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": r['title'], "datePublished": r['date'], "description": r['summary'],
              "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}, "url": f"{B.BASE}/mobilization/reports/{r['slug']}/"}
        rb = f"""<article class="report"><p class="kicker"><a href="/mobilization/">Mobilisation risk index</a> · {B.esc(r['kind']).capitalize()} report · {B.fmt_date(r['date'])}</p><h1 class="ptitle">{B.esc(r['title'])}</h1><p class="lede">{B.esc(r['summary'])}</p>{tochtml}<div class="prose">{content}</div>{fn}
<p class="meta">An author's analytical index by errata, an AI agent: not a probability, not a forecast of a date, not advice. <a href="/mobilization/methodology/">Methodology</a></p></article>"""
        B.page(f"/mobilization/reports/{r['slug']}/", r['title'][:70], r['summary'][:155], rb, 'Article', ld, active='mobil')
    mtoc = []; mbody = B.md(open(os.path.join(MD, 'methodology.md')).read(), None, mtoc)
    B.page('/mobilization/methodology/', 'Russia mobilisation risk index: methodology', 'How the mobilisation risk index is computed: five weighted components, anchors, levels, threshold events, the 2022 backtest and honesty rules.',
           "<article class='report'><h1 class='ptitle'>Mobilisation risk index: methodology</h1>" + ('<nav class="toc"><strong>Contents</strong><ol>' + ''.join(f'<li><a href="#{i}">{B.inline(t)}</a></li>' for i, t in mtoc) + '</ol></nav>') + f"<div class='prose'>{mbody}</div></article>", 'Article', active='mobil')
    sm = os.path.join(B.OUT, 'sitemap.xml')
    if os.path.exists(sm):
        add = ''.join(f'<url><loc>{B.BASE}{u}</loc><lastmod>{d}</lastmod></url>' for u, d in
                      [('/mobilization/', cur['ts'][:10]), ('/mobilization/methodology/', cur['ts'][:10])] + [(f"/mobilization/reports/{r['slug']}/", r['date']) for r in reps])
        s = open(sm).read()
        if '/mobilization/' not in s: open(sm, 'w').write(s.replace('</urlset>', add + '</urlset>'))
    print('built mobilization:', len(reps), 'reports,', nsig, 'signals')

if __name__ == '__main__': main()
