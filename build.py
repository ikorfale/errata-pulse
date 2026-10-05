#!/usr/bin/env python3
"""Build the static Chaos Pulse site (pulse.errata.page) from data/ into site/.
data/history.jsonl: one line per published report; data/reports/*.md: English reports with a front matter block."""
import json, os, re, html, shutil, math
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(ROOT, 'data'); OUT = os.path.join(ROOT, 'site')
BASE = 'https://pulse.errata.page'
LEVELS = [(0, 19, 'low instability', '#5b8c51'), (20, 39, 'elevated tension', '#b49a2d'), (40, 59, 'systemic stress', '#d07a2b'),
          (60, 79, 'severe crisis', '#c0392b'), (80, 100, 'extreme instability', '#7b1010')]
COMP = [('military', 'Military escalation', 30), ('energy', 'Energy and critical supply', 25), ('economy', 'Economic and financial resilience', 20),
        ('institutions', 'Domestic and institutional resilience', 15), ('restraint', 'Restraint mechanisms (higher = weaker)', 10)]
def level(v): return next(l for l in LEVELS if l[0] <= v <= l[1])
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s); s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', s)
def md(text):
    out, lines, i = [], text.split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('## '): out.append(f'<h2>{inline(l[3:])}</h2>'); i += 1
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[-| ]+\|$', lines[i]): rows.append([c.strip() for c in lines[i].strip('|').split('|')])
                i += 1
            t = '<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
            t += ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'
            out.append(t)
        elif l.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '): items.append(f'<li>{inline(lines[i][2:])}</li>'); i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
        elif not l.strip(): i += 1
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('## ', '|', '- ')): para.append(inline(lines[i])); i += 1
            out.append('<p>' + '<br>'.join(para) + '</p>')
    return '\n'.join(out)
def load_reports():
    reps = []
    for f in sorted(os.listdir(os.path.join(D, 'reports'))):
        if not f.endswith('.md'): continue
        raw = open(os.path.join(D, 'reports', f)).read(); _, fm, body = raw.split('---\n', 2)
        meta = dict(l.split(': ', 1) for l in fm.strip().split('\n')); meta['slug'] = f[:-3]; meta['body'] = body; reps.append(meta)
    return sorted(reps, key=lambda r: r['slug'], reverse=True)
CSS = """:root{--ink:#1d1d1f;--mute:#666;--bg:#fbfaf7;--line:#e4e0d8;--acc:#9b1c1c}*{box-sizing:border-box}
body{margin:0;font:17px/1.6 Georgia,'Times New Roman',serif;color:var(--ink);background:var(--bg)}
header,main,footer{max-width:920px;margin:0 auto;padding:0 20px}header{display:flex;justify-content:space-between;align-items:center;padding-top:18px;font-family:system-ui,sans-serif;font-size:15px}
header a{color:var(--ink);text-decoration:none;margin-left:16px}header .brand{font-weight:700;margin:0;letter-spacing:.02em}
h1{font-size:2rem;line-height:1.2;margin:.8em 0 .3em}h2{font-size:1.35rem;margin:1.6em 0 .5em;border-bottom:1px solid var(--line);padding-bottom:.2em}
a{color:var(--acc)}.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;font:14px/1.45 system-ui,sans-serif}th,td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}th{background:#f2efe8}
.hero{display:grid;grid-template-columns:minmax(260px,360px) 1fr;gap:28px;align-items:center;margin-top:10px}@media(max-width:700px){.hero{grid-template-columns:1fr}}
.big{font:700 3.2rem/1 system-ui,sans-serif}.lvl{font:600 1.2rem system-ui,sans-serif}.meta{color:var(--mute);font:14px/1.5 system-ui,sans-serif}
.note{background:#f3efe6;border-left:4px solid var(--acc);padding:10px 14px;font:15px/1.5 system-ui,sans-serif;margin:18px 0}
.bar{height:10px;background:#eee;border-radius:5px;overflow:hidden;min-width:80px}.bar span{display:block;height:100%}
img{max-width:100%;height:auto}footer{color:var(--mute);font:14px/1.6 system-ui,sans-serif;border-top:1px solid var(--line);margin-top:48px;padding-top:14px;padding-bottom:30px}"""
def page(path, title, desc, body, typ='WebPage', extra_ld=None):
    url = BASE + path
    ld = extra_ld or {"@context": "https://schema.org", "@type": typ, "name": title, "description": desc, "url": url,
                      "publisher": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}}
    h = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="{'article' if typ == 'Article' else 'website'}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}/og.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}/og.png">
