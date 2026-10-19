// fetch.js CH HOURS -> posts_CH.json : public web preview of a Telegram channel, back HOURS from now, 1 req/s
const A = require('../../api/alerts.js'); const fs = require('fs');
const UA = 'errata-alerts-audit/1.0 (AI agent; errata@agentmail.to)';
(async () => {
  const ch = process.argv[2], since = Date.now() - (+process.argv[3]) * 3600e3; let url = `https://t.me/s/${ch}`, all = [], n = 0;
  while (n++ < 200) {
    const r = await fetch(url, { headers: { 'User-Agent': UA } }); if (!r.ok) { console.error(ch, r.status); break; }
    const p = A.parsePage(await r.text()); if (!p.length) break;
    all = all.concat(p.map(x => ({ ...x, ch }))); const oldest = Math.min(...p.map(x => x.id));
    if (Math.min(...p.map(x => x.ts)) < since) break;
    url = `https://t.me/s/${ch}?before=${oldest}`; await new Promise(r => setTimeout(r, 1000));
  }
  const seen = new Set(); all = all.filter(p => !seen.has(p.id) && seen.add(p.id) && p.ts >= since);
  fs.writeFileSync(`posts_${ch}.json`, JSON.stringify(all)); console.log(ch, n, 'pages', all.length, 'posts', all.length ? new Date(Math.min(...all.map(p=>p.ts))).toISOString() : '');
})();
