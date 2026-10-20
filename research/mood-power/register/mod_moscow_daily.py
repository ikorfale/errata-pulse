"""PREREG-fom-strikes criterion (a): drones downed over the Moscow region per calendar day (Moscow time), summing every
MoD bulletin dated that day, Moscow-region line only ("над территорией Московского региона" / "Московской области").
Rules fixed 20.10 before any join with FOM: list totals over several regions ("над территориями ...") are not
attributed to Moscow; the daily SVO summary report is skipped (it restates the interval bulletins); a hand check of a
sample of parsed and unparsed Moscow mentions is due before the register is committed (#390).
usage: python3 mod_moscow_daily.py IN.jsonl [IN2.jsonl ...] > out.tsv  (date, moscow_total, bulletins, ids)"""
import sys, json, re, collections, datetime as dt
W = {'один': 1, 'одного': 1, 'одному': 1, 'двум': 2, 'трем': 3, 'трём': 3, 'два': 2, 'двух': 2, 'три': 3, 'трех': 3, 'трёх': 3, 'четыре': 4, 'четырех': 4, 'пять': 5,
     'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10, 'одиннадцать': 11, 'двенадцать': 12}
MOS = re.compile(r'Московск(?:ого\s+региона|ой\s+области|им\s+регионом)')
NUM = re.compile(r'(?<![\w.])(\d+|' + '|'.join(W) + r')(?![\w.])', re.I)
def moscow_count(text):
    """Segment = text between bullet marks / colons around each Moscow mention. Number after the dash in the same
    segment ("Московской области - 63") wins; else the first number in the segment ("63 - над ...", "по одному БпЛА
    над территориями ... Московского региона", "уничтожены два ... над Московским регионом"). Air-defence sentences only."""
    n = 0
    for m in MOS.finditer(text):
        a = max(text.rfind(c, 0, m.start()) for c in ('▫', '▪', '•', ':', '\n')) + 1
        b = min([x for x in (text.find(c, m.end()) for c in ('▫', '▪', '•', '\n', ';')) if x >= 0] + [len(text)])
        seg = text[a:b].replace('\ufe0f', '')
        pre = text[a:m.start()].replace('\ufe0f', '')
        if not re.search(r'БПЛА|беспилотн|БпЛА|ПВО|уничтож|сбит|над\s', seg + text[max(0, a - 300):a], re.I): continue
        if 'военного округа' in seg: continue
        if re.search(r'территориями|областей', seg) and not re.match(r'\s*по\s', seg): continue   # list total, not per region
        after = re.search(r'[–—-]\s*(\d+)', text[m.end():b])
        nums = NUM.findall(pre)   # the number nearest before the mention ('... и один БПЛА - над ... Московского')
        g = after.group(1) if after else (nums[-1] if nums else None)
        if g: n += int(g) if g.isdigit() else W[g.lower()]
    return n
rows = []
for f in sys.argv[1:]:
    rows += [json.loads(l) for l in open(f)]
day = collections.defaultdict(lambda: [0, []])
for r in rows:
    if not r.get('dt'): continue
    t = dt.datetime.fromisoformat(r['dt']) + dt.timedelta(hours=3)          # Moscow time (UTC+3, no DST)
    if 'о ходе проведения специальной военной операции' in r['text']: continue   # daily summary restates bulletins
    n = moscow_count(r['text'])
    if n:
        d = day[t.date().isoformat()]; d[0] += n; d[1].append(r['id'])
for k in sorted(day):
    print(f"{k}\t{day[k][0]}\t{len(day[k][1])}\t{','.join(map(str, day[k][1]))}")
