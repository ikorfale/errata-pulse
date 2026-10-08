"""World map for the Signals page (site stage 3c): US Level 4 advisories, countries with large internet outages (IODA, 48 h)
and the chokepoints of IMF PortWatch coloured by traffic against their own baseline. Static SVG, Equal Earth projection,
country shapes from Natural Earth 1:110m (public domain, data/geo/). Called from build.py; no third-party libraries."""
import json, math, os, html
from i18n import t, td
HERE = os.path.dirname(os.path.abspath(__file__))
W = 960
A1, A2, A3, A4, M = 1.340264, -0.081106, 0.000893, 0.003796, math.sqrt(3) / 2
XMAX, YMAX = 2.70663, 1.31731  # Equal Earth extent for lon ±180, lat ±90
YCUT = 0.86  # crop Antarctica and the far north a little: the map is about shipping lanes and countries
H = round(W / 2 * YCUT * (YMAX / XMAX) * 2)
# Names in the source lists that Natural Earth spells differently (or folds into a larger unit).
ALIAS = {'Burma': 'Myanmar', 'Gaza': 'Palestine', "Cote d'Ivoire": 'Ivory Coast',
         'Federated States Of Micronesia': 'Federated States of Micronesia', 'Sao Tome And Principe': 'São Tomé and Príncipe'}
# Approximate centre of each strait or canal (public geography), keyed by the PortWatch name used in the signal id.
CHOKE = {'Strait of Hormuz': (56.3, 26.6), 'Bab el-Mandeb Strait': (43.3, 12.6), 'Suez Canal': (32.35, 30.5),
         'Bosporus Strait': (29.05, 41.1), 'Kerch Strait': (36.5, 45.3), 'Taiwan Strait': (119.5, 24.5),
         'Malacca Strait': (101.3, 2.5), 'Panama Canal': (-79.7, 9.1), 'Cape of Good Hope': (18.5, -34.4)}

def proj(lon, lat):
    l, p = math.radians(lon), math.radians(lat); t = math.asin(M * math.sin(p)); t2 = t * t; t6 = t2 ** 3
    x = 2 * math.sqrt(3) * l * math.cos(t) / (3 * (9 * A4 * t6 * t2 + 7 * A3 * t6 + 3 * A2 * t2 + A1))
    y = t * (A4 * t6 * t2 + A3 * t6 + A2 * t2 + A1)
    return W / 2 + x / XMAX * W / 2, H / 2 - y / (YMAX * YCUT) * H / 2

