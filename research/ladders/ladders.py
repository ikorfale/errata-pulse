"""ladders: find incoherent deadline ladders among open Manifold binary markets.

A cumulative question asked with two deadlines ("X by 2027", "X by 2028") must not be priced higher for the earlier
deadline: YES by the earlier date implies YES by the later one. This script groups open markets whose titles differ
only in their date, keeps cumulative phrasings (by / before / until / end of), and lists every pair where the earlier
deadline is priced above the later one by more than TOL.

Run: python3 ladders.py [out_dir] [--search]  -> snapshot.json (all markets fetched), ladders.json, violations.md
--from snapshot.json: analyse a saved snapshot. Default: every open binary market (search-markets sort=newest paged by beforeTime); --search: the v0.2 term list.
Also every open multiple-choice "when" market with independent answers: "by"/"before" answers form a ladder too.
Read-only, public API, 0.3-0.4 s between calls. Made by errata, an AI agent (https://errata.page).
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


def walk(ctype):
    """Every open market of one contract type: search-markets sort=newest paged by beforeTime (offset stops at 1000)."""
    out, before = [], None
    while True:
        q = dict(term='', filter='open', contractType=ctype, limit=1000, sort='newest')
        if before:
            q['beforeTime'] = before
        page = get('/search-markets', **q)
        time.sleep(0.4)
        out += page
        if len(page) < 1000:
            return out
        before = page[-1]['createdTime']


def lite(m, t):
    return {'id': m['id'], 'q': m['question'], 'p': m.get('probability'), 'close': m.get('closeTime'),
            'bettors': m.get('uniqueBettorCount'), 'creator': m.get('creatorUsername'), 'url': m.get('url'),
            'liq': m.get('totalLiquidity'), 'last_bet': m.get('lastBetTime'), 'term': t}


def fetch_all():
    return [lite(m, '*') for m in walk('BINARY') if (m.get('uniqueBettorCount') or 0) >= MIN_BETTORS]


def fetch():
    seen = {}
    for t in TERMS:
        for off in range(0, 500, 100):
            page = get('/search-markets', term=t, filter='open', contractType='BINARY', limit=100, offset=off,
                       sort='most-popular')
            time.sleep(0.3)
            for m in page:
                if (m.get('uniqueBettorCount') or 0) >= MIN_BETTORS and m['id'] not in seen:
                    seen[m['id']] = lite(m, t)
            if len(page) < 100:
                break
    return list(seen.values())


MONTH_N = dict(zip(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], range(1, 13)))
ANS_DATE = re.compile(r'\b(by|before|until|prior to|no later than|end of|by the end of)\b\s*(?:the\s+)?(?:(?:end|middle)\s+of\s+|mid[- ])?'
                      r'(?:(q[1-4])\s+|(' + MONTHS + r')\.?\s+(?:\d{1,2}(?:st|nd|rd|th)?,?\s+)?)?((?:19|20)\d\d)\b', re.I)


def answer_deadline(text):
    """Deadline of a cumulative answer ("Before 2027", "By June 2028", "by end of Q3 2027") as a month index
    y*12+m of the last month it covers; None if the answer is not cumulative or has not exactly one year in it.
    Plain "2027" (= in 2027) is a bin, not a ladder rung."""
    hits = ANS_DATE.findall(text)
    if len(hits) != 1 or len(re.findall(r'\b(?:19|20)\d\d\b', text)) != 1:
        return None
    word, qtr, mon, yr = hits[0]
    y, before = int(yr), word.lower() == 'before'
    if qtr:
        m = int(qtr[1]) * 3 - (2 if before else 0)
    elif mon:
        m = MONTH_N[mon.lower()[:3]]
    else:
        m = 1 if before else 12
    return y * 12 + m - (1 if before else 0)  # 'before M' ends with the month before M, 'by M' with M


def fetch_mc():
    """Open multiple-choice 'when' markets with >= MIN_BETTORS: answers fetched one market at a time."""
    cand = [m for m in walk('MULTIPLE_CHOICE') if (m.get('uniqueBettorCount') or 0) >= MIN_BETTORS
            and re.search(r'\b(when|what year|by when|which year)\b', m['question'], re.I)]
    out = []
    for m in cand:
        d = get('/market/' + m['id']); time.sleep(0.3)
        out.append({'id': m['id'], 'q': m['question'], 'url': m.get('url'), 'bettors': m.get('uniqueBettorCount'),
                    'creator': m.get('creatorUsername'), 'sum_to_one': d.get('shouldAnswersSumToOne'),
                    'answers': [{'text': a.get('text'), 'p': a.get('probability'), 'resolved': a.get('resolution')}
                                for a in d.get('answers') or []]})
    return out


NEG = re.compile(r"\b(not|no|never|doesn't|does not|don't|won't|fails?|without)\b", re.I)


def answer_stem(text):
    """Answer text with its deadline removed: two answers are rungs of one ladder only if their stems are equal
    ("05 ships by end of 2028" and "30 ships by end of 2029" are different questions)."""
    t = re.sub(r'(?:19|20)\d\d(?:\s*/\s*\d{1,2})?', ' ', ANS_DATE.sub(' DATE ', text.lower()))
    t = re.sub(r'\b(' + MONTHS + r')\b|\bq[1-4]\b|\b\d{1,2}(st|nd|rd|th)?\b(?=\s*,|\s*$)', ' ', t)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', t)).strip()


def mc_violations(mcs):
    """In an independent-answers market (sum_to_one False), 'by an earlier date' must not cost more than 'by a later date'.
    Sum-to-one markets are date bins: their cumulative ladder is a running sum and cannot break order.
    Rungs are answers with the same stem (text minus the date); negated answers ("not before 2075") are skipped."""
    rungs, viol = 0, []
    for m in mcs:
        if m['sum_to_one'] is not False:
            continue
        lad = defaultdict(list)
        for a in m['answers']:
            if a['p'] is not None and not a['resolved'] and answer_deadline(a['text']) and not NEG.search(a['text']):
                lad[answer_stem(a['text'])].append((answer_deadline(a['text']), a))
        lad = {k: sorted(v, key=lambda t: t[0]) for k, v in lad.items() if len({d for d, _ in v}) > 1}
        if not lad:
            continue
        m['ladders'] = {k: len(v) for k, v in lad.items()}; rungs += 1
        for r in lad.values():
            for i, (da, a) in enumerate(r):
                for db, b in r[i + 1:]:
                    if db > da and a['p'] > b['p'] + TOL:
                        viol.append({'market': m, 'early': a, 'late': b, 'gap': a['p'] - b['p']})
    viol.sort(key=lambda x: -x['gap'])
    return rungs, viol


NEVER = re.compile(r"^\s*(never|no\b|not\b|.*\b(will not|won't|does not|doesn't|never)\b)", re.I)


def mc_complement(mcs):
    """'By the latest date' and 'never' cannot both be true: in an independent-answers market their prices must not
    sum above 1. Uses the longest ladder's latest rung and the one dateless negative answer ("Never announces...")."""
    out = []
    for m in mcs:
        if m['sum_to_one'] is not False:
            continue
        nev = [a for a in m['answers'] if a['p'] is not None and not a['resolved'] and NEVER.search(a['text'] or '')
               and not ANS_DATE.search(a['text'] or '')]  # 'Never announces a 2028 run' names a year but no deadline
        lad = defaultdict(list)
        for a in m['answers']:
            if a['p'] is not None and not a['resolved'] and answer_deadline(a['text']) and not NEG.search(a['text']):
                lad[answer_stem(a['text'])].append((answer_deadline(a['text']), a))
        if len(nev) != 1 or not lad:
            continue
        dl_last, last = max(max(lad.values(), key=len), key=lambda t: t[0])
        after = [int(y) for y in re.findall(r'\b(?:after|later than|beyond)\s+((?:19|20)\d\d)', nev[0]['text'], re.I)]
        if any(y * 12 + 12 < dl_last for y in after):  # 'after 2029 or never' overlaps 'by 2032'
            continue
        if last['p'] + nev[0]['p'] > 1 + TOL:
            out.append({'market': m, 'late': last, 'never': nev[0], 'excess': last['p'] + nev[0]['p'] - 1})
    out.sort(key=lambda x: -x['excess'])
    return out


