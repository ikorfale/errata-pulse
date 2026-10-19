"""Sample Exilenova+ (Ukrainian strike-monitoring channel; reports strikes from videos and geolocation) from its public
web preview t.me/s/exilenova_plus: days 8-14 of every month Nov 2025 - Oct 2026, for comparison with alert depth.
Polite: one request per 2 s, identified user agent. Output: exilenova/$OUT (default posts.jsonl) {"id","time","text"}; env FROM=YYYY-MM to start later, GAP=seconds."""
import re, os, json, time, html, urllib.request, datetime as dt
GAP = float(os.environ.get('GAP', 2)); OUT = os.environ.get('OUT', 'posts.jsonl'); FROM = os.environ.get('FROM', '2025-11')
UA = {'User-Agent': 'errata-research (AI agent; errata@agentmail.to)'}
def page(before=None):
    url = 'https://t.me/s/exilenova_plus' + (f'?before={before}' if before else '')
    time.sleep(GAP)
    h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf8', 'replace')
    out = []
    for blk in h.split('class="tgme_widget_message_wrap')[1:]:
        i = re.search(r'data-post="exilenova_plus/(\d+)"', blk); t = re.search(r'datetime="([^"]+)"', blk)
        x = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', blk, re.S)
        if i and t:
            txt = html.unescape(re.sub(r'<[^>]+>', ' ', x.group(1))) if x else ''
            out.append({'id': int(i.group(1)), 'time': t.group(1), 'text': re.sub(r'\s+', ' ', txt).strip()})
    return out
def first_time(before):
    p = page(before); return (dt.datetime.fromisoformat(p[0]['time']), p) if p else (None, p)
def find(target, lo, hi):   # smallest 'before' whose page starts at/after target, by bisection on id
    while hi - lo > 15:
        mid = (lo + hi) // 2; t, _ = first_time(mid)
        if t is None or t < target: lo = mid
        else: hi = mid
    return lo
top = page()[-1]['id']; seen = set(); f = open('exilenova/' + OUT, 'w')
months = [(2025, 11), (2025, 12)] + [(2026, m) for m in range(1, 11)]
for y, m in [ym for ym in months if f'{ym[0]}-{ym[1]:02d}' >= FROM]:
    a = dt.datetime(y, m, 8, tzinfo=dt.timezone.utc); b = a + dt.timedelta(days=7)
    cur = find(a, 1, top + 1); n = 0
    while True:   # walk forward: page(before=cur+20) gives posts below cur+20
        p = page(cur + 20)
        if not p: break
        for r in p:
            t = dt.datetime.fromisoformat(r['time'])
            if a <= t < b and r['id'] not in seen: seen.add(r['id']); f.write(json.dumps(r, ensure_ascii=False) + '\n'); n += 1
        if dt.datetime.fromisoformat(p[-1]['time']) >= b or p[-1]['id'] >= top: break
        cur = max(p[-1]['id'], cur + 20)   # a run of >20 deleted ids would otherwise loop in place
    f.flush(); print(y, m, n, flush=True)
