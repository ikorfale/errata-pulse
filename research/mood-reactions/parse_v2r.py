"""#536 parser for the v2 re-fetch: like fetch.parse, but keeps every reaction the t.me/s preview shows.
fetch.parse (used for data_v2/) matched only plain emoji (<i class="emoji"><b>X</b>), so custom emoji
(<tg-emoji emoji-id=N>) and paid star reactions were silently missing from the denominator; PREREG-v2 counts them
("every other reaction, custom emoji included, is non-fear"). Found 27.10 21:20Z before any reaction value was read.
Keys: plain emoji as the character, custom emoji as 'custom:<id>', paid stars as 'paid'. Text is kept in full."""
import re, html
from fetch import num

R = re.compile(r'<span class="tgme_reaction( tgme_reaction_paid)?">(?:<i class="emoji"[^>]*><b>([^<]+)</b></i>'
               r'|<tg-emoji emoji-id="(\d+)">\s*</tg-emoji>|<i class="icon icon-telegram-stars"></i>)([\d.KM]+)</span>')
ANY = re.compile(r'class="tgme_reaction[ "]')

def parse(h):
    out = []
    for b in h.split('class="tgme_widget_message_wrap')[1:]:
        p = re.search(r'data-post="[^/"]+/(\d+)"', b)
        t = re.search(r'datetime="([^"]+)"', b)
        if not p or not t:
            continue
        v = re.search(r'tgme_widget_message_views">([^<]+)', b)
        reacts = {}
        hits = R.findall(b)
        for paid, em, cid, n in hits:
            k = 'paid' if paid else em if em else f'custom:{cid}'
            reacts[k] = reacts.get(k, 0) + num(n)
        unparsed = len(ANY.findall(b)) - len(hits)
        tx = re.search(r'class="tgme_widget_message_text js-message_text[^"]*"[^>]*>(.*?)</div>', b, re.S)
        # not the first ..._text div: on a reply that is the quoted post (js-message_reply_text); Fable review 1, 27.10
        text = html.unescape(re.sub(r'<[^>]+>', ' ', tx.group(1))).strip() if tx else ''
        out.append({'id': int(p.group(1)), 'time': t.group(1), 'views': num(v.group(1)) if v else None,
                    'reacts': reacts, 'unparsed_reactions': unparsed, 'text': text})
    nxt = re.search(r'<link rel="prev" href="[^"]*before=(\d+)"', h)
    return out, (nxt.group(1) if nxt else None)
