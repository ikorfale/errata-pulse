"""PREREG v1.4 item 11 (Fable review 23.10): fieldwork dates read from each weekly FOM 'Dominanty' PDF instead of
assumed as 'series date - 2'. Fetches issues d{n}no{year}.pdf politely (one at a time, 3 s apart), extracts the
'ФОМнибус» D1–D2 <month>' line (pdftotext -raw: the default layout drops or splits the digits in some issues), records the pdf sha256. Output: fieldwork.tsv (issue, start, end, sha256, raw).
Reads no FOM mood values."""
import hashlib, re, subprocess, sys, time, datetime as dt, urllib.request, os
MON = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
       'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
RX = re.compile(r'ФОМнибус»\s*(\d{1,2})(?:\s+([а-я]+))?\s*[–—-]\s*(\d{1,2})\s+([а-я]+)', re.S)
ISSUES = [(2025, n) for n in range(36, 53)] + [(2026, n) for n in range(1, 43)]
out = open('fieldwork.tsv', 'w'); out.write('issue\tfield_start\tfield_end\tpdf_sha256\traw\n')
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fom', 'weekly'); os.makedirs(CACHE, exist_ok=True)   # PDFs not committed
for y, n in ISSUES:
    url = f'https://media.fom.ru/fom-bd/d{n}no{y}.pdf'; p = os.path.join(CACHE, f'd{n}no{y}.pdf')
    if os.path.exists(p): pdf = open(p, 'rb').read()
    else:
      try: pdf = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'errata-research/1.0 (errata@agentmail.to)'}), timeout=30).read()
      except Exception as e: out.write(f'{y}-{n}\t\t\t\tfetch {type(e).__name__}\n'); out.flush(); time.sleep(3); continue
      time.sleep(3)
    if pdf[:4] != b'%PDF': out.write(f'{y}-{n}\t\t\t\tnot a pdf\n'); continue
    open(p, 'wb').write(pdf)
    txt = subprocess.run(['pdftotext', '-raw', p, '-'], capture_output=True, text=True).stdout
    m = RX.search(txt)
    if not m: out.write(f'{y}-{n}\t\t\t{hashlib.sha256(pdf).hexdigest()}\tno fieldwork line\n'); continue
    d1, m1, d2, m2 = m.groups(); m2n = MON.get(m2); m1n = MON.get(m1) if m1 else m2n
    if not m2n or not m1n: out.write(f'{y}-{n}\t\t\t{hashlib.sha256(pdf).hexdigest()}\tmonth? {m.group(0)!r}\n'); continue
    end = dt.date(y if not (n <= 2 and m2n == 12) else y - 1, m2n, int(d2))
    start = dt.date(end.year - (m1n > m2n), m1n, int(d1))
    out.write(f'{y}-{n}\t{start}\t{end}\t{hashlib.sha256(pdf).hexdigest()}\t{" ".join(m.group(0).split())}\n'); out.flush()
print(open('fieldwork.tsv').read())
