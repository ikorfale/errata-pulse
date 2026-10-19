// /api/alerts: officially declared air-raid alerts in Russian regions, region level only, near real time.
// Reads the public web previews of two Telegram channels that relay regional announcements ("опасность БПЛА",
// "ракетная опасность", "отбой") and keeps, per region, whether an alert is declared now. On purpose it drops
// everything below region level: no towns, no drone counts, no headings, no interceptions (Chaos Pulse public rules).
// Cached at the edge for 60 s, so Telegram sees at most a few requests a minute whatever the traffic.
const CHANNELS = ['radarrussiia', 'locatorru'];
const UA = 'errata-alerts/1.0 (AI agent; https://pulse.errata.page/alerts/; errata@agentmail.to)';
const WINDOW_H = 12, STALE_H = 4, MAX_PAGES = 26, BATCH = 5;
// region stems; M = needs a region word (область/край/...) in the same segment, so a town of the same name is skipped
const REG = [
  ['RU-MOW', /московск\S*\s+обл|подмосков/, 0], ['RU-MOS', /(^|[^а-яё])москв[аеуы]([^а-яё]|$)/, 0],
  ['RU-SPE', /петербург|(^|[^а-яё])спб([^а-яё]|$)/, 0], ['RU-LEN', /ленинградск|ленобл/, 0],
  ['RU-VOR', /воронежск/, 1], ['RU-TUL', /тульск/, 1], ['RU-KLU', /калужск/, 1], ['RU-KDA', /краснодарск|кубан/, 1],
  ['RU-ROS', /ростовск/, 1], ['RU-ORL', /орловск/, 1], ['RU-RYA', /рязанск/, 1], ['RU-LIP', /липецк/, 1],
  ['RU-YAR', /ярославск/, 1], ['RU-SMO', /смоленск/, 1], ['RU-AD', /адыге/, 0], ['RU-VLA', /владимирск/, 1],
  ['RU-PNZ', /пензенск/, 1], ['RU-SAR', /саратовск/, 1], ['RU-IVA', /ивановск/, 1], ['RU-TAM', /тамбовск/, 1],
  ['RU-SAM', /самарск/, 1], ['RU-TA', /татарстан/, 0], ['RU-VGG', /волгоградск/, 1], ['RU-NIZ', /нижегородск/, 1],
  ['RU-ULY', /ульяновск/, 1], ['RU-TVE', /тверск/, 1], ['RU-VLG', /вологодск/, 1], ['RU-BRY', /брянск/, 1],
  ['RU-KRS', /(^|[^а-яё])курск/, 1], ['RU-BEL', /белгородск/, 1], ['RU-KOS', /костромск/, 1], ['RU-CU', /чуваш/, 0],
  ['RU-NGR', /новгородск/, 1], ['RU-MO', /мордови/, 0], ['RU-PSK', /псковск/, 1], ['RU-AST', /астраханск/, 1],
  ['RU-STA', /ставропольск/, 1], ['RU-ORE', /оренбургск/, 1], ['RU-KL', /калмык/, 0], ['RU-KIR', /кировск\S*\s+обл/, 0],
  ['RU-ARK', /архангельск/, 1], ['RU-ME', /марий/, 0], ['RU-UD', /удмурт/, 0], ['RU-PER', /пермск/, 1],
  ['RU-BA', /башкир|башкорт/, 0], ['UA-43', /крым/, 0], ['UA-40', /севастопол/, 0], ['RU-MUR', /мурманск/, 1],
  ['RU-KGD', /калининградск/, 1], ['RU-KR', /карели/, 0], ['RU-TYU', /тюменск/, 1], ['RU-SVE', /свердловск/, 1],
  ['RU-CHE', /челябинск/, 1], ['RU-DA', /дагестан/, 0], ['RU-CE', /чечен|чечн/, 0], ['RU-SE', /осети/, 0],
  ['RU-KB', /кабардин/, 0], ['RU-KC', /карачаев/, 0], ['RU-IN', /ингуш/, 0], ['RU-KO', /(^|[^а-яё])коми([^а-яё]|$)/, 0],
  ['RU-YAN', /ямал/, 0], ['RU-KHM', /ханты|югр/, 0], ['RU-OMS', /(^|[^а-яёт])омск/, 1], ['RU-KGN', /курганск/, 1],
  ['RU-NVS', /новосибирск/, 1], ['RU-TOM', /томск/, 1], ['RU-KEM', /кемеровск|кузбас/, 0], ['RU-ALT', /алтайск\S*\s+кра/, 0],
  ['RU-AL', /республик\S*\s+алтай/, 0], ['RU-KYA', /красноярск/, 1], ['RU-IRK', /иркутск/, 1], ['RU-NEN', /(^|[^-])ненецк/, 0],
  ['RU-KK', /хакас/, 0], ['RU-TY', /тыва|тува/, 0], ['RU-BU', /бурят/, 0], ['RU-ZAB', /забайкал/, 0], ['RU-AMU', /амурск/, 1],
  ['RU-YEV', /еврейск/, 0], ['RU-KHA', /хабаровск/, 1], ['RU-PRI', /приморск\S*\s+кра/, 0], ['RU-SAK', /сахалин/, 0],
  ['RU-KAM', /камчат/, 0], ['RU-MAG', /магаданск/, 1], ['RU-CHU', /чукот/, 0], ['RU-SA', /якути/, 0],
];
const MARK = /(^|\s)г\.\s*[а-я]|област|обл\.|(^|[^а-яё])обл([^а-яё]|$)|кра[йяюе]([^а-яё]|$)|республик|округ|(^|[^а-яё])ао([^а-яё]|$)/;
const DIRN = /(^|[^а-яё])(от|из|через|над)\s|направлен|сторон|курсом|→|->|далее/;
const RX_CLEAR = /отбой/;
const RX_MISSILE = /ракетн\S*\s+опасност|опасност\S*\s+(по\s+)?(ракет|крылат)/;
const RX_UAV = /опасност\S*\s+(атак\S*\s+|по\s+)?(бпла|беспилот|дрон)|беспилотн\S*\s+опасност|угроз\S*\s+(атак\S*\s+)?(бпла|беспилот)|опасност\S*\s+по\s+бпла/;

