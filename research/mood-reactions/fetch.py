#!/usr/bin/env python3
"""Page back through a public channel's t.me/s preview and save per-post views and emoji reaction counts.
Usage: fetch.py CHANNEL SINCE_YYYY-MM-DD   -> data/CHANNEL.jsonl (one post per line). Polite: 3 s between pages."""
import re, sys, json, time, html, urllib.request, os

def num(s):
    s = s.strip().upper()
    m = {'K': 1e3, 'M': 1e6}
    return int(float(s[:-1]) * m[s[-1]]) if s and s[-1] in m else int(float(s or 0))

def parse(h):
    out = []
    for b in h.split('class="tgme_widget_message_wrap')[1:]:
        p = re.search(r'data-post="[^/"]+/(\d+)"', b)
        t = re.search(r'datetime="([^"]+)"', b)
        if not p or not t:
            continue
        v = re.search(r'tgme_widget_message_views">([^<]+)', b)
        reacts = {}
        for em, n in re.findall(r'class="tgme_reaction"><i class="emoji"[^>]*><b>([^<]+)</b></i>([\d.KM]+)', b):
            reacts[em] = reacts.get(em, 0) + num(n)
        paid = re.findall(r'class="tgme_reaction[^"]*paid[^"]*">.*?([\d.KM]+)</span>', b)
        tx = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', b, re.S)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', tx.group(1))).strip() if tx else ''
        out.append({'id': int(p.group(1)), 'time': t.group(1), 'views': num(v.group(1)) if v else None,
                    'reacts': reacts, 'text': text[:600]})
    nxt = re.search(r'<link rel="prev" href="[^"]*before=(\d+)"', h)
    return out, (nxt.group(1) if nxt else None)

def main(ch, since):
    os.makedirs('data', exist_ok=True)
    seen, rows, before = set(), [], None
    for page in range(200):
        url = f'https://t.me/s/{ch}' + (f'?before={before}' if before else '')
        req = urllib.request.Request(url, headers={'User-Agent': 'errata-research/1.0 (AI agent; errata@agentmail.to)'})
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
        posts, before = parse(h)
        for p in posts:
            if p['id'] not in seen:
                seen.add(p['id']); rows.append(p)
        oldest = min((p['time'] for p in posts), default='')
        if not before or oldest[:10] < since:
            break
        time.sleep(3)
    rows.sort(key=lambda p: p['id'])
    with open(f'data/{ch}.jsonl', 'w') as f:
        for p in rows:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
    print(ch, len(rows), 'posts', rows[0]['time'][:16] if rows else '', '->', rows[-1]['time'][:16] if rows else '', 'pages', page + 1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
