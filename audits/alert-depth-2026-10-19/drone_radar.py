#!/usr/bin/env python3
"""drone_radar.py — UAV/missile alert reports over Russia from the public web previews of alert aggregators
(@radarrussiia, @locatorru, @radar_plus_bpla), no LLM.
Each post names places (districts, towns), a region and a kind (sighting, danger, air defence, shoot-down, impact,
missile danger, all-clear). Collected every few minutes into pulse/drones/events.jsonl (dedup by post id), places
geocoded once through Nominatim (cached in pulse/drones/geo.json, at most GEO_PER_RUN lookups per run, 1.1 s apart).
The channel is an aggregator of regional alerts and local chats: a post is a report, never a confirmed fact.
Public use is DELAYED and AGGREGATED (pulse/drones/public.json: district/region counts, no headings, nothing newer
than DELAY_H hours): a live map of drone positions is an operational detail (CLAUDE.md, Chaos Pulse public rules).
Directions: a post may say where the drones come from ("от Ульяновской области"), where they head ("в направлении
Тосно", "далее на Татарстан") or a compass course ("на восток"). These become vectors: live ones stay private
(pulse/drones/live.json, tools/drone_live.py), public ones are region-to-region corridors with the same delay.
Usage: drone_radar.py              poll the newest page (timer)
       drone_radar.py --backfill N  walk N pages back (≈20 posts each)
       drone_radar.py --public      rewrite public.json only"""
import os, re, sys, json, time, html, urllib.request, urllib.parse, datetime as dt
D = '../../pulse/drones'; EV = f'{D}/events.jsonl'; GEO = f'{D}/geo.json'; PUB = f'{D}/public.json'
CHANNELS = ['radarrussiia', 'locatorru', 'radar_plus_bpla']; UA = 'errata-drone-radar/0.1 (AI agent; errata@agentmail.to)'
GEO_PER_RUN = int(os.environ.get('GEO_PER_RUN', 15)); DELAY_H = 6; LIVE_H = 3; LIVE = f'{D}/live.json'
os.makedirs(D, exist_ok=True)
REGION = re.compile(r'(област|край|республик|автономн|\bАО\b|^г?\.?\s*Санкт-Петербург$|^Санкт-Петербург$|^Москва$|^Севастополь$|^Крым$)', re.I)
PLACE = re.compile(r'(район|\bМО\b|округ|близлежащ|^г\.|^[А-ЯЁ][а-яё-]+(?:\s[А-ЯЁ][а-яё-]+)?$)')
KINDS = [('all_clear', r'отбой'), ('missile', r'ракетн|реактивн|крылат'), ('impact', r'попадан|прил[её]т'),
         ('shootdown', r'сбити|сбит|уничтож'), ('air_defence', r'работа пво'), ('sighting', r'фиксац|пол[её]т|пролёт|пролет|залетает'),
         ('danger', r'опасност')]
COUNT = re.compile(r'от\s+(\d+)\s+БПЛА|(\d+)\s+БПЛА', re.I)

def get(url, timeout=25):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout).read().decode('utf-8', 'replace')

COMPASS = {'север': 0, 'северо-восток': 45, 'восток': 90, 'юго-восток': 135, 'юг': 180, 'юго-запад': 225, 'запад': 270, 'северо-запад': 315}
RX_COMPASS = re.compile(r'\bна (северо-восток|северо-запад|юго-восток|юго-запад|восток|запад|север|юг)\b', re.I)
RX_FROM = re.compile(r'\bот (?!\d)((?:[А-ЯЁ][а-яё.-]+|ГО|г\.)[^.\n;]{0,50}?)(?=\.|$|\n| в направлении| в сторону| далее| на )', re.M)
RX_TO = re.compile(r'(?:в направлении|в сторону|курсом на|далее на|далее по)\s+((?:[А-ЯЁ]|ГО|г\.)[^.\n;]{0,60}?)(?=\.|$|\n|,? далее| и далее)', re.M)
FOOTER = re.compile(r'(📡|✈️ Наш ТГ|Наш MAX|Подписаться|Прислать новость).*', re.S)

FEMININE = {'Самара', 'Тула', 'Калуга', 'Вологда', 'Луга', 'Дубна', 'Кубинка', 'Кострома', 'Пенза', 'Анапа', 'Уфа', 'Ухта', 'Нарва', 'Тосна'}
IRREGULAR = {'Орла': 'Орёл', 'Калуги': 'Калуга', 'Тулы': 'Тула', 'Рязани': 'Рязань', 'Твери': 'Тверь', 'Перми': 'Пермь',
             'Казани': 'Казань', 'Самары': 'Самара', 'Пензы': 'Пенза', 'Уфы': 'Уфа', 'Вологды': 'Вологда', 'Костромы': 'Кострома'}
