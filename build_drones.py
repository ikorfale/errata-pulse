"""Drone and missile alert map (/drones/): where a public Russian alert aggregator (@radarrussiia) reported UAVs,
missile danger, air defence and impacts. Delayed by at least 6 hours and aggregated by district or region on purpose:
no live positions, no live headings (public rules of the Chaos Pulse). Data: data/drones.json, written by the collector.
Directions are drawn as region-to-region corridors from the posts' own words, with the same delay.
Leaflet + OpenStreetMap/CARTO tiles, loaded by the browser; the page itself is static."""
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
    corr = d.get('corridors', []); tl = d.get('timeline', {})
    L = {k: t(v) for k, v in {'play': 'Play', 'pause': 'Pause', 'reports': 'reports', 'corridor': 'corridor', 'hour': 'hour (UTC)'}.items()}
    body = f"""<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">
<style>.dr-tabs button{{font:inherit;padding:.35rem .8rem;border:1px solid var(--line,#ccc);background:transparent;color:inherit;border-radius:6px;cursor:pointer;margin-right:.3rem}}
.dr-tabs button.on{{background:#c0392b;color:#fff;border-color:#c0392b}}#drmap{{background:#1b1e24}}#drmap .leaflet-tile-pane{{filter:invert(1) hue-rotate(180deg) brightness(.85) contrast(.9) saturate(.4)}}
.dr-bar{{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;margin:.6rem 0}}.dr-bar input[type=range]{{flex:1;min-width:200px}}
.dr-clock{{font-variant-numeric:tabular-nums;font-weight:600}}.dr-live{{display:inline-block;width:.55rem;height:.55rem;border-radius:50%;background:#2ecc71;margin-right:.35rem;animation:drp 2s infinite}}
@keyframes drp{{50%{{opacity:.25}}}}.dr-pulse{{animation:drq 1.4s ease-out infinite}}@keyframes drq{{0%{{stroke-opacity:1}}100%{{stroke-opacity:.1}}}}</style>
<h1 class="ptitle">{t('Drone and missile alerts over Russia')}</h1>
<p class="lede">{t('Where public Russian alert aggregators reported drones, missile danger, air defence fire and impacts, and which way the drones were said to fly. A map of how far and how often the air war reaches into Russia, replayed hour by hour, not a live tracker.')}</p>
<p class="note">{t('<strong>Delayed on purpose.</strong> Nothing newer than {h} hours is shown, and directions are drawn as corridors with their ends rounded to about 50 km: a live map of drone positions and headings would be operational information. Every point and arrow is a report by a channel that relays regional alerts and local chats, not a confirmed fact. Data: {r}; cutoff {c} UTC.', h=d.get('delay_hours', 6), r=esc(rng), c='<span id="dr-cut">' + esc(d.get('cutoff', '')[:16].replace('T', ' ')) + '</span>')}</p>
<p class="meta"><span class="dr-live"></span>{t('Data updated every 3 hours; the page picks it up by itself')} · {t('Sources')}: @radarrussiia, @locatorru, @radar_plus_bpla</p>
<div class="dr-tabs" role="tablist"><button data-m="replay" class="on">{t('Replay')}</button><button data-m="corr">{t('Corridors')}</button><button data-m="heat">{t('Where')}</button>
<label style="margin-left:.6rem">{t('Period')} <select id="dr-days"><option value="1">{t('last day')}</option><option value="3">{t('3 days')}</option><option value="7" selected>{t('7 days')}</option><option value="30">{t('30 days')}</option><option value="0">{t('all')}</option></select></label></div>
<div class="dr-bar" id="dr-rbar"><button id="dr-play">▶ {L['play']}</button><input type="range" id="dr-h" min="0" max="0" value="0" aria-label="{L['hour']}"><span class="dr-clock" id="dr-clock"></span></div>
<div id="drmap" style="height:min(72vh,660px);border-radius:8px;margin:.4rem 0 1rem" role="region" aria-label="{t('Map of alert reports')}"></div>
<p class="meta" id="dr-sum"></p>
<p class="meta">{t('Replay: each hour lights the regions that had reports, brighter for more; the arrows are the corridors reported that day. Corridors: an arrow from where the drones were said to come from to where they were said to head, thicker for more reports. Where: circle area is the number of reports per district; colour <span style="color:#9b59b6">■</span> missile danger, <span style="color:#e74c3c">■</span> impacts or shoot-downs, <span style="color:#f39c12">■</span> mostly sightings and danger.')}</p>
<h2 class="sec">{t('Most reported corridors')}</h2><div id="drcor"></div>
<h2 class="sec">{t('Most reported places')}</h2><div id="drtop"></div>
<h2 class="sec">{t('How it works')}</h2><div class="prose"><ul>
<li>{t('Every few minutes a collector reads the public web previews of three alert channels, @radarrussiia, @locatorru and @radar_plus_bpla, and parses each post into places, a region and a kind: sighting, danger, air defence, shoot-down, impact, missile danger, all-clear.')}</li>
<li>{t('Directions come from the words of the posts, not from radar: “from the Ulyanovsk region”, “towards Tosno”, “then on to Tatarstan”, “heading east”. A stated origin or destination becomes an arrow between the two places; a bare compass course is used only internally. The three channels often relay the same alert, so counts overlap.')}</li>
<li>{t('Places are located once with OpenStreetMap’s Nominatim and placed at the centre of the district, town or region. Parsing has noise: a misread name can land in the wrong place.')}</li>
<li>{t('The map feeds the <a href="/">Chaos Pulse</a> as evidence on how deep strikes reach and how often, never as a formula. Built by errata, an AI agent.')}</li></ul></div>
<p class="meta">{t('Data:')} <a href="/drones/data.json">data.json</a>. {t('Map tiles © OpenStreetMap contributors.')}</p>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
<script>(function(){{var LB={json.dumps(L, ensure_ascii=False)};
var m=L.map('drmap',{{scrollWheelZoom:false,zoomControl:true}}).setView([54.5,42],5);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:9,attribution:'© OpenStreetMap'}}).addTo(m);
var g=L.layerGroup().addTo(m),D=null,mode='replay',hours=[],hi=0,timer=null;
function esc(s){{return String(s).replace(/[&<>]/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]}})}}
function days(){{var n=+document.getElementById('dr-days').value,all={{}};D.points.forEach(function(p){{for(var k in p.days)all[k]=1}});Object.keys(D.timeline||{{}}).forEach(function(h){{all[h.slice(0,10)]=1}});var a=Object.keys(all).sort();return n?a.slice(-n):a}}
function arrow(a,b,w,col,op,tip){{var ln=L.polyline([a,b],{{color:col,weight:w,opacity:op}}).addTo(g);if(tip)ln.bindTooltip(tip);
var p1=m.latLngToLayerPoint(a),p2=m.latLngToLayerPoint(b),ang=Math.atan2(p2.y-p1.y,p2.x-p1.x),s=6+w*1.5;
var q=[[p2.x,p2.y],[p2.x-s*Math.cos(ang-0.45),p2.y-s*Math.sin(ang-0.45)],[p2.x-s*Math.cos(ang+0.45),p2.y-s*Math.sin(ang+0.45)]].map(function(x){{return m.layerPointToLatLng(L.point(x[0],x[1]))}});
L.polygon(q,{{color:col,fillColor:col,fillOpacity:op,weight:0}}).addTo(g)}}
function corr(ds){{return (D.corridors||[]).map(function(c){{var n=0;for(var k in c.days)if(ds.indexOf(k)>=0)n+=c.days[k];return [n,c]}}).filter(function(x){{return x[0]}}).sort(function(a,b){{return b[0]-a[0]}})}}
function draw(){{if(!D)return;g.clearLayers();var ds=days(),sum='';
document.getElementById('dr-rbar').style.display=mode=='replay'?'flex':'none';
if(mode=='heat'){{var tot=0,n=0;D.points.forEach(function(p){{var c=0;for(var k in p.days)if(ds.indexOf(k)>=0)c+=p.days[k];if(!c)return;tot+=c;n++;
var K=p.kinds||{{}},T=0;for(var q in K)T+=K[q];var col=(K.missile||0)>=.2*T?'#9b59b6':((K.impact||0)+(K.shootdown||0))>=.2*T?'#e74c3c':'#f39c12',rg=p.level=='region';
L.circleMarker([p.lat,p.lon],{{radius:3+3*Math.sqrt(c),color:col,weight:rg?1.5:1,dashArray:rg?'4 3':null,fillOpacity:rg?.08:.5}}).bindTooltip(esc(p.name)+': '+c).addTo(g)}});sum=tot+' '+LB.reports+' · '+n}}
if(mode=='corr'){{var cs=corr(ds),mx=cs.length?cs[0][0]:1;cs.slice(0,120).forEach(function(x){{var c=x[1];arrow(c.a,c.b,1+5*Math.sqrt(x[0]/mx),'#ff7b54',.35+.55*x[0]/mx,esc(c.from)+' → '+esc(c.to)+': '+x[0])}});sum=cs.length+' '+LB.corridor}}
if(mode=='replay'){{hours=Object.keys(D.timeline||{{}}).filter(function(h){{return ds.indexOf(h.slice(0,10))>=0}});var R=document.getElementById('dr-h');R.max=Math.max(0,hours.length-1);if(hi>R.max)hi=+R.max;R.value=hi;frame()}}
if(sum)document.getElementById('dr-sum').textContent=sum}}
function frame(){{g.clearLayers();var h=hours[hi];if(!h)return;document.getElementById('dr-clock').textContent=h.replace('T',' ')+':00 UTC';
var day=h.slice(0,10),cs=corr([day]),mx=cs.length?cs[0][0]:1;cs.slice(0,60).forEach(function(x){{var c=x[1];arrow(c.a,c.b,1+4*Math.sqrt(x[0]/mx),'#ff7b54',.25+.4*x[0]/mx,esc(c.from)+' → '+esc(c.to))}});
var tot=0;[0,1,2].forEach(function(back){{var hh=hours[hi-back];if(!hh)return;var row=D.timeline[hh];for(var r in row){{var ll=D.regions[r];if(!ll)continue;if(!back)tot+=row[r];
L.circleMarker(ll,{{radius:6+5*Math.sqrt(row[r]),color:'#ffd166',weight:back?1:2,fillColor:'#ff9f1c',fillOpacity:back?.12/back:.55,opacity:back?.3/back:1,className:back?'':'dr-pulse'}}).bindTooltip(esc(r)+': '+row[r]).addTo(g)}}}});
document.getElementById('dr-sum').textContent=tot+' '+LB.reports+' · '+LB.hour+' '+(hi+1)+'/'+hours.length}}
function play(){{var b=document.getElementById('dr-play');if(timer){{clearInterval(timer);timer=null;b.textContent='▶ '+LB.play;return}}
b.textContent='❚❚ '+LB.pause;if(hi>=hours.length-1)hi=0;timer=setInterval(function(){{if(hi>=hours.length-1){{play();return}}hi++;document.getElementById('dr-h').value=hi;frame()}},450)}}
function tables(){{var ds=days(),cs=corr(ds);document.getElementById('drcor').innerHTML='<table class="tbl"><tbody>'+cs.slice(0,12).map(function(x){{return '<tr><td>'+esc(x[1].from)+' → '+esc(x[1].to)+'</td><td class="num">'+x[0]+'</td></tr>'}}).join('')+'</tbody></table>';
var rows=[];D.points.forEach(function(p){{var c=0;for(var k in p.days)if(ds.indexOf(k)>=0)c+=p.days[k];if(c)rows.push([c,p.name])}});rows.sort(function(a,b){{return b[0]-a[0]}});
document.getElementById('drtop').innerHTML='<table class="tbl"><tbody>'+rows.slice(0,15).map(function(r){{return '<tr><td>'+esc(r[1])+'</td><td class="num">'+r[0]+'</td></tr>'}}).join('')+'</tbody></table>'}}
document.querySelectorAll('.dr-tabs button').forEach(function(b){{b.onclick=function(){{document.querySelectorAll('.dr-tabs button').forEach(function(x){{x.classList.remove('on')}});b.classList.add('on');mode=b.dataset.m;if(timer)play();draw()}}}});
document.getElementById('dr-days').onchange=function(){{hi=0;draw();tables()}};document.getElementById('dr-play').onclick=play;
document.getElementById('dr-h').oninput=function(e){{hi=+e.target.value;frame()}};m.on('zoomend',function(){{mode=='replay'?frame():draw()}});
function load(first){{fetch('/drones/data.json?'+Date.now()).then(function(r){{return r.json()}}).then(function(j){{var atEnd=!hours.length||hi>=hours.length-1;D=j;document.getElementById('dr-cut').textContent=(j.cutoff||'').slice(0,16).replace('T',' ');
if(mode=='replay'){{hours=Object.keys(D.timeline||{{}}).filter(function(h){{return days().indexOf(h.slice(0,10))>=0}});if(first||atEnd)hi=Math.max(0,hours.length-1)}}draw();tables()}})}}
load(true);setInterval(function(){{if(!timer)load(false)}},300000)}})();</script>"""
    B.page('/drones/', t('Drone and missile alerts over Russia, mapped | Chaos Pulse'), t('Where public alert channels reported drones, missile danger, air defence and impacts across Russia, with reported flight corridors and an hour-by-hour replay. Delayed: the air war’s reach, not a live tracker.'), body, 'Dataset', active='drones')
    print('built drones:', len(pts), 'points')

def esc(s): return html.escape(str(s))
if __name__ == '__main__': main()
