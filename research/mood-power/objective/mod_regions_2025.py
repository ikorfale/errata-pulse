"""#385: MoD-claimed UAVs destroyed over each Russian region, from the Russian MoD Telegram bulletins (mod_claims_2025.jsonl),
summed over a date window (default 2025-03-26..2025-10-21: 210 days ending on the LAST day of Chronicles wave 15 fieldwork, the same
window for every respondent, so early respondents get up to 25 days of post-interview exposure; see window_sensitivity.md).
A post counts if it says UAVs were destroyed/intercepted and lists '<number> – над территорией <region>'; numbers in digits
or Russian words. Weekly summaries ('за прошедшую неделю', 'в течение недели') are skipped. Interception location as
claimed by the MoD, not impact. Usage: mod_regions_2025.py [START END] -> mod_regions_2025.tsv; with BOUNDS=1 also bounds_min.tsv / bounds_max.tsv: per region the
min / max over interview dates 26.09..21.10 of exposure_window.exposure (183 days, interview day excluded); run it on 2025-03-27 2025-10-20."""
import json, re, sys, collections
START, END = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('2025-03-26', '2025-10-21')
W = {'один': 1, 'одного': 1, 'одна': 1, 'два': 2, 'двух': 2, 'три': 3, 'трех': 3, 'трёх': 3, 'четыре': 4, 'четырех': 4, 'четырёх': 4,
     'пять': 5, 'пяти': 5, 'шесть': 6, 'шести': 6, 'семь': 7, 'семи': 7, 'восемь': 8, 'восьми': 8, 'девять': 9, 'девяти': 9,
     'десять': 10, 'десяти': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
     'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19, 'двадцать': 20}
TV = {'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50}
TENS = re.compile(r'\b(двадцать|тридцать|сорок|пятьдесят)(?:\s+(один|одного|два|двух|три|трех|трёх|четыре|четырех|четырёх|пять|шесть|семь|восемь|девять))?\b', re.I)
NUM = r'(\d+|' + '|'.join(sorted(W, key=len, reverse=True)) + r')'
ITEM = re.compile(NUM + r'(?:\s+(?:БПЛА|БпЛА|беспилотн\w+(?:\s+\w+){0,3}))?\s*(?:[–—-]|перехвачен\w*|уничтожен\w*)\s*над\s+(территори(?:ей|ями)|акваторией)\s+((?:(?!\s+и\s)[^,.;\n(])+)', re.I)
SING = re.compile(r'(?:уничтожен|перехвачен)\s+(?:один\s+)?украинск\w+\s+беспилотн\w+\s+летательн\w+\s+аппарат(?:\s+самолетного\s+типа)?\s+над\s+(территорией|акваторией)\s+((?:(?!\s+и\s)[^,.;\n(])+)', re.I)
tot = collections.Counter(); posts = used = skipped_week = 0; days = collections.defaultdict(set); unparsed = []
for l in open('mod_claims_2025.jsonl'):
    x = json.loads(l); d = x['dt'][:10]
    if not (START <= d <= END): continue
    t = TENS.sub(lambda m: str(TV[m.group(1).lower()] + (W[m.group(2).lower()] if m.group(2) else 0)), x['text']); posts += 1
    if 'беспилот' not in t and 'БПЛА' not in t: continue
    if re.search(r'прошедш\w+ недел|в течение недели|за неделю', t, re.I): skipped_week += 1; continue
    items = ITEM.findall(t)
    if not items and not re.search(r'[▫▪•]', t):  # a headline total is never assigned to the first region of a list
        m = re.search(NUM + r'\s+украинск\w+\s+беспилотн[^.:]*?над\s+территорией\s+((?:(?!\s+и\s)[^,.;\n(])+)', t, re.I)
        if m: items = [(m.group(1), 'территорией', m.group(2))]
    if not items:
        m = SING.search(t)
        if m: items = [('1', m.group(1), m.group(2))]
    if not items:
        if 'над территори' in t: unparsed.append((d, t[:160].replace('\n', ' ')))
        continue
    used += 1
    for n, kind, reg in items:
        n = int(n) if n.isdigit() else W[n.lower()]
        reg = re.sub(r'\s+', ' ', reg.strip()).replace('Республики ', 'Республика ')
        w = reg.split(); reg = ' '.join(w[:2]) if w[0] in ('Республика', 'Московского', 'Черного', 'Азовского', 'Каспийского', 'Балтийского') else w[0]  # 'Курской' = 'Курской области'
        tot[reg] += n; days[reg].add(d)
print(f'window {START}..{END}: posts {posts}, bulletins with region items {used}, weekly summaries skipped {skipped_week}, region mentions unparsed {len(unparsed)}')
for d, t in unparsed[:8]: print('  UNPARSED', d, t)
import os
if os.environ.get('BOUNDS'):
    import datetime as _dt
    from exposure_window import exposure
    T = [_dt.date(2025, 9, 26) + _dt.timedelta(k) for k in range(26)]
    for tag, fn in (('min', min), ('max', max)):
        with open(f'bounds_{tag}.tsv', 'w') as f:
            f.write('region\tuavs\tdays\n')
            for r, n in tot.most_common(): f.write(f'{r}\t{n}\t{fn(exposure(days, r, t) for t in T)}\n')
with open('mod_regions_2025.tsv', 'w') as f:
    f.write('region\tuavs\tdays\n')
    for r, n in tot.most_common(): f.write(f'{r}\t{n}\t{len(days[r])}\n')
for r, n in tot.most_common(40): print(f'{n:6d} {len(days[r]):4d}d  {r}')