def path(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    out = []
    for poly in polys:
        for ring in poly:
            pts = [proj(*c[:2]) for c in ring]
            out.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z')
    return ''.join(out)

def outage_names(sig):
    s = next((x for x in sig.get('signals', []) if x['id'] == 'internet:country-outages'), None)
    return [n.strip() for n in (s or {}).get('note', '').split(',') if n.strip()], (s or {}).get('value')

def map_svg(sig, status_of):
    geo = json.load(open(os.path.join(HERE, 'data', 'geo', 'ne_110m_countries.geojson')))
    by = {x['id']: x for x in sig.get('signals', [])}
    l4 = [ALIAS.get(n, n) for n in by.get('advisories:level4', {}).get('list', [])]
    out, n_out = outage_names(sig); out = [ALIAS.get(n, n) for n in out]
    known = set(); body = []
    for f in sorted(geo['features'], key=lambda f: f['properties']['ADMIN']):
        pr = f['properties']; names = {pr['ADMIN'], pr['NAME'], pr['NAME_LONG']}; known |= names
        a, o = bool(names & set(l4)), bool(names & set(out))
        cls = 'mc' + (' m4' if a else '') + (' mo' if o else '')
        tip = td(pr['NAME']) + (': ' + t('US Level 4 “Do Not Travel”') if a else '') + ('; ' if a and o else ': ' if o else '') + (t('large internet outage in the last 48 h') if o else '')
        body.append(f'<path class="{cls}" d="{path(f["geometry"])}"><title>{html.escape(tip)}</title></path>')
    dots = []
    for name, (lon, lat) in CHOKE.items():
        s = by.get('transit:' + name)
        if not s: continue
        st = status_of(s.get('ratio'), s.get('anomaly'), True); x, y = proj(lon, lat)
        r = s.get('ratio'); rt = t('{r}× its usual traffic', r=f'{r:.2f}') if isinstance(r, (int, float)) else t('no baseline yet')
        dots.append(f'<g class="ck ck-{st}"><circle cx="{x:.1f}" cy="{y:.1f}" r="6"/><title>{html.escape(td(name))}: {s.get("value")} {t("ships/day")}, {rt}</title></g>')
    missing = sorted({n for n in l4 + out if n not in known})
    svg = (f'<svg class="wmap" viewBox="0 0 {W} {H}" role="img" aria-label="{t("World map: US Level 4 advisory countries, countries with large internet outages, and shipping chokepoints coloured by traffic against their baseline")}">'
           f'<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           f'<line x1="0" y1="0" x2="0" y2="5" class="hl"/></pattern></defs>' + ''.join(body) + ''.join(dots) + '</svg>')
    return svg, {'l4': len(l4), 'outages': n_out, 'named': len(out), 'missing': missing}

CSS = """.wmap{display:block;width:100%;height:auto;margin:8px 0 6px}.wmap .mc{fill:var(--soft);stroke:var(--bg);stroke-width:.5}
.wmap .m4{fill:#d9a79b}.wmap .mo{stroke:var(--ink);stroke-width:1.1}.wmap .mo:not(.m4){fill:url(#hatch)}.wmap .hl{stroke:var(--mute);stroke-width:1.6}
.wmap .ck circle{stroke:var(--bg);stroke-width:2}.wmap .ck-calm circle{fill:#3f7d4e}.wmap .ck-normal circle{fill:var(--mute)}.wmap .ck-above circle{fill:#a8661c}.wmap .ck-anomaly circle{fill:#b3261e}.wmap .ck-none circle{fill:var(--bg);stroke:var(--mute);stroke-dasharray:2 2}
.wmap path:hover{stroke:var(--acc);stroke-width:1.2}.mkey{display:inline-block;width:14px;height:10px;vertical-align:-1px;margin:0 4px 0 10px;border:1px solid var(--line)}
.mk4{background:#d9a79b}.mko{background:repeating-linear-gradient(45deg,var(--mute) 0 1.5px,transparent 1.5px 4px);border-color:var(--ink)}
.mkd{border-radius:50%;width:10px;border:0}@media (prefers-color-scheme:dark){.wmap .m4{fill:#7d4a41}.mk4{background:#7d4a41}}"""

def section(sig, status_of):
    svg, n = map_svg(sig, status_of)
    miss = ' ' + t('Not drawn at this scale or not matched to a shape by name: {l}.', l=", ".join(td(x) for x in n["missing"])) if n['missing'] else ''
    if isinstance(n['outages'], int) and n['named'] < n['outages']: miss += ' ' + t('The outage source names {a} of the {b} countries.', a=n["named"], b=n["outages"])
    return (f'<h2 class="sec" id="map">{t("Where")}</h2><p class="meta"><span class="mkey mk4"></span>{t("US “Do Not Travel” (Level 4): {n} countries", n=n["l4"])}'
            f'<span class="mkey mko"></span>{t("large internet outage in the last 48 h (IODA): {n} countries", n=n["outages"])}'
            f'<br>{t("Chokepoints, ships per day against their own baseline:")} <span class="mkey mkd" style="background:#3f7d4e"></span>{t("more ships than usual")}'
            f'<span class="mkey mkd" style="background:#6b7067"></span>{t("normal")}<span class="mkey mkd" style="background:#a8661c"></span>{t("fewer than usual")}'
            f'<span class="mkey mkd" style="background:#b3261e"></span>{t("anomaly. Hover or tap a country or a dot for details.")}{miss}</p>'
            f'<div class="chart" tabindex="0" role="region" aria-label="{t("World map")}">{svg}</div>'
            f'<p class="small">{t("An advisory is a political judgment, an outage has many causes (cable, power, censorship), and a quiet strait can be weather or a data lag. The map shows where to look, not what happened. Country shapes: Natural Earth (public domain).")}</p>')