def overlap(i, j):
    """Token Jaccard of two markets' descriptions: low means the creators wrote different resolution criteria."""
    w = []
    for x in (i, j):
        m = get('/market/' + x); time.sleep(0.3)
        w.append(set(re.findall(r'[a-z0-9]+', (m.get('textDescription') or '').lower())))
    return len(w[0] & w[1]) / max(1, len(w[0] | w[1]))


def main(out):
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    if '--from' in sys.argv:  # rerun the analysis on a saved snapshot, no fetching
        snap = json.load(open(sys.argv[sys.argv.index('--from') + 1]))
        ts, rows, mcs = snap['fetched_at'], snap['markets'], snap['multiple_choice']
    else:
        rows = fetch() if '--search' in sys.argv else fetch_all()
        mcs = fetch_mc()
    json.dump({'fetched_at': ts, 'coverage': 'search terms' if '--search' in sys.argv else 'all open',
               'markets': rows, 'multiple_choice': mcs}, open(f'{out}/snapshot.json', 'w'))
    mc_rungs, mc_viol = mc_violations(mcs)
    mc_comp = mc_complement(mcs)
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
    # order rungs by the deadline written in the title (a market can close years after its deadline: "by 2030"
    # closing 2041); fall back to the close time only when the title has no single cumulative date
    dl = lambda r: (answer_deadline(r['q']) or 0, r['close'])
    later = lambda a, b: (dl(b)[0] > dl(a)[0]) if dl(a)[0] and dl(b)[0] else b['close'] - a['close'] > 86400000
    for k, v in fam.items():
        v.sort(key=dl)
        for i, a in enumerate(v):
            for b in v[i + 1:]:
                npairs += later(a, b)
                if later(a, b) and a['p'] > b['p'] + TOL:
                    stale = [r['q'] for r in (a, b) if not r['last_bet'] or now - r['last_bet'] > STALE_DAYS * 86400000]
                    yrs = max((b['close'] - now) / (365.25 * 86400000), 0.25)
                    viol.append({'key': k, 'early': a, 'late': b, 'gap': a['p'] - b['p'], 'gap_per_year': (a['p'] - b['p']) / yrs,
                                 'same_creator': a['creator'] == b['creator'], 'stale': stale,
                                 'criteria_overlap': None if a['creator'] == b['creator'] else overlap(a['id'], b['id'])})
    viol.sort(key=lambda x: -x['gap'])
    json.dump({'fetched_at': ts, 'families': fam, 'violations': viol, 'mc_violations': mc_viol, 'mc_complement': mc_comp},
              open(f'{out}/ladders.json', 'w'))
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
    L += ['', '## Multiple-choice "when" markets', '',
          f'{len(mcs)} open multiple-choice "when" markets with >= {MIN_BETTORS} bettors; '
          f'{sum(m["sum_to_one"] is True for m in mcs)} are date bins (answers sum to one, so the ladder cannot break); '
          f'{mc_rungs} have independent answers with at least two cumulative deadlines ("by"/"before" a date); '
          f'{len(mc_viol)} answer pairs where the earlier deadline is priced more than {TOL:.2f} above the later one, '
          f'in {len({x["market"]["id"] for x in mc_viol})} markets.', '']
    for x in mc_viol:
        m, a, b = x['market'], x['early'], x['late']
        L += [f'- **{x["gap"] * 100:.0f} pts**: [{m["q"]}]({m["url"]}) ({m["bettors"]} bettors): '
              f'"{a["text"]}" {a["p"] * 100:.0f}% vs "{b["text"]}" {b["p"] * 100:.0f}%']
    L += ['', '## "By the last date" plus "never" above 100%', '',
          f'{len(mc_comp)} independent-answers markets where the latest "by" answer and the "never" answer together '
          f'cost more than {1 + TOL:.2f}: both cannot resolve YES.', '']
    for x in mc_comp:
        m = x['market']
        L += [f'- **+{x["excess"] * 100:.0f} pts**: [{m["q"]}]({m["url"]}) ({m["bettors"]} bettors): '
              f'"{x["late"]["text"]}" {x["late"]["p"] * 100:.0f}% + "{x["never"]["text"]}" {x["never"]["p"] * 100:.0f}%']
    open(f'{out}/violations.md', 'w').write('\n'.join(L) + '\n')
    print(L[2]); print(f'{len(mc_viol)} mc pairs, {len(mc_comp)} complement breaks')


if __name__ == '__main__':
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--from']
    main(args[0] if args else '.')