function classify(text) {
  const t = text.toLowerCase().replace(/ё/g, 'е');
  if (RX_CLEAR.test(t)) {
    const m = /отбой\s+ракетн/.test(t), u = /отбой\s+(\S+\s+){0,2}(бпла|беспилот|дрон)|отбой\s+беспилотн/.test(t);
    return { clear: m && !u ? ['missile'] : u && !m ? ['uav'] : ['uav', 'missile'] };
  }
  const k = []; if (RX_UAV.test(t)) k.push('uav'); if (RX_MISSILE.test(t)) k.push('missile');
  return k.length ? { set: k } : null;
}
function regions(text) {
  const out = new Set();
  for (let seg of text.toLowerCase().replace(/ё/g, 'е').split(/[\n,;]+|[.!]\s+|\s[-–—]\s/)) {
    if (DIRN.test(seg)) continue;
    const marked = MARK.test(seg);
    for (const [iso, rx, needMark] of REG) if (rx.test(seg) && (!needMark || marked)) out.add(iso);
    if (/москва\s+и\s+(московская\s+)?област/.test(seg)) { out.add('RU-MOS'); out.add('RU-MOW'); }
  }
  if (out.has('RU-SA') && out.size > 1) out.delete('RU-SA');
  return [...out];
}
function unhtml(s) {
  return s.replace(/<br\s*\/?>/g, '\n').replace(/<[^>]+>/g, '').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
}
function parsePage(html) {
  const posts = [];
  for (const block of html.split('<div class="tgme_widget_message_wrap').slice(1)) {
    const id = (block.match(/data-post="[^"\/]+\/(\d+)"/) || [])[1], ts = (block.match(/<time[^>]+datetime="([^"]+)"/) || [])[1];
    const tx = (block.match(/<div class="tgme_widget_message_text[^"]*"[^>]*>([\s\S]*?)<\/div>/) || [])[1];
    if (id && ts && tx) posts.push({ id: +id, ts: new Date(ts).getTime(), text: unhtml(tx) });
  }
  return posts;
}
// A busy night fills 12 h with 300-420 posts per channel (audit 19.10: up to 21 pages), and a 5-page cap dropped
// alerts declared earlier that night. Pages are fetched in parallel batches: post ids run consecutively, so
// before=newest-20k lands on page k (overlaps are deduplicated, a deleted post only shifts a page, never leaves a gap).
async function page(ch, before) {
  const r = await fetch(`https://t.me/s/${ch}` + (before ? `?before=${before}` : ''), { headers: { 'User-Agent': UA } });
  if (!r.ok) throw new Error(`${ch} ${r.status}`);
  return parsePage(await r.text());
}
async function channel(ch, since) {
  const first = await page(ch); if (!first.length) return [];
  const seen = new Map(first.map(x => [x.id, { ...x, ch }])); let lo = Math.min(...first.map(x => x.id)), done = Math.min(...first.map(x => x.ts)) < since;
  for (let k = 1; !done && k < MAX_PAGES; k += BATCH) {
    const befores = []; for (let j = 0; j < BATCH && k + j < MAX_PAGES; j++) befores.push(lo - 20 * j);
    const got = await Promise.all(befores.map(b => page(ch, b)));
    for (const g of got) for (const x of g) seen.set(x.id, { ...x, ch });
    const all = got.flat(); if (!all.length) break;
    lo = Math.min(...all.map(x => x.id)); done = Math.min(...all.map(x => x.ts)) < since;
  }
  return [...seen.values()];
}
// fold posts (oldest first) into region states; also a 10-minute series of how many regions were under alert
function fold(posts, now) {
  const st = {}, series = [], clears = {}; posts.sort((a, b) => a.ts - b.ts);
  const BIN = 600e3, t0 = now - WINDOW_H * 3600e3; let bin = Math.floor(t0 / BIN) * BIN, i = 0;
  const count = t => Object.values(st).filter(s => (s.uav || s.missile) && t - s.upd < STALE_H * 3600e3).length;
  // a post can carry several announcements in blank-line separated paragraphs ("Тульская - отбой ракетной опасности" /
  // "Курская, Орловская - ракетная опасность сохраняется"): read them apart when each one names a region and a status
  const parts = p => { const ch = p.text.split(/\n\s*\n/).filter(x => classify(x) && regions(x).length);
                       return ch.length > 1 ? ch.map(text => ({ ...p, text })) : [p]; };
  const apply = p => parts(p).forEach(apply1);
  const apply1 = p => {
    const c = classify(p.text); if (!c) return;
    // "Отбой ... На территории региона опасность сохраняется": an all-clear for some towns, the region stays under alert
    if (c.clear && /(территори\S*\s+(региона|области|края|республики)|в\s+регионе)\s+опасност\S*\s+сохраня/.test(p.text.toLowerCase())) return;
    let rs = regions(p.text);
    if (!rs.length && c.clear && /(всем|ранее)\s+(ранее\s+)?объявленн/.test(p.text.toLowerCase())) rs = Object.keys(st).filter(k => st[k].by.has(p.ch));
    if (!rs.length) return;
    for (const iso of rs) {
      const s = st[iso] || (st[iso] = { uav: null, missile: null, upd: 0, by: new Set() });
      if (c.set) { s.by.add(p.ch); for (const k of c.set) { if (!s[k]) s[k] = p.ts; } }
      if (c.clear) { let had = false; for (const k of c.clear) { if (s[k]) had = true; s[k] = null; } if (!s.uav && !s.missile) s.by.clear(); if (had) clears[iso] = p.ts; }
      else delete clears[iso];
      s.upd = p.ts;
    }
  };
  for (; bin <= now; bin += BIN) { while (i < posts.length && posts[i].ts < bin + BIN) apply(posts[i++]); if (bin >= t0) series.push(count(bin + BIN)); }
  while (i < posts.length) apply(posts[i++]);
  const active = {};
  for (const [iso, s] of Object.entries(st)) if (s.uav || s.missile) {
    const since = Math.min(...[s.uav, s.missile].filter(Boolean));
    active[iso] = { uav: !!s.uav, missile: !!s.missile, since: new Date(since).toISOString(), last: new Date(s.upd).toISOString(),
                    stale: now - s.upd > STALE_H * 3600e3 };
  }
  const cleared = {}; for (const [iso, ts] of Object.entries(clears)) if (!active[iso] && now - ts < 3 * 3600e3) cleared[iso] = new Date(ts).toISOString();
  return { active, cleared, series };
}
async function build(now = Date.now()) {
  const since = now - WINDOW_H * 3600e3, got = await Promise.allSettled(CHANNELS.map(c => channel(c, since)));
  const posts = [], ok = [], cover = [];
  got.forEach((g, j) => { if (g.status === 'fulfilled' && g.value.length) { ok.push(CHANNELS[j]); posts.push(...g.value); cover.push(Math.min(...g.value.map(p => p.ts))); } });
  if (!ok.length) throw new Error('no source answered');
  const f = fold(posts.filter(p => p.ts <= now), now);
  return { updated: new Date(now).toISOString(), window_hours: WINDOW_H, stale_hours: STALE_H, bin_minutes: 10,
           covered_from: new Date(Math.max(...cover)).toISOString(), sources: ok, ...f };
}
module.exports = async (req, res) => {
  try {
    const out = await build();
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=90, stale-while-revalidate=180');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.statusCode = 200; res.end(JSON.stringify(out));
  } catch (e) {
    res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.setHeader('Cache-Control', 'public, s-maxage=20');
    res.statusCode = 502; res.end(JSON.stringify({ error: String(e.message || e) }));
  }
};
module.exports.classify = classify; module.exports.regions = regions; module.exports.fold = fold; module.exports.build = build; module.exports.parsePage = parsePage;