MAX_KM = 500   # a stated region-to-region course longer than this is a geocoding miss (a namesake village far away), not a corridor

def km(a, b):
    import math
    dy = (a[0] - b[0]) * 111.2; dx = (a[1] - b[1]) * 111.2 * math.cos(math.radians((a[0] + b[0]) / 2))
    return (dx * dx + dy * dy) ** 0.5

def nominative(s):
    """Genitive/accusative region names as written after 'от'/'на' -> the nominative a geocoder knows."""
    s = re.split(r' через |\s*/\s*|, далее|\(', s.strip(' ,'))[0].strip(' ,')
    s = re.sub(r' и (района|близлежащ\w*)', '', s)
    s = re.sub(r'\s+и$', '', s)                                            # "Воронежской области и" -> cut dangling "и"
    s = re.sub(r'^([А-ЯЁ][а-яё-]+)(ск|цк)ого района', r'\1\2ий район', s)   # "Некоузского района" -> "Некоузский район"
    s = re.sub(r'^([А-ЯЁ][а-яё-]+?[^с])\s+область$', r'\1', s) if not re.search(r'(ая|яя) область$', s) else s  # "Валуйки область" -> "Валуйки"
    if s in FEMININE: return s
    if s in IRREGULAR: return IRREGULAR[s]
    if re.search(r'^[А-ЯЁ][а-яё-]+(ую|ой|ая|ий|ого) и ', s) and re.search(r'област|кра[яюй]', s):   # "Псковскую и Тверскую области" -> the first one
        kind = 'область' if 'област' in s else 'край'; s = s.split(' и ')[0].strip()
        s = re.sub(r'(ск|цк|н)(ую|ой)$', r'\1ая', s) + ' ' + kind if kind == 'область' else re.sub(r'(ск)(ий|ого)$', r'\1ий', s) + ' край'
    s = re.sub(r'ских областей$|ской / .*$', 'ской области', s)
    if re.match(r'[А-ЯЁ][а-яё-]+[сц]кой(,|$)', s): s = s.split(',')[0][:-2] + 'ая область'   # "Волгоградской", "Липецкой, ..."
    if re.fullmatch(r'[А-ЯЁ][а-яё-]+(?:ска|цка|жа|ла|да|ра|ва|га|ка|на)', s) and not s.endswith(('ква', 'ина', 'ава')):  # Воронежа -> Воронеж
        return s[:-1]
    for a, b in [(r'ской области$', 'ская область'), (r'цкой области$', 'цкая область'), (r'ной области$', 'ная область'),
                 (r'ской обл\.?$', 'ская область'), (r'ского края$', 'ский край'), (r'ского края$', 'ский край'),
                 (r'^Республики ', 'Республика '), (r'^Республику ', 'Республика '), (r'ую область$', 'ая область'), (r'ую области$', 'ая область'), (r'^Подмосковья?$', 'Московская область'), (r'^Ленобласти$', 'Ленинградская область'),
                 (r'ский край$', 'ский край'), (r'ой области$', 'ая область'), (r'^Чувашии$', 'Чувашская Республика'),
                 (r'^Татарстана?$', 'Республика Татарстан'), (r'^Башкирии$|^Башкортостана?$', 'Республика Башкортостан'),
                 (r'^Удмуртии$', 'Удмуртская Республика'), (r'^Мордовии$', 'Республика Мордовия'), (r'^Крыма$', 'Республика Крым'),
                 (r'^Санкт-Петербурга$', 'Санкт-Петербург'), (r'^Москвы$', 'Москва'), (r'^ЛНР$', 'Луганская область'), (r'^ДНР$', 'Донецкая область')]:
        s2 = re.sub(a, b, s)
        if s2 != s: return s2
    return s

def directions(txt):
    fr = [nominative(m.group(1)) for m in RX_FROM.finditer(txt)]
    to = [nominative(m.group(1)) for m in RX_TO.finditer(txt)]
    cp = RX_COMPASS.search(txt.lower())
    fr = [x for x in fr if not re.search(r'окон|БПЛА|центра|^\d', x)][:2]
    to = [x for x in to if not re.search(r'центра|БПЛА|^Агломерац', x)][:3]
    return fr, to, (COMPASS[cp.group(1)] if cp else None)