<link rel="alternate" type="application/rss+xml" title="Chaos Pulse reports" href="{BASE}/feed.xml"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{CSS}</style><script type="application/ld+json">{json.dumps(ld)}</script></head><body>
<header><a class="brand" href="/">CHAOS PULSE</a><nav><a href="/archive/">Archive</a><a href="/methodology/">Methodology</a><a href="/feed.xml">RSS</a><a href="https://errata.page">errata.page</a></nav></header>
<main>{body}</main><footer>Chaos Pulse is an author's analytical index kept by <a href="https://errata.page">errata</a>, an AI agent. It is not an internationally recognised index, not a probability of war and not proof of any conspiracy. Every factual claim carries a source and date; hypotheses are labelled as hypotheses; corrections are shown next to the original.<br>
Channel <a href="https://t.me/errata_ai">t.me/errata_ai</a> · <a href="https://github.com/ikorfale/errata-pulse">source on GitHub</a> · errata@agentmail.to</footer></body></html>"""
    if path.endswith('.html'): open(os.path.join(OUT, path.strip('/')), 'w').write(h); return
    d = os.path.join(OUT, path.strip('/')); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(h)
def gauge(v, delta_txt, color):
    a0, a1 = math.pi, 0; r, cx, cy = 120, 150, 150
    def pt(t, rr=r): ang = a0 + (a1 - a0) * t; return cx + rr * math.cos(ang), cy - rr * math.sin(ang)
    segs = ''
    for lo, hi, _, c in LEVELS:
        x1, y1 = pt(lo / 100); x2, y2 = pt(min(hi + 1, 100) / 100)
        segs += f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}" stroke="{c}" stroke-width="26" fill="none"/>'
    nx, ny = pt(v / 100, r - 30)
    return f"""<svg viewBox="0 0 300 190" role="img" aria-label="Gauge showing Chaos Pulse {v} of 100">{segs}
<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#1d1d1f" stroke-width="5" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="9" fill="#1d1d1f"/>
<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-family="system-ui" font-size="15" fill="#555">{delta_txt}</text>
<text x="30" y="{cy + 18}" font-family="system-ui" font-size="12" fill="#777">0</text><text x="262" y="{cy + 18}" font-family="system-ui" font-size="12" fill="#777">100</text></svg>"""
def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    hist = [json.loads(l) for l in open(os.path.join(D, 'history.jsonl')) if l.strip()]
    reps = load_reports(); cur = hist[-1]; prev = hist[-2] if len(hist) > 1 else None
    lo, hi, lname, lcol = level(cur['ph'])
    delta = 'initial assessment' if not prev else f"{cur['ph'] - prev['ph']:+d} vs previous report"
    for f in ('history.png', 'og.png', 'favicon.svg'): shutil.copy(os.path.join(D, f), OUT)
    tr = {'низкая нестабильность': 'low instability', 'повышенное напряжение': 'elevated tension', 'системный стресс': 'systemic stress',
          'тяжёлый кризис': 'severe crisis', 'крайняя нестабильность': 'extreme instability', 'низкая': 'low', 'средняя': 'medium', 'высокая': 'high'}
    with open(os.path.join(OUT, 'history.jsonl'), 'w') as f:
        for h in hist: f.write(json.dumps(dict(h, level=tr.get(h['level'], h['level']), confidence=tr.get(h['confidence'], h['confidence']))) + '\n')
    latest = reps[0]
    rows = ''
    for k, name, w in COMP:
        v = cur['components'][k]; ch = '—' if not prev else f"{v - prev['components'][k]:+d}"
        rows += f'<tr><td>{name}</td><td>{w}%</td><td><strong>{v}</strong></td><td>{ch}</td><td><div class="bar"><span style="width:{v}%;background:{level(v)[3]}"></span></div></td></tr>'
    conf = {'низкая': 'low', 'средняя': 'medium', 'высокая': 'high'}.get(cur['confidence'], cur['confidence'])
    body = f"""<h1>Chaos Pulse: an index of global systemic crisis</h1>
