"""PREREG-fom-strikes criterion (a) fallback: drones Sobyanin reports downed while "flying to Moscow", per calendar day
(Moscow time, UTC+3), summing every post of that day. Weekly/daily "в сторону Московского региона летело N" summaries
are NOT summed (they restate); they are written to a separate column for a cross-check.
usage: python3 sobyanin_daily.py sobyanin_2026.jsonl > sobyanin_daily.tsv   (date, city_total, posts, region_summary)"""
import sys, json, re, collections, datetime as dt
W = {'один': 1, 'одного': 1, 'два': 2, 'двух': 2, 'три': 3, 'трех': 3, 'трёх': 3, 'четыре': 4, 'четырех': 4, 'пять': 5,
     'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
     'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
     'девятнадцать': 19, 'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50,
     'четырёх': 4, 'пяти': 5, 'шести': 6, 'семи': 7, 'восьми': 8, 'девяти': 9, 'десяти': 10, 'одиннадцати': 11,
     'двенадцати': 12, 'тринадцати': 13, 'четырнадцати': 14, 'пятнадцати': 15, 'двадцати': 20, 'тридцати': 30}
TARGET = re.compile(r'летевш\w*\s+(?:на|в\s+сторону)\s+Москв', re.I)
SUMMARY = re.compile(r'в сторону Московского региона летел\w*\s+(\d+)', re.I)
DRONE = re.compile(r'БПЛА|беспилотник', re.I)
AGG = re.compile(r'в сторону Московского региона|за прошедшие сутки|со вчерашнего|на всех рубежах|в период|всего|за сутки|за ночь|с начала|сутки|последние|в общей сложности', re.I)
SHOT = re.compile(r'ПВО|уничтож|сбит|сбил|отраж|нейтрализ', re.I)
def count(text):
    """Drones in one downing report, read from its first sentence (number nearest before the drone noun; a singular
    noun alone = 1). Aggregates over a period (AGG) return None: they restate the single reports."""
    t = text.replace('\xa0', ' ')
    first = re.split(r'(?<=[.!])\s', t.strip(), 1)[0]
    if AGG.search(t) or not DRONE.search(first) or not SHOT.search(first): return None
    if re.search(r'Подмосков|област', first, re.I): return None
    m = DRONE.search(first)
    nums = re.findall(r'(?<![\w.])(\d+|' + '|'.join(W) + r')(?![\w.])', first[:m.start()], re.I)
    if not nums:
        after = re.match(r'\S*\s*\S*', first[m.end():])
        nums = re.findall(r'(?<![\w.])(\d+|' + '|'.join(W) + r')(?![\w.])', first[m.start():], re.I)[:1] if re.match(r'\w*,?\s+(?:уничтожен|сбит)\w*\s+(?:ещё\s+)?\d', first[m.start():]) else []
    if not nums:
        return 1 if re.match(r'(?:БПЛА|беспилотник(?:а|ом)?)\b', first[m.start():], re.I) and not re.match(r'беспилотник(?:ов|и)\b', first[m.start():], re.I) else 0
    g = nums[-1].lower()
    return int(g) if g.isdigit() else W[g]
if __name__ == '__main__':
    day, posts, summ, zero = collections.Counter(), collections.Counter(), {}, []
    for f in sys.argv[1:]:
        for l in open(f):
            x = json.loads(l)
            d = (dt.datetime.fromisoformat(x['dt']) + dt.timedelta(hours=3)).date().isoformat()
            s = SUMMARY.search(x['text'])
            if s and 'до 08:30' in x['text'] and 'октября до' not in x['text'][:0]:
                summ[d] = summ.get(d, '') + s.group(1) + ('w' if re.search(r'с 08:30 \d+ \w+ до 08:30', x['text']) and
                                                         'неделю' in x['text'] else '') + ','
            c = count(x['text'])
            if c is None: continue
            if c == 0: zero.append(x['id'])
            day[d] += c; posts[d] += 1
    print('date\tcity_total\tposts\tregion_summary')
    for d in sorted(set(day) | set(summ)): print(f'{d}\t{day[d]}\t{posts[d]}\t{summ.get(d, "")}')
    print('# zero-count matches (hand check):', zero[:40], len(zero), file=sys.stderr)
