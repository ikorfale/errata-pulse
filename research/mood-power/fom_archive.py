"""Power check step 1 (plan #349): FOM weekly 'calm vs anxious' back to 2021, merged from a few yearly charts.
Each PDF holds ~a year of weekly points, so 8 fetches cover 2021-2026. Parse: fom_geom.py (geometry + printed labels).
Output: fom/archive.json (date -> calm, anxious, dk; first PDF wins on a date, conflicts listed)."""
import json, sys, time
import urllib.request
from fom_geom import parse
PDFS = [(2022, 10), (2022, 40), (2023, 10), (2023, 40), (2024, 10), (2024, 40), (2025, 10), (2025, 40), (2026, 41)]
merged, conflicts, log = {}, [], []
for y, w in PDFS:
    url = f'https://media.fom.ru/fom-bd/d{w}no{y}.pdf'
    try: pdf = urllib.request.urlopen(url, timeout=30).read()
    except Exception: pdf = None
    time.sleep(2)
    if not pdf or pdf[:4] != b'%PDF': log.append(f"{y}w{w}: missing"); continue
    open(f'fom/d{w}no{y}.pdf', 'wb').write(pdf)
    try: rows, rep = parse(f'fom/d{w}no{y}.pdf')
    except Exception as e: log.append(f"{y}w{w}: parse failed: {e!r}"); continue
    log.append(f"{y}w{w}: {len(rows)} weeks {rows[0]['date']}..{rows[-1]['date']}, label problems {len(rep['label_mismatch'])} {rep['label_mismatch'][:2]}")
    for r in rows:
        o = merged.get(r['date'])
        if o and (o['calm'], o['anxious']) != (r['calm'], r['anxious']): conflicts.append((r['date'], o, r))
        merged.setdefault(r['date'], r)
series = [merged[d] for d in sorted(merged)]
json.dump({'pdfs': log, 'conflicts': conflicts, 'series': series}, open('fom/archive.json', 'w'), ensure_ascii=False, indent=0)
print('\n'.join(log)); print(f"{len(series)} weeks {series[0]['date']}..{series[-1]['date']}, conflicts {len(conflicts)}")
for c in conflicts[:5]: print('  conflict', c)