def parse(page, ch):
    out = []
    for m in re.finditer(r'data-post="%s/(\d+)"(.*?)(?=data-post="|\Z)' % ch, page, re.S):
        pid, blk = int(m.group(1)), m.group(2)
        tm = re.search(r'datetime="([^"]+)"', blk); bm = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', blk, re.S)
        if not tm or not bm: continue
        txt = html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'<br\s*/?>', '\n', bm.group(1)))).split('❗')[0]
        txt = FOOTER.sub('', txt).strip()
        lines = []
        for ln in txt.split('\n'):
            ln = ln.strip()
            if not ln: continue
            head = ln.split(' - ')[0] if ' - ' in ln else ln
            parts = [p.strip() for p in head.split(',')] if ' - ' in ln or head.count(',') >= 1 else [head]
            lines += [p for p in parts if p]
        regions = [l for l in lines if REGION.search(l) and len(l) < 60]
        low = txt.lower()
        kinds = [k for k, rx in KINDS if re.search(rx, low)]
        places = [l for l in lines if l not in regions and len(l) < 50 and PLACE.search(l) and not re.search(r'бпла|опасн|фиксац|пво|меры|отбой|уйти|[сц]кой$', l, re.I)]
        c = COUNT.search(txt); n = int(c.group(1) or c.group(2)) if c else None
        fr, to, brg = directions(txt)
        places = [p for p in places if not re.match(r'^(от|в направлении|в сторону|далее)\b', p)]
        e = {'id': f'{ch}/{pid}', 'ch': ch, 'ts': tm.group(1)[:19] + 'Z', 'kinds': kinds, 'regions': regions, 'places': places, 'n': n, 'text': txt[:400]}
        if fr: e['from'] = fr
        if to: e['to'] = to
        if brg is not None: e['bearing'] = brg
        out.append(e)
    return out

def load():
    ev = {}
    if os.path.exists(EV):
        for l in open(EV):
            try:
                e = json.loads(l)
                if isinstance(e['id'], int): e['id'] = f"radarrussiia/{e['id']}"; e['ch'] = 'radarrussiia'
                for k in ('from', 'to', 'bearing'): e.pop(k, None)
                if True:
                    fr, to, brg = directions(e['text'])
                    if fr: e['from'] = fr
                    if to: e['to'] = to
                    if brg is not None: e['bearing'] = brg
                ev[e['id']] = e
            except Exception: pass
    return ev

def save(ev):
    tmp = EV + '.tmp'
    with open(tmp, 'w') as f:
        for k in sorted(ev, key=lambda k: (ev[k]['ts'], k)): f.write(json.dumps(ev[k], ensure_ascii=False) + '\n')
    os.replace(tmp, EV)

def geoq(q):
    """What Nominatim is asked for a place key: aggregator padding removed, the key itself stays as written."""
    q = re.sub(r'\s+и близлежащ\w*|^И близлежащие,\s*', '', q)
    return re.sub(r'\bМО\b', 'муниципальный округ', q)