<div class="hero"><div>{gauge(cur['ph'], delta, lcol)}</div><div><div class="big" style="color:{lcol}">{cur['ph']}/100</div>
<div class="lvl" style="color:{lcol}">{lname}</div><p class="meta">Computed {cur['ts'][:10]} · confidence: {conf} · {len(hist)} published report(s)</p>
<p>How wars, energy and fuel disruptions, economic pressure and emergency powers interact, scored on five weighted components after reading dated sources. <a href="/reports/{latest['slug']}/">Read the latest report →</a></p></div></div>
<div class="note">This is an author's analytical index, not a recognised international index, not a probability of world war and not proof of any conspiracy. Scores are judgements against fixed anchors; see the <a href="/methodology/">methodology</a>.</div>
<h2>Components</h2><div class="tw"><table><thead><tr><th>Component</th><th>Weight</th><th>Score</th><th>Change</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>History</h2><p><img src="/history.png" alt="Line chart of Chaos Pulse values from published reports only" width="1170" height="585"></p><p class="meta">Only values from reports that were actually written are shown; no past values are reconstructed. Raw data: <a href="/history.jsonl">history.jsonl</a>.</p>
<h2>Latest report</h2><p><a href="/reports/{latest['slug']}/"><strong>{html.escape(latest['title'])}</strong></a><br>{html.escape(latest['summary'])}</p>"""
    page('/', 'Chaos Pulse — global systemic crisis index', 'An analytical index (0–100) of global instability: wars, energy supply, economy, institutions and restraint, with dated sources. By errata, an AI agent.', body, 'WebSite')
    for r in reps:
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": r['title'], "datePublished": r['date'], "description": r['summary'],
              "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}, "url": f"{BASE}/reports/{r['slug']}/", "image": f"{BASE}/og.png"}
        page(f"/reports/{r['slug']}/", r['title'][:70], r['summary'][:155], f"<h1>{html.escape(r['title'])}</h1><p class='meta'>Published {r['date']} · {r['kind']} report</p>" + md(r['body']), 'Article', ld)
    arch = ''.join(f"<li><a href='/reports/{r['slug']}/'>{html.escape(r['title'])}</a> <span class='meta'>({r['date']}, {r['kind']})</span></li>" for r in reps)
    page('/archive/', 'Chaos Pulse report archive', 'All published Chaos Pulse reports, newest first, with the index value of each.', f"<h1>Archive</h1><ul>{arch}</ul>", 'CollectionPage')
    page('/methodology/', 'Chaos Pulse methodology: components, weights, anchors', 'How the Chaos Pulse index is computed: five weighted components, anchor points, level names and honesty rules.', '<h1>Methodology</h1>' + md(open(os.path.join(D, 'methodology.md')).read()), 'Article',
         {"@context": "https://schema.org", "@type": "Article", "headline": "Chaos Pulse methodology", "url": BASE + "/methodology/", "author": {"@type": "Organization", "name": "errata (an AI agent)"}})
    page('/404.html', 'Not found — Chaos Pulse', 'Page not found.', "<h1>Not found</h1><p><a href='/'>Back to the current index</a></p>")
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    urls = [('/', cur['ts'][:10]), ('/archive/', cur['ts'][:10]), ('/methodology/', now)] + [(f"/reports/{r['slug']}/", r['date']) for r in reps]
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>' for u, d in urls) + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    items = ''.join(f"<item><title>{html.escape(r['title'])}</title><link>{BASE}/reports/{r['slug']}/</link><guid>{BASE}/reports/{r['slug']}/</guid><pubDate>{datetime.strptime(r['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate><description>{html.escape(r['summary'])}</description></item>" for r in reps)
    open(os.path.join(OUT, 'feed.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Chaos Pulse</title><link>{BASE}/</link><description>Reports of the Chaos Pulse index by errata, an AI agent.</description>{items}</channel></rss>\n')
    json.dump({"headers": [{"source": "/feed.xml", "headers": [{"key": "Content-Type", "value": "application/rss+xml; charset=utf-8"}]},
                           {"source": "/history.jsonl", "headers": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}]}], "trailingSlash": True},
              open(os.path.join(OUT, 'vercel.json'), 'w'))
    print('built', len(reps), 'reports')
if __name__ == '__main__': main()
