// replay.js: rebuild what /api/alerts would have shown every 5 min (same classify/regions/fold, same 12 h window,
// same 5-page cap per channel) from saved aggregator posts; writes replay.json {t: {iso: {uav, missile, stale}}}
const A = require('../../api/alerts.js'); const fs = require('fs');
const CH = ['radarrussiia', 'locatorru'], PAGE = 20, MAXP = +(process.env.MAXP || 5), WIN = 12 * 3600e3;
const P = Object.fromEntries(CH.map(c => [c, JSON.parse(fs.readFileSync(`posts_${c}.json`)).sort((a, b) => b.id - a.id)]));
const t0 = Date.parse(process.argv[2]), t1 = Date.parse(process.argv[3]), out = {};
for (let t = t0; t <= t1; t += 300e3) {
  const since = t - WIN, posts = [];
  for (const c of CH) {
    const avail = P[c].filter(p => p.ts <= t);
    for (let pg = 0; pg < MAXP; pg++) { const page = avail.slice(pg * PAGE, pg * PAGE + PAGE); if (!page.length) break;
      posts.push(...page); if (Math.min(...page.map(x => x.ts)) < since) break; }
  }
  const f = A.fold(posts.filter(p => p.ts >= since).map(p => ({ ...p })), t), s = {};
  for (const [iso, a] of Object.entries(f.active)) s[iso] = { uav: a.uav, missile: a.missile, stale: a.stale };
  out[new Date(t).toISOString()] = s;
}
fs.writeFileSync(process.env.OUT || 'replay.json', JSON.stringify(out)); console.log(Object.keys(out).length, 'steps');
