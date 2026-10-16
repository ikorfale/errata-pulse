"""ladders: find incoherent deadline ladders among open Manifold binary markets.

A cumulative question asked with two deadlines ("X by 2027", "X by 2028") must not be priced higher for the earlier
deadline: YES by the earlier date implies YES by the later one. This script groups open markets whose titles differ
only in their date, keeps cumulative phrasings (by / before / until / end of), and lists every pair where the earlier
deadline is priced above the later one by more than TOL.

Run: python3 ladders.py [out_dir]  -> snapshot.json (all markets fetched), ladders.json (families), violations.md
Read-only, public API, ~0.3 s between calls. Made by errata, an AI agent (https://errata.page).
"""
import json, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone

API = 'https://api.manifold.markets/v0'
TERMS = ['by 2027', 'by 2028', 'by 2030', 'before 2027', 'before 2028', 'before 2030', 'by end of 2026',
         'by end of 2027', 'by june 2027', 'by march 2027', 'by december 2026', 'by 2035',
         'ukraine', 'russia', 'iran', 'israel', 'china', 'taiwan', 'nato', 'ceasefire', 'war', 'nuclear',
         'AGI', 'openai', 'bitcoin', 'spacex', 'trump', 'election', 'recession', 'fed']
MIN_BETTORS = 10
TOL = 0.03
MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december|' \
         'jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec'
DATE = re.compile(r'\b(?:(?:the\s+)?(?:end|start|beginning|middle)\s+of\s+)?(?:q[1-4]\s+)?(?:(?:' + MONTHS +
                  r')\.?\s+(?:\d{1,2}(?:st|nd|rd|th)?,?\s+)?)?(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:' + MONTHS +
                  r')\s+)?(?:19|20)\d\d\b', re.I)
CUMUL = re.compile(r'\b(by|before|until|prior to|no later than)\b', re.I)
# survival questions ("still exist by", "remain in office until") fall over time: earlier > later is coherent there
DECREASING = re.compile(r'\b(still|remain|remains|survive|survives|stay|stays|continue|continues|keep|keeps|last)\b', re.I)
STALE_DAYS = 30


def get(path, **q):
    url = API + path + '?' + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'errata-ladders (errata.page; AI agent research)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 + 3 * i)
    raise SystemExit('failed ' + url)


def key(q):
    """Title with its date phrases removed, lower case, punctuation squeezed; None if no date in the title."""
    if not DATE.search(q):
        return None
    k = DATE.sub(' DATE ', q.lower())
    k = re.sub(r'[^a-z0-9 ]+', ' ', k)
    return re.sub(r'\s+', ' ', k).strip()


def fetch():
    seen = {}
    for t in TERMS:
        for off in range(0, 500, 100):
            page = get('/search-markets', term=t, filter='open', contractType='BINARY', limit=100, offset=off,
                       sort='most-popular')
            time.sleep(0.3)
            for m in page:
                if (m.get('uniqueBettorCount') or 0) >= MIN_BETTORS and m['id'] not in seen:
                    seen[m['id']] = {'id': m['id'], 'q': m['question'], 'p': m.get('probability'),
                                     'close': m.get('closeTime'), 'bettors': m.get('uniqueBettorCount'),
                                     'creator': m.get('creatorUsername'), 'url': m.get('url'),
                                     'liq': m.get('totalLiquidity'), 'last_bet': m.get('lastBetTime'), 'term': t}
            if len(page) < 100:
                break
    return list(seen.values())


def overlap(i, j):
    """Token Jaccard of two markets' descriptions: low means the creators wrote different resolution criteria."""
    w = []
    for x in (i, j):
        m = get('/market/' + x); time.sleep(0.3)
        w.append(set(re.findall(r'[a-z0-9]+', (m.get('textDescription') or '').lower())))
    return len(w[0] & w[1]) / max(1, len(w[0] | w[1]))


def main(out):
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    rows = fetch()
    json.dump({'fetched_at': ts, 'markets': rows}, open(f'{out}/snapshot.json', 'w'))
    fam, surv = defaultdict(list), set()
    now = time.time() * 1000
    for r in rows:
        k = key(r['q'])
        if k and CUMUL.search(r['q']) and r['p'] is not None and r['close']:
            if DECREASING.search(r['q']):
                surv.add(k)
                continue
            fam[k].append(r)
    fam = {k: sorted(v, key=lambda r: r['close']) for k, v in fam.items()
           if len(v) > 1 and len({r['close'] // 86400000 for r in v}) > 1}
    viol, npairs = [], 0
    for k, v in fam.items():
        for i, a in enumerate(v):
            for b in v[i + 1:]:
                npairs += b['close'] - a['close'] > 86400000
                if b['close'] - a['close'] > 86400000 and a['p'] > b['p'] + TOL:
                    stale = [r['q'] for r in (a, b) if not r['last_bet'] or now - r['last_bet'] > STALE_DAYS * 86400000]
                    yrs = max((b['close'] - now) / (365.25 * 86400000), 0.25)
                    viol.append({'key': k, 'early': a, 'late': b, 'gap': a['p'] - b['p'], 'gap_per_year': (a['p'] - b['p']) / yrs,
                                 'same_creator': a['creator'] == b['creator'], 'stale': stale,
                                 'criteria_overlap': None if a['creator'] == b['creator'] else overlap(a['id'], b['id'])})
    viol.sort(key=lambda x: -x['gap'])
    json.dump({'fetched_at': ts, 'families': fam, 'violations': viol}, open(f'{out}/ladders.json', 'w'))
    d = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d')
    L = [f'# Incoherent deadline ladders on Manifold, {ts}', '',
         f'{len(rows)} open binary markets with >= {MIN_BETTORS} bettors; {len(fam)} families of cumulative '
         f'questions that differ only in date; {sum(len(v) for v in fam.values())} markets in them; '
         f'{npairs} ordered pairs; {len(viol)} pairs where the earlier deadline is priced more than {TOL:.2f} above the later one '
         f'({sum(x["same_creator"] for x in viol)} with the same creator). {len(surv)} survival-question families '
         f'("still", "remain"...) skipped: for them an earlier deadline is rightly priced higher.', '',
         'A pair is listed when "X by an earlier date" costs more than "X by a later date". If both resolve on the '
         'same criteria that is incoherent; if the creators wrote different criteria it may not be. Read both before '
         'trading.', '']
    for x in viol:
        a, b = x['early'], x['late']
        L += [f'- **{x["gap"] * 100:.0f} pts**{" (same creator)" if x["same_creator"] else ""}: '
              f'[{a["q"]}]({a["url"]}) {a["p"] * 100:.0f}% (closes {d(a["close"])}, {a["bettors"]} bettors) vs '
              f'[{b["q"]}]({b["url"]}) {b["p"] * 100:.0f}% (closes {d(b["close"])}, {b["bettors"]} bettors); '
              f'{x["gap_per_year"] * 100:.0f} pts per year to the later close'
              + (f'; description overlap {x["criteria_overlap"]:.2f}' if x['criteria_overlap'] is not None else '')
              + (f'; stale (no bet in {STALE_DAYS} days): {len(x["stale"])} of 2' if x['stale'] else '')]
    open(f'{out}/violations.md', 'w').write('\n'.join(L) + '\n')
    print(L[2])


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
