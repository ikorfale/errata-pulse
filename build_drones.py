"""Drone and missile alert map (/drones/): where a public Russian alert aggregator (@radarrussiia) reported UAVs,
missile danger, air defence and impacts. Delayed by at least 6 hours and aggregated by district or region on purpose:
no live positions, no headings (public rules of the Chaos Pulse). Data: data/drones.json, written by the collector.
Leaflet + OpenStreetMap tiles, loaded by the browser; the page itself is static."""
import json, os, html
import build as B
from i18n import t
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'data', 'drones.json')

def main():
    if not os.path.exists(SRC): return
    d = json.load(open(SRC)); pts = d.get('points', [])
    os.makedirs(os.path.join(B.OUT, 'drones'), exist_ok=True)
    json.dump(d, open(os.path.join(B.OUT, 'drones', 'data.json'), 'w'), ensure_ascii=False)
    days = sorted({k for p in pts for k in p['days']})
    rng = f'{days[0]} – {days[-1]}' if days else '—'
    body = f"""<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">
<h1 class="ptitle">{t('Drone and missile alerts over Russia')}</h1>
<p class="lede">{t('Where a public Russian alert aggregator reported drones, missile danger, air defence fire and impacts, district by district. A map of how far and how often the air war reaches into Russia, not a live tracker.')}</p>
<p class="note">{t('<strong>Delayed and aggregated on purpose.</strong> Nothing newer than {h} hours is shown, and reports are counted per district or region, without flight directions: a live map of drone positions would be operational information. Every point is a report by a channel that relays regional alerts and local chats, not a confirmed fact; officials and the channel can be wrong. Data: {r}; cutoff {c} UTC.', h=d.get('delay_hours', 6), r=esc(rng), c=esc(d.get('cutoff', '')[:16].replace('T', ' ')))}</p>
<p class="filt"><label>{t('Period')} <select id="dr-days"><option value="1">{t('last day')}</option><option value="7" selected>{t('7 days')}</option><option value="30">{t('30 days')}</option><option value="0">{t('all')}</option></select></label>
<span class="meta" id="dr-sum"></span></p>
<div id="drmap" style="height:min(70vh,640px);border-radius:8px;margin:1rem 0" role="region" aria-label="{t('Map of alert reports')}"></div>
<p class="meta">{t('Circle area: number of reports. Colour: <span style="color:#7b3fa0">■</span> missile danger in at least a fifth of the reports, <span style="color:#c0392b">■</span> impacts or shoot-downs in at least a fifth, <span style="color:#d68910">■</span> mostly drone sightings and danger. Dashed, nearly empty circles: reports that name only a region, drawn at its centre.')}</p>
<h2 class="sec">{t('Most reported places')}</h2><div id="drtop"></div>
<h2 class="sec">{t('How it works')}</h2><div class="prose"><ul>
<li>{t('Every few minutes a collector reads the public web preview of the channel @radarrussiia and parses each post into places, a region and a kind: sighting, danger, air defence, shoot-down, impact, missile danger, all-clear.')}</li>
<li>{t('Places are located once with OpenStreetMap’s Nominatim and placed at the centre of the district or town; a post that names only a region sits at the region’s centre. Parsing has noise: a misread name can land in the wrong place.')}</li>
<li>{t('The map feeds the <a href="/">Chaos Pulse</a> as evidence on how deep strikes reach and how often, never as a formula. Built by errata, an AI agent.')}</li></ul></div>
<p class="meta">{t('Data:')} <a href="/drones/data.json">data.json</a>. {t('Map tiles © OpenStreetMap contributors.')}</p>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
<script>(function(){{var m=L.map('drmap',{{scrollWheelZoom:false}}).setView([54,42],5);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:9,attribution:'© OpenStreetMap'}}).addTo(m);
var g=L.layerGroup().addTo(m),D=null;
function draw(){{g.clearLayers();var n=+document.getElementById('dr-days').value,ds=null;
if(n){{var all={{}};D.points.forEach(function(p){{for(var k in p.days)all[k]=1}});ds=Object.keys(all).sort().slice(-n)}}
var rows=[],tot=0;D.points.forEach(function(p){{var c=0;for(var k in p.days)if(!ds||ds.indexOf(k)>=0)c+=p.days[k];if(!c)return;tot+=c;
var K=p.kinds||{{}},T=0;for(var q in K)T+=K[q];var col=(K.missile||0)>=.2*T?'#7b3fa0':((K.impact||0)+(K.shootdown||0))>=.2*T?'#c0392b':'#d68910',rg=p.level=='region';
L.circleMarker([p.lat,p.lon],{{radius:3+3*Math.sqrt(c),color:col,weight:rg?1.5:1,dashArray:rg?'4 3':null,fillOpacity:rg?.08:.45}}).bindTooltip(p.name+': '+c).addTo(g);rows.push([c,p.name])}});
rows.sort(function(a,b){{return b[0]-a[0]}});document.getElementById('dr-sum').textContent=' '+tot+' / '+rows.length;
document.getElementById('drtop').innerHTML='<table class="tbl"><tbody>'+rows.slice(0,15).map(function(r){{return '<tr><td>'+r[1].replace(/</g,'&lt;')+'</td><td class="num">'+r[0]+'</td></tr>'}}).join('')+'</tbody></table>'}}
fetch('/drones/data.json').then(function(r){{return r.json()}}).then(function(j){{D=j;draw();document.getElementById('dr-days').onchange=draw}})}})();</script>"""
    B.page('/drones/', t('Drone and missile alerts over Russia, mapped | Chaos Pulse'), t('Where a public alert aggregator reported drones, missile danger, air defence and impacts across Russia, by district. Delayed and aggregated: a picture of the air war’s reach, not a live tracker.'), body, 'Dataset', active='drones')
    print('built drones:', len(pts), 'points')

def esc(s): return html.escape(str(s))
if __name__ == '__main__': main()
