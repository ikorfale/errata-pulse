"""build_badge.py — embeddable SVG badges with the latest value of each index, for READMEs and other sites.
/badge.svg (Chaos Pulse) and /badge-mobilization.svg (Russia mobilisation risk), shields.io-like, level colour on the right.
Values come from the published history files only; the date of the reading is part of the badge, so a stale embed says so."""
import json, os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.abspath(__file__))


def width(s):
    # Verdana 11px average advance, close to what shields.io uses; digits and lowercase ~6.5-7px
    return int(sum(7.2 if c.isupper() else 4.2 if c in ' .,:|il' else 6.6 for c in s)) + 12


def svg(label, value, colour, title):
    lw, vw = width(label), width(value)
    w = lw + vw
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<clipPath id="r"><rect width="{w}" height="20" rx="3" fill="#fff"/></clipPath>
<g clip-path="url(#r)"><rect width="{lw}" height="20" fill="#1b1a17"/><rect x="{lw}" width="{vw}" height="20" fill="{colour}"/><rect width="{w}" height="20" fill="url(#s)"/></g>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
<text x="{lw / 2:.1f}" y="15" fill="#010101" fill-opacity=".3">{escape(label)}</text><text x="{lw / 2:.1f}" y="14">{escape(label)}</text>
<text x="{lw + vw / 2:.1f}" y="15" fill="#010101" fill-opacity=".3">{escape(value)}</text><text x="{lw + vw / 2:.1f}" y="14">{escape(value)}</text></g></svg>
'''


def level(levels, v):
    for lo, hi, name, col in levels:
        if lo <= v <= hi:
            return name, col
    return levels[-1][2], levels[-1][3]


def build(out, pulse_levels, mob_levels, mob_tr):
    made = []
    h = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'history.jsonl')) if l.strip()]
    if h:
        last = h[-1]; name, col = level(pulse_levels, last['ph'])
        val = f"{last['ph']} {name} · {last['ts'][:10]}"
        open(os.path.join(out, 'badge.svg'), 'w').write(svg('chaos pulse', val, col, f'Chaos Pulse {last["ph"]}/100, {name}, report of {last["ts"][:10]}'))
        made.append('badge.svg')
    mp = os.path.join(ROOT, 'data', 'mobilization', 'history.jsonl')
    m = [json.loads(l) for l in open(mp) if l.strip()] if os.path.exists(mp) else []
    if m:
        last = m[-1]; name, col = level(mob_levels, last['mri'])
        val = f"{last['mri']} {name} · {last['ts'][:10]}"
        open(os.path.join(out, 'badge-mobilization.svg'), 'w').write(svg('mobilisation risk', val, col, f'Russia mobilisation risk index {last["mri"]}/100, {name}, report of {last["ts"][:10]}'))
        made.append('badge-mobilization.svg')
    return made
