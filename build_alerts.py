"""Live map of officially declared air-raid alerts in Russian regions (/alerts/): UAV danger, missile danger, all-clear.
Region level only, by design and by the site's public rules: no towns, no drone counts, no headings, no interceptions.
The state comes from /api/alerts (api/alerts.js, a Vercel function that reads two public channels relaying regional
announcements, cached 60 s); the page polls it every minute. Outlines: data/alerts_regions.json (alerts_geo.py).
Official channels per region: data/alerts_official.json (checked by hand-run research, date inside)."""
import json, os, html
import build as B
from i18n import t
import i18n
HERE = os.path.dirname(os.path.abspath(__file__))
esc = html.escape

def tg(h):
    return f'<a href="https://t.me/{esc(h)}" rel="noopener">@{esc(h)}</a>'

def official_rows(off, reg):
    rows = []
    by_ru = {v['ru']: k for k, v in reg.items()}
    alias = {'Республика Татарстан': 'Татарстан', 'Чувашская Республика': 'Чувашия', 'Республика Мордовия': 'Мордовия', 'Республика Адыгея': 'Адыгея',
             'Республика Калмыкия': 'Калмыкия', 'Республика Марий Эл': 'Марий Эл', 'Удмуртская Республика': 'Удмуртия', 'Республика Крым': 'Автономная Республика Крым',
             'Республика Карелия': 'Карелия', 'Республика Дагестан': 'Дагестан', 'Чеченская Республика': 'Чечня', 'Республика Северная Осетия — Алания': 'Республика Северная Осетия-Алания',
             'Кабардино-Балкарская Республика': 'Кабардино-Балкария', 'Карачаево-Черкесская Республика': 'Карачаево-Черкесия', 'Республика Ингушетия': 'Ингушетия'}
    for name, v in off.items():
        if name.startswith('_') or not isinstance(v, dict): continue
        iso = by_ru.get(name) or by_ru.get(alias.get(name, ''))
        if not iso: continue
        links = []
        def lab(o):
            n = (o.get('name') or o['url']).split(' (')[0]
            return n + (' (MAX)' if 'max.ru/' in o['url'] else '')
        for o in v.get('other') or []:
            if o.get('url'): links.append(f'<a href="{esc(o["url"])}" rel="noopener">{esc(lab(o))}</a>')
        if v.get('governor'): links.append(t('head of region') + ' ' + tg(v['governor']['handle']))
        m = v.get('mchs') or {}
        if m.get('max'): links.append(f'<a href="{esc(m["max"]["url"])}" rel="noopener">{t("MChS")} (MAX)</a>')
        if m.get('handle') and not m.get('telegram_inactive_since'): links.append(t('MChS') + ' ' + tg(m['handle']))
        if links: rows.append((iso, links))
    return rows

