"""Weekly Telegram posting and MAX links of verified governor channels, 30 Mar 2026 to now.
v2 after Fable's review 25.10: walk back to the date (hard cap 1200 pages; v1's 80 pages reached April for 3 of 10
channels), store the matched max.ru URLs per post (footer vs cross-post vs invite are classified in report.py),
anchored regex (no remax.ru), and log per channel how the walk ended and the collection date.
Pages back through the public preview t.me/s/<handle>?before=<id>, one request per 3 s.
Writes posts.jsonl {handle, region, role, id, t (UTC), max_urls, max_link, views} and walks.jsonl (one line per channel)."""
import re, json, time, urllib.request, sys
SINCE = '2026-03-30'
MAXRE = re.compile(r'(?<![\w.-])(?:https?://)?(?:www\.)?max\.ru/[^\s"<>\']*', re.I)
UA = {'User-Agent': 'errata-research (AI agent; errata.page)'}
chans = [l.rstrip('\n').split('\t') for l in open('../regions/verified.tsv')][1:]
chans = [(c[0], c[1], c[2]) for c in chans if c[3] == 'yes']
# deep re-walk of busy channels whose 80 pages stopped after SINCE: python3 collect.py --deep h1,h2 [pages]
# writes posts_deep.jsonl; report.py takes a handle's rows from there when present
PAGES, OUT = 1200, 'posts.jsonl'
if len(sys.argv) > 2 and sys.argv[1] == '--deep':
    only = set(sys.argv[2].split(',')); PAGES = int(sys.argv[3]) if len(sys.argv) > 3 else 250; OUT = 'posts_deep.jsonl'
    chans = [c for c in chans if c[2] in only]
done = set()
try:
    done = {json.loads(l)['handle'] for l in open(OUT)}
except FileNotFoundError: pass
out = open(OUT, 'a')
def views(v):
    v = v.strip(); m = {'K': 1e3, 'M': 1e6}.get(v[-1:], 1)
    return int(float(v.rstrip('KM')) * m) if v else None
for region, role, h in chans:
    if h in done: continue
    before, pages, rows, end = None, 0, [], 'cap'
    while pages < PAGES:
        url = f'https://t.me/s/{h}' + (f'?before={before}' if before else '')
        try: page = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read().decode('utf-8', 'replace')
        except Exception as e: print(h, 'error', e, file=sys.stderr); end = f'error {e}'[:80]; break
        pages += 1; time.sleep(3)
        blocks = re.split(r'<div class="tgme_widget_message_wrap', page)[1:]
        got = []
        for b in blocks:
            pid = re.search(rf'data-post="{re.escape(h)}/(\d+)"', b, re.I)
            t = re.search(r'<time datetime="([^"]+)"', b)
            if not pid or not t: continue
            v = re.search(r'<span class="tgme_widget_message_views">([^<]*)</span>', b)
            got.append({'handle': h, 'region': region, 'role': role, 'id': int(pid.group(1)), 't': t.group(1)[:19],
                        'max_urls': sorted(set(MAXRE.findall(b))), 'max_link': bool(MAXRE.search(b)), 'views': views(v.group(1)) if v else None})
        if not got: end = 'empty page'; break
        rows += got
        oldest = min(got, key=lambda r: r['id'])
        if oldest['t'] < SINCE: end = 'reached date'; break
        if oldest['id'] <= 1: end = 'channel start'; break
        before = oldest['id']
    seen = set()
    for r in sorted(rows, key=lambda r: r['id']):
        if r['id'] in seen: continue
        seen.add(r['id']); out.write(json.dumps(r, ensure_ascii=False) + '\n')
    out.flush()
    open('walks.jsonl', 'a').write(json.dumps({'handle': h, 'pages': pages, 'posts': len(seen), 'end': end,
        'oldest': min((r['t'] for r in rows), default=None), 'collected': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}) + '\n')
    print(h, pages, 'pages', len(seen), 'posts', min((r['t'] for r in rows), default='-'), file=sys.stderr, flush=True)
