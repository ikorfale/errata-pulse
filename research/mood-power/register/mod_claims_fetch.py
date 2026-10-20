"""Fetch Russian MoD channel posts (public web preview t.me/s/mod_russia) between two post ids, oldest-first
output, raw text + datetime only, one request per 3 s. For plan #385 (objective drone exposure per region,
Apr-Oct 2025, to join with Chronicles wave 15). Parsing happens separately (mod_claims_parse.py).
Usage: python3 mood/mod_claims_fetch.py LOW_ID HIGH_ID OUT.jsonl  (env TG_CHANNEL, default mod_russia; #390 uses
mos_sobyanin as the PREREG fallback for Moscow after the MoD dropped its regional breakdown in March 2026)"""
import sys, os, re, json, time, html, urllib.request
CH = os.environ.get('TG_CHANNEL', 'mod_russia')
LOW, HIGH, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
UA = 'errata-research (AI agent; errata@agentmail.to; errata.page)'
MSG = re.compile(rf'data-post="{CH}/(\d+)".*?(?=data-post="{CH}/|\Z)', re.S)
seen = {}
before = HIGH
while before > LOW:
    for attempt in range(4):
        try:
            req = urllib.request.Request(f'https://t.me/s/{CH}?before={before}', headers={'User-Agent': UA})
            page = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace'); break
        except Exception as e:
            print('retry', before, e, flush=True); time.sleep(30 * (attempt + 1))
    else:
        print('giving up at', before, flush=True); break
    ids = []
    for m in MSG.finditer(page):
        pid = int(m.group(1)); block = m.group(0)
        dt = re.search(r'datetime="([^"]+)"', block)
        tx = re.search(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', block, re.S)
        text = html.unescape(re.sub(r'<br\s*/?>', '\n', tx.group(1))) if tx else ''
        text = re.sub(r'<[^>]+>', '', text)
        if LOW <= pid < HIGH and pid not in seen:
            seen[pid] = {'id': pid, 'dt': dt.group(1) if dt else None, 'text': text}
        ids.append(pid)
    if not ids: print('empty page at', before, flush=True); break
    nb = min(ids)
    if nb >= before: break
    before = nb
    if len(seen) % 200 < 20: print(before, len(seen), flush=True)
    time.sleep(3)
with open(OUT, 'w') as f:
    for pid in sorted(seen): f.write(json.dumps(seen[pid], ensure_ascii=False) + '\n')
print('done', len(seen), 'posts', min(seen, default=None), max(seen, default=None))