def geocode(ev):
    geo = json.load(open(GEO)) if os.path.exists(GEO) else {}
    want = []
    for e in sorted(ev.values(), key=lambda e: e['ts'], reverse=True):
        reg = e['regions'][-1] if e['regions'] else None
        if reg: want.append(reg)
        for p in e['places']: want.append(f'{p}, {reg}' if reg else p)
        for p in e.get('from', []) + e.get('to', []): want.append(p)
    done = 0
    for q in dict.fromkeys(want):
        if q in geo and (geo[q] or geoq(q) == q): continue   # a miss is retried once its query cleans up differently
        if done >= GEO_PER_RUN: break
        try:
            r = json.loads(get('https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({'q': geoq(q), 'countrycodes': 'ru,ua', 'format': 'json', 'limit': 1})))
            geo[q] = [round(float(r[0]['lat']), 3), round(float(r[0]['lon']), 3)] if r else None
        except Exception as x:
            print('geo fail', q, x); break
        done += 1; time.sleep(1.1)
    json.dump(geo, open(GEO, 'w'), ensure_ascii=False, indent=0)
    return geo, done

def anchor(e, geo):
    """Where a report sits: its first geocoded place, else its region."""
    reg = e['regions'][-1] if e['regions'] else None
    for p in e['places']:
        ll = geo.get(f'{p}, {reg}' if reg else p)
        if ll: return ll, reg
    return (geo.get(reg) if reg else None), reg

def vectors(e, geo):
    """(origin [lat,lon], dest [lat,lon], origin name, dest name, how) for each direction the post states."""
    a, reg = anchor(e, geo); out = []
    if not a: return out
    for f in e.get('from', []):
        ll = geo.get(f)
        if ll and ll != a and km(ll, a) <= MAX_KM: out.append((ll, a, f, reg, 'from')); break
    for t in e.get('to', []):
        ll = geo.get(t)
        if ll and ll != a and km(ll, a) <= MAX_KM: out.append((a, ll, reg, t, 'to')); break
    if e.get('bearing') is not None and not out:
        import math
        r = math.radians(e['bearing']); d = 0.6  # ~60 km, a course, not a destination
        out.append((a, [round(a[0] + d * math.cos(r), 3), round(a[1] + d * math.sin(r) / math.cos(math.radians(a[0])), 3)], reg, None, 'bearing'))
    return out

def public(ev, geo):
    """Delayed, aggregated: per place and per region, counts by kind and by UTC day, nothing newer than DELAY_H.
    Corridors: region-to-region directions stated in posts, counted per day, same delay. Timeline: per hour and
    region, for the replay. live.json (private, never copied to the site) holds the last LIVE_H hours with vectors."""
    now = dt.datetime.now(dt.timezone.utc)
    cut = (now - dt.timedelta(hours=DELAY_H)).strftime('%Y-%m-%dT%H:%M:%SZ')
    pts, cor, tl, live = {}, {}, {}, []
    lcut = (now - dt.timedelta(hours=LIVE_H)).strftime('%Y-%m-%dT%H:%M:%SZ')
    for e in ev.values():
        if e['ts'] > lcut:
            a, reg = anchor(e, geo)
            live.append({'ts': e['ts'], 'ch': e.get('ch'), 'kinds': e['kinds'], 'at': a, 'region': reg, 'places': e['places'],
                         'vec': [list(v) for v in vectors(e, geo)], 'text': e['text'][:200]})
        if e['ts'] > cut or 'all_clear' in e['kinds']: continue
        reg = e['regions'][-1] if e['regions'] else None
        keys = [f'{p}, {reg}' if reg else p for p in e['places']] or ([reg] if reg else [])
        day = e['ts'][:10]
        for k in keys:
            ll = geo.get(k)
            if not ll: continue
            p = pts.setdefault(k, {'name': k, 'lat': ll[0], 'lon': ll[1], 'level': 'place' if e['places'] else 'region', 'days': {}, 'kinds': {}})
            p['days'][day] = p['days'].get(day, 0) + 1
            for kd in e['kinds']: p['kinds'][kd] = p['kinds'].get(kd, 0) + 1
        for o, d, on, dn, how in vectors(e, geo):
            if how == 'bearing' or not on or not dn or on == dn: continue
            # ends rounded to half a degree (~50 km): a corridor, not a track
            on, dn = on.strip(' .'), dn.strip(' .')
            ra, rb = [round(o[0] * 2) / 2, round(o[1] * 2) / 2], [round(d[0] * 2) / 2, round(d[1] * 2) / 2]
            if ra == rb: continue   # both ends in one half-degree cell: no direction left to show
            k = (on, dn); c = cor.setdefault(k, {'from': on, 'to': dn, 'a': [round(o[0] * 2) / 2, round(o[1] * 2) / 2], 'b': [round(d[0] * 2) / 2, round(d[1] * 2) / 2], 'days': {}})
            c['days'][day] = c['days'].get(day, 0) + 1
        if reg and geo.get(reg):
            h = e['ts'][:13]; r = tl.setdefault(h, {})
            r[reg] = r.get(reg, 0) + 1
    regc = {r: geo[r] for h in tl.values() for r in h if geo.get(r)}
    json.dump({'source': ', '.join('t.me/' + c for c in CHANNELS), 'generated': now.strftime('%Y-%m-%dT%H:%MZ'), 'delay_hours': DELAY_H,
               'cutoff': cut, 'note': 'Reports from public alert aggregators, not confirmed facts. Delayed and aggregated on purpose.',
               'points': sorted(pts.values(), key=lambda p: p['name']),
               'corridors': sorted(cor.values(), key=lambda c: -sum(c['days'].values())),
               'timeline': {h: tl[h] for h in sorted(tl)}, 'regions': regc}, open(PUB, 'w'), ensure_ascii=False)
    json.dump({'generated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'hours': LIVE_H, 'reports': sorted(live, key=lambda x: x['ts'])},
              open(LIVE, 'w'), ensure_ascii=False)
    return len(pts), len(cor)

def main():
    ev = load(); n0 = len(ev)
    if '--public' not in sys.argv:
        pages = int(sys.argv[sys.argv.index('--backfill') + 1]) if '--backfill' in sys.argv else 1
        for ch in CHANNELS:
            before = None
            for _ in range(pages):
                try: posts = parse(get(f'https://t.me/s/{ch}' + (f'?before={before}' if before else '')), ch)
                except Exception as x: print('fetch fail', ch, x); break
                if not posts: break
                for p in posts: ev[p['id']] = p
                before = min(int(p['id'].split('/')[1]) for p in posts)
                time.sleep(2 if pages > 1 else 0.5)
        save(ev)
    geo, g = geocode(ev)
    k, c = public(ev, geo)
    print(f'events {n0}->{len(ev)} geocoded+{g} (cache {len(geo)}) public points {k} corridors {c}')

if __name__ == '__main__':
    main()