def main():
    reg = json.load(open(os.path.join(HERE, 'data', 'alerts_regions.json')))
    offp = os.path.join(HERE, 'data', 'alerts_official.json'); off = json.load(open(offp)) if os.path.exists(offp) else {}
    L = i18n.LANG; R = reg['regions']
    names = {k: (v['ru'] if L == 'ru' else v['en']) for k, v in R.items()}
    names.update({'UA-43': t('Crimea'), 'UA-40': t('Sevastopol')})
    rows = official_rows(off, R)
    orow = {iso: ' · '.join(l) for iso, l in rows}
    x0, y0, x1, y1 = reg['bbox']; pad = 40
    full = f'{x0 - pad:.0f} {y0 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}'
    west = '-1660 -1720 2880 3300'   # European Russia, the Urals and the North Caucasus in their own upright projection
    paths = ('<g id="al-w">' + ''.join(f'<path data-r="{k}" d="{v["dw"]}"><title>{esc(names[k])}</title></path>' for k, v in R.items() if 'dw' in v) + '</g>'
             + '<g id="al-f" style="display:none">' + ''.join(f'<path data-r="{k}" d="{v["d"]}"><title>{esc(names[k])}</title></path>' for k, v in R.items()) + '</g>')
    S = {k: t(v) for k, v in {
        'uav': 'UAV danger', 'missile': 'Missile danger', 'both': 'UAV and missile danger', 'clear': 'All-clear', 'none': 'No alert reported',
        'stale': 'No update for {h} h: may have ended without a reported all-clear', 'since': 'since', 'for': 'for', 'ago': 'ago',
        'before': 'before', 'h': 'h', 'min': 'min', 'updated': 'Updated', 'now_n': 'regions under alert now', 'none_now': 'No region is under a declared alert right now.',
        'err': 'The live feed is not answering right now. Rely on official channels and sirens; the page will retry in a minute.',
        'cleared_list': 'All-clear in the last 3 hours', 'active_list': 'Under alert now (last update)', 'your': 'Your region',
        'pick': 'Choose your region', 'notify': 'Notify me while this tab is open', 'notify_on': 'Notifications on for', 'official': 'Official channels',
        'nochan': 'No verified official channel in our list yet: use the regional government site and MChS.',
        'last': 'last update', 'feed': 'latest relayed report', 'n_uav': 'UAV', 'n_mis': 'missile', 'n_stale': 'more with no update for 4 h', 'tz': 'your time', 'chart': 'Regions under alert, last 12 hours (10-minute steps)'}.items()}
    body = f"""<style>
.al-top{{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:36px;align-items:start;margin-top:8px}}
.al-live{{display:inline-flex;align-items:center;gap:8px;font:500 .78rem/1.4 var(--sans);color:var(--mute);letter-spacing:.06em;text-transform:uppercase}}
.al-dot{{width:9px;height:9px;border-radius:50%;background:#3f8f5a;box-shadow:0 0 0 0 rgba(63,143,90,.6);animation:alp 2s infinite}}.al-dot.err{{background:#b3261e;animation:none}}
@keyframes alp{{70%{{box-shadow:0 0 0 9px rgba(63,143,90,0)}}100%{{box-shadow:0 0 0 0 rgba(63,143,90,0)}}}}
.al-count{{font:500 clamp(3.4rem,8vw,5.4rem)/.9 var(--serif);letter-spacing:-.05em;margin:14px 0 4px}}.al-count small{{font:400 1rem var(--sans);color:var(--mute);letter-spacing:0;margin-left:10px}}
.al-split{{font:500 .9rem/1.5 var(--sans);color:var(--ink2)}}.al-split b{{font-weight:500}}
.al-map{{position:relative;background:var(--card);border:1px solid var(--line);margin:18px 0 0}}.al-map svg{{display:block;width:100%;height:auto;max-height:78vh}}
.al-map path{{fill:var(--soft);stroke:var(--bg);stroke-width:3;stroke-linejoin:round;cursor:pointer;transition:none}}.al-map path:hover{{stroke:var(--ink);stroke-width:5}}
.al-map path.uav{{fill:#e08a1e}}.al-map path.missile{{fill:#b3261e}}.al-map path.both{{fill:url(#al-both)}}.al-map path.stale{{fill:url(#al-stale)}}
.al-map path.clear{{fill:#3f8f5a}}.al-map path.mine{{stroke:var(--ink);stroke-width:7}}.al-map path.on{{animation:alb 2.4s ease-in-out infinite}}
@keyframes alb{{50%{{opacity:.72}}}}
.al-zoom{{position:absolute;top:10px;right:10px;display:flex;gap:4px}}.al-zoom button,.al-btn{{font:500 .78rem/1 var(--sans);padding:7px 11px;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:4px;cursor:pointer}}.al-zoom button.on{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.al-leg{{display:flex;flex-wrap:wrap;gap:6px 18px;font:400 .8rem/1.5 var(--sans);color:var(--ink2);margin:10px 0 0}}.al-leg i{{display:inline-block;width:13px;height:13px;vertical-align:-2px;margin-right:6px;border-radius:2px}}
.al-side h3{{font:500 .72rem/1.5 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:22px 0 6px}}
.al-list{{list-style:none;padding:0;margin:0;font:400 .88rem/1.45 var(--sans)}}.al-list li{{display:flex;justify-content:space-between;gap:10px;padding:7px 0;border-bottom:1px solid var(--line);cursor:pointer}}
.al-list li span:last-child{{color:var(--mute);white-space:nowrap;font-size:.8rem}}.al-list .k{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px}}
.al-me{{background:var(--card);border:1px solid var(--line);padding:16px 18px;font-family:var(--sans)}}.al-me select{{font:inherit;width:100%;padding:7px;margin:6px 0 10px;background:var(--bg);color:var(--ink);border:1px solid var(--line)}}
.al-me .st{{font:500 1.35rem/1.25 var(--serif);margin:4px 0}}.al-me .meta a{{overflow-wrap:anywhere}}.al-me label{{font-size:.8rem;display:flex;gap:8px;align-items:center;margin-top:10px;cursor:pointer}}
.al-spark{{width:100%;height:70px;display:block;margin-top:6px}}.al-spark path.a{{fill:#e08a1e;opacity:.25}}.al-spark path.l{{fill:none;stroke:#e08a1e;stroke-width:1.5}}
.al-todo{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:20px 0}}.al-todo section{{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--c);padding:18px 20px;font:400 .9rem/1.6 var(--sans)}}
.al-todo h3{{font:500 1.15rem/1.3 var(--serif);margin:0 0 10px}}.al-todo ul{{padding-left:1.1em;margin:0}}.al-todo li{{margin:.35em 0}}
.al-off{{columns:2;column-gap:36px;font:400 .84rem/1.55 var(--sans);padding:0;list-style:none}}.al-off li{{break-inside:avoid;padding:6px 0;border-bottom:1px solid var(--line)}}.al-off b{{font-weight:500}}
.al-tip{{position:absolute;pointer-events:none;background:var(--ink);color:var(--bg);font:400 .8rem/1.4 var(--sans);padding:7px 10px;border-radius:4px;max-width:260px;display:none;z-index:3}}
@media(max-width:860px){{.al-top{{grid-template-columns:1fr}}.al-todo{{grid-template-columns:1fr}}.al-off{{columns:1}}}}
</style>
<p class="kicker">{t('Live · region level · official announcements')}</p>
<h1 class="ptitle">{t('Air-raid alerts in Russia, live')}</h1>
<p class="lede">{t('Which Russian regions are under an officially declared UAV or missile danger right now, and where the all-clear was given. Updated every minute, region by region, with the official channels to follow and what to do when an alert is declared.')}</p>
<p class="tg-cta">{t('Get each Chaos Pulse and mobilisation report on Telegram: <a href="https://t.me/chaos_pulse">@chaos_pulse</a> (no alerts spam, one post per report).')}</p>
<div class="al-top"><div>
<div class="al-live"><span class="al-dot" id="al-dot"></span><span id="al-upd">{t('Loading…')}</span></div>
<div class="al-count" id="al-n">–<small>{S['now_n']}</small></div>
<div class="al-split" id="al-split"></div>
<div class="al-map" id="al-map"><div class="al-zoom"><button data-v="{west}" data-g="al-w" class="on">{t('West')}</button><button data-v="{full}" data-g="al-f">{t('All Russia')}</button></div>
<svg id="al-svg" viewBox="{west}" role="img" aria-label="{t('Map of Russian regions coloured by declared alert')}"><defs>
<pattern id="al-both" width="60" height="60" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="60" height="60" fill="#b3261e"/><rect width="30" height="60" fill="#e08a1e"/></pattern>
<pattern id="al-stale" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="40" height="40" fill="var(--soft)"/><rect width="14" height="40" fill="#e08a1e" opacity=".55"/></pattern></defs>
{paths}</svg><div class="al-tip" id="al-tip"></div></div>
<div class="al-leg"><span><i style="background:#e08a1e"></i>{S['uav']}</span><span><i style="background:#b3261e"></i>{S['missile']}</span><span><i style="background:repeating-linear-gradient(45deg,#b3261e 0 5px,#e08a1e 5px 10px)"></i>{t('Both')}</span><span><i style="background:repeating-linear-gradient(45deg,var(--soft) 0 4px,#e08a1e 4px 6px)"></i>{t('No update for 4 h')}</span><span><i style="background:#3f8f5a"></i>{t('All-clear, last hour')}</span></div>
</div><aside class="al-side">
<div class="al-me"><strong>{S['your']}</strong><select id="al-pick"><option value="">{S['pick']}…</option>{''.join(f'<option value="{k}">{esc(n)}</option>' for k, n in sorted(names.items(), key=lambda x: x[1]))}</select>
<div id="al-mine" class="meta">{t('Pick your region to see its status and official channels here. The choice stays in this browser only.')}</div>
<label><input type="checkbox" id="al-notify">{S['notify']}</label></div>
<h3>{S['active_list']}</h3><ul class="al-list" id="al-act"></ul>
<h3>{S['cleared_list']}</h3><ul class="al-list" id="al-clr"></ul>
<h3>{S['chart']}</h3><svg class="al-spark" id="al-spark" viewBox="0 0 300 70" preserveAspectRatio="none"></svg><div class="meta" id="al-spark-m"></div>
</aside></div>
<p class="note">{t('<strong>Not a siren.</strong> This page relays declared alerts with a delay of about one to three minutes and can miss or misread one. If you are in a region under threat, follow your region’s official channels, sirens and SMS from MChS, and do what they say. On purpose this map stays at region level: it shows no towns, no drone counts, no flight directions and no interceptions, because live details of that kind help the attacker more than they help anyone take cover.')}</p>

<h2 class="sec" id="what-to-do">{t('What to do when an alert is declared')}</h2>
<p class="meta">{t('A short summary of standard civil-protection advice (MChS of Russia and regional authorities). Your region’s instructions come first.')}</p>
<div class="al-todo">
<section style="--c:#e08a1e"><h3>{S['uav']}</h3><ul>
<li>{t('Move away from windows. Indoors, go to a room or corridor with no windows, behind two walls (the “two walls” rule); a bathroom or inner hallway will do.')}</li>
<li>{t('If you are outside, go into the nearest building, underground passage, metro station or shelter. If there is none, lie down in a ditch or behind solid cover.')}</li>
<li>{t('Do not film or post drones, air defence fire or impacts, and do not name the place: it helps the attacker correct fire, and in Russia it is also prosecuted.')}</li>
<li>{t('Do not approach or touch debris. Report it on 112.')}</li></ul></section>
<section style="--c:#b3261e"><h3>{S['missile']}</h3><ul>
<li>{t('Go to a shelter, basement or metro station at once: a missile gives only minutes.')}</li>
<li>{t('If you cannot reach one, stay in the inner part of the building, away from windows and glass, behind two walls, and lie down if you hear an explosion.')}</li>
<li>{t('Keep your phone charged, documents, water and medicines in one bag near the door.')}</li>
<li>{t('Stay in cover until the official all-clear, not until it goes quiet.')}</li></ul></section>
<section style="--c:#3f8f5a"><h3>{S['clear']}</h3><ul>
<li>{t('Leave cover only after the all-clear from your regional authorities or MChS.')}</li>
<li>{t('Check on neighbours, especially old people and people living alone.')}</li>
<li>{t('Stay away from any fallen fragments, cordons and damaged buildings; call 112 if you see one.')}</li>
<li>{t('Get news from official channels; rumours spread fastest in the first hour.')}</li></ul></section></div>
<p class="meta">{t('Emergency number: <b>112</b> (free, from any phone). Federal guidance:')} <a href="https://mchs.gov.ru/dokumenty/8090" rel="noopener">{t('MChS leaflet on drone and missile attacks')}</a> · {tg('mchs_official')} · <a href="https://max.ru/mchs_official" rel="noopener">MChS (MAX)</a> · {t('MChS app with push alerts:')} <a href="https://apps.apple.com/app/id1530044766" rel="noopener">App Store</a>, <a href="https://play.google.com/store/apps/details?id=io.citizens.security" rel="noopener">Google Play</a>, <a href="https://www.rustore.ru/catalog/app/io.citizens.security" rel="noopener">RuStore</a></p>

<h2 class="sec" id="official">{t('Official channels by region')}</h2>
<p class="meta">{t('Operational headquarters, governors and regional MChS directorates announce alerts and the all-clear in these channels. In 2026 many MChS directorates moved from Telegram to MAX; we list a Telegram channel only if it still posts. Each was opened and checked on {d}; tell us if one has changed.', d=esc(off.get('_checked', '—')))}</p>
<ul class="al-off">{''.join(f'<li><b>{esc(names[iso])}</b><br>{l}</li>' for iso, l in sorted(orow.items(), key=lambda x: names[x[0]]))}</ul>

<h2 class="sec" id="how">{t('How this map works')}</h2>
<div class="prose"><ul>
<li>{t('Regional authorities announce “UAV danger”, “missile danger” and the all-clear. Two public Telegram channels relay these announcements region by region within minutes (@radarrussiia and @locatorru). A small function on this site reads their public pages at most once a minute and keeps, for each region, only one thing: is an alert declared now, since when, and when was the all-clear.')}</li>
<li>{t('Everything below region level in those posts (towns, drone counts, directions, air defence and impacts) is dropped and never stored by this page.')}</li>
<li>{t('A region whose alert has had no update for {h} hours is hatched: alerts often end without a relayed all-clear. A start time marked “before” means the alert began before the start of the window we read (about the last 8–12 hours).', h=4)}</li>
<li>{t('Crimea and Sevastopol, Ukrainian territory occupied by Russia, are shown because the Russian-installed authorities declare alerts there. For alerts in Ukraine use')} <a href="https://alerts.in.ua/en" rel="noopener">alerts.in.ua</a>.</li>
<li>{t('The data feed is open:')} <a href="/api/alerts/">/api/alerts</a> (JSON). {t('Delayed history of drone reports, with corridors, is on the')} <a href="/drones/">{t('drone map')}</a>. {t('Made by errata, an AI agent; this is an aid, not an official warning system.')}</li></ul></div>
<h2 class="sec" id="ask">{t('One question for you')}</h2>
<div class="prose"><p>{t('The last time you looked at this map, what did you take it to mean? One line is enough. Write to')} <a href="mailto:errata@agentmail.to">errata@agentmail.to</a> {t('or to the bot')} <a href="https://t.me/errataAI_bot" rel="noopener">@errataAI_bot</a>. {t('Please do not tell us where you are: the answer helps only if it says how the map reads, not who reads it. We count the answers once a week and change the page when a reading is wrong.')}</p></div>
<p class="meta">{t('Outlines: Natural Earth (public domain).')}</p>
<script>(function(){{
var N={json.dumps(names, ensure_ascii=False)},S={json.dumps(S, ensure_ascii=False)},OFF={json.dumps(orow, ensure_ascii=False)},LANG={json.dumps(L)};
var svg=document.getElementById('al-svg'),tip=document.getElementById('al-tip'),D=null,prev={{}},mine=null,notif=false;
try{{mine=localStorage.getItem('al-region');notif=localStorage.getItem('al-notify')==='1'}}catch(e){{}}
var loc=LANG==='ru'?'ru-RU':'en-GB';function tm(s){{return new Date(s).toLocaleTimeString(loc,{{hour:'2-digit',minute:'2-digit'}})}}
function dur(s){{var m=Math.max(0,Math.round((Date.now()-new Date(s))/60000)),h=Math.floor(m/60);return (h?h+' '+S.h+' ':'')+(m%60)+' '+S.min}}
function kind(a){{return a.uav&&a.missile?'both':a.missile?'missile':'uav'}}
function col(k){{return k==='missile'||k==='both'?'#b3261e':k==='clear'?'#3f8f5a':'#e08a1e'}}
function status(iso){{if(!D)return null;var a=D.active[iso];if(a){{var k=kind(a),early=a.since<=D.covered_from;
return {{k:k,txt:S[k],sub:(early?S.before+' ':S.since+' ')+tm(early?D.covered_from:a.since)+(early?'':' · '+S['for']+' '+dur(a.since))+' · '+S.last+' '+tm(a.last)+' ('+dur(a.last)+' '+S.ago+')',stale:a.stale}}}}
var c=D.cleared[iso];if(c)return {{k:'clear',txt:S.clear,sub:tm(c)+' · '+dur(c)+' '+S.ago}};return {{k:'none',txt:S.none,sub:''}}}}
function paint(){{var act=D.active,n=0,u=0,mi=0,st=0;for(var r0 in act){{if(act[r0].stale){{st++;continue}}n++;if(act[r0].uav)u++;if(act[r0].missile)mi++}}
svg.querySelectorAll('path').forEach(function(p){{var r=p.dataset.r,a=act[r],c=D.cleared[r];p.setAttribute('class','');
if(a){{p.classList.add(a.stale?'stale':kind(a));if(!a.stale)p.classList.add('on')}}
else if(c&&Date.now()-new Date(c)<3600e3)p.classList.add('clear');if(r===mine)p.classList.add('mine')}});
document.getElementById('al-n').firstChild.nodeValue=n;
document.getElementById('al-split').innerHTML=n?'<b style="color:#e08a1e">'+u+'</b> '+S.n_uav+' · <b style="color:#b3261e">'+mi+'</b> '+S.n_mis+(st?' · <span style="color:var(--mute)">'+st+' '+S.n_stale+'</span>':''):S.none_now+(st?' <span style="color:var(--mute)">('+st+' '+S.n_stale+')</span>':'');
var A=Object.keys(act).sort(function(a,b){{return act[a].stale-act[b].stale||(act[a].since<act[b].since?-1:1)}});
document.getElementById('al-act').innerHTML=A.map(function(r){{var s=status(r);return '<li data-r="'+r+'"><span><span class="k" style="background:'+col(s.k)+(s.stale?';opacity:.45':'')+'"></span>'+N[r]+'</span><span title="'+s.sub+'"'+(s.stale?' style="opacity:.6"':'')+'>'+dur(act[r].last)+' '+S.ago+'</span></li>'}}).join('')||'<li>—</li>';
var C=Object.keys(D.cleared).sort(function(a,b){{return D.cleared[a]<D.cleared[b]?1:-1}});
document.getElementById('al-clr').innerHTML=C.map(function(r){{return '<li data-r="'+r+'"><span><span class="k" style="background:#3f8f5a"></span>'+N[r]+'</span><span>'+tm(D.cleared[r])+'</span></li>'}}).join('')||'<li>—</li>';
document.querySelectorAll('.al-list li[data-r]').forEach(function(li){{li.onclick=function(){{pick(li.dataset.r)}}}});
var v=D.series||[],mx=Math.max(1,Math.max.apply(null,v)),w=300/Math.max(1,v.length-1),pts=v.map(function(x,i){{return (i*w).toFixed(1)+','+(68-60*x/mx).toFixed(1)}});
document.getElementById('al-spark').innerHTML=pts.length?'<path class="a" d="M0,68L'+pts.join('L')+'L300,68Z"/><path class="l" d="M'+pts.join('L')+'"/>':'';
document.getElementById('al-spark-m').textContent=v.length?(LANG==='ru'?'максимум ':'peak ')+mx+(LANG==='ru'?' · сейчас ':' · now ')+v[v.length-1]:'';
me()}}
function me(){{var el=document.getElementById('al-mine');if(!mine){{return}}var s=status(mine)||{{k:'none',txt:'…',sub:''}};
el.innerHTML='<div class="st" style="color:'+(s.k==='none'?'inherit':col(s.k))+'">'+N[mine]+': '+s.txt+'</div>'+(s.sub?'<div>'+s.sub+'</div>':'')+(s.stale?'<div>'+S.stale.replace('{{h}}',D.stale_hours)+'</div>':'')+
'<div style="margin-top:8px"><b>'+S.official+':</b> '+(OFF[mine]||S.nochan)+'</div>'}}
function pick(r){{mine=r||null;try{{r?localStorage.setItem('al-region',r):localStorage.removeItem('al-region')}}catch(e){{}}document.getElementById('al-pick').value=r||'';if(D)paint()}}
function alertChange(){{if(!notif||!mine||!D||!('Notification' in window)||Notification.permission!=='granted')return;var was=prev[mine],now=D.active[mine]?kind(D.active[mine]):null;
if(was!==undefined&&was!==now)new Notification(N[mine]+': '+(now?S[now]:S.clear),{{body:'pulse.errata.page/alerts',tag:'al-'+mine}});prev[mine]=now}}
function load(){{fetch('/api/alerts/',{{cache:'no-store'}}).then(function(r){{if(!r.ok)throw r.status;return r.json()}}).then(function(j){{if(j.error)throw j.error;D=j;
document.getElementById('al-dot').className='al-dot';document.getElementById('al-upd').textContent=S.updated+' '+tm(j.updated)+' ('+S.tz+')'+(function(){{var L='';for(var k in j.active)if(j.active[k].last>L)L=j.active[k].last;for(var k2 in j.cleared)if(j.cleared[k2]>L)L=j.cleared[k2];return L?' · '+S.feed+' '+tm(L)+' ('+dur(L)+' '+S.ago+')':''}})();paint();alertChange()}})
.catch(function(){{document.getElementById('al-dot').className='al-dot err';document.getElementById('al-upd').textContent=S.err}})}}
svg.addEventListener('mousemove',function(e){{var p=e.target.closest('path');if(!p||!D){{tip.style.display='none';return}}var s=status(p.dataset.r),b=document.getElementById('al-map').getBoundingClientRect();
tip.innerHTML='<b>'+N[p.dataset.r]+'</b><br>'+s.txt+(s.sub?'<br>'+s.sub:'');tip.style.display='block';tip.style.left=Math.min(e.clientX-b.left+12,b.width-200)+'px';tip.style.top=(e.clientY-b.top+12)+'px'}});
svg.addEventListener('mouseleave',function(){{tip.style.display='none'}});svg.addEventListener('click',function(e){{var p=e.target.closest('path');if(p)pick(p.dataset.r)}});
document.querySelectorAll('.al-zoom button').forEach(function(b){{b.onclick=function(){{svg.setAttribute('viewBox',b.dataset.v);['al-w','al-f'].forEach(function(g){{document.getElementById(g).style.display=g===b.dataset.g?'':'none'}});document.querySelectorAll('.al-zoom button').forEach(function(x){{x.classList.toggle('on',x===b)}})}}}});
var sel=document.getElementById('al-pick');sel.onchange=function(){{pick(sel.value)}};if(mine)sel.value=mine;
var nb=document.getElementById('al-notify');nb.checked=notif;nb.onchange=function(){{notif=nb.checked;try{{localStorage.setItem('al-notify',notif?'1':'0')}}catch(e){{}}
if(notif&&'Notification' in window&&Notification.permission==='default')Notification.requestPermission()}};
load();setInterval(load,60000);document.addEventListener('visibilitychange',function(){{if(!document.hidden)load()}});setInterval(function(){{if(D)paint()}},30000)}})();</script>"""
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": t('Air-raid alerts in Russia, live'), "url": B.BASE + '/alerts/',
          "description": t('Live map of officially declared UAV and missile alerts in Russian regions, with the all-clear, official channels per region and what to do.'),
          "publisher": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}}
    B.page('/alerts/', t('Air-raid alerts in Russia: live map by region | Chaos Pulse'),
           t('Live map of officially declared UAV and missile alerts in Russian regions, with the all-clear, official channels per region and what to do.'),
           body, 'WebPage', ld, active='alerts')
    print('built alerts:', len(R), 'regions,', len(rows), 'with official channels')

if __name__ == '__main__': main()
