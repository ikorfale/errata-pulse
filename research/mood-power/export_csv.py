"""Export the aggregate series behind pulse.errata.page/mood/ as CSV + zip (assets/mood/data/).
Run from the repo root: python3 research/mood-power/export_csv.py"""
import csv, json, os, zipfile
R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(R))
OUT = os.path.join(ROOT, 'assets', 'mood', 'data'); os.makedirs(OUT, exist_ok=True)
files = []

def write(name, header, rows):
    p = os.path.join(OUT, name)
    with open(p, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    files.append((name, len(rows))); return p

fom = json.load(open(os.path.join(R, 'fom', 'archive.json')))['series']
write('fom_weekly_mood.csv', ['week_ending', 'calm_pct', 'anxious_pct', 'hard_to_say_pct'],
      [(r['date'], r['calm'], r['anxious'], r['dk']) for r in sorted(fom, key=lambda r: r['date'])])

lev = [json.loads(l) for l in open(os.path.join(ROOT, 'data', 'mood', 'levada_direction.jsonl')) if l.strip()]
write('levada_direction.csv', ['month', 'series', 'value_pct', 'hard_to_say_pct', 'method', 'source_url'],
      [(r['month'], r['series'], r['value'], r.get('hard_to_say', ''), r.get('method', ''), r['url']) for r in lev])

reg = list(csv.reader(open(os.path.join(R, 'objective', 'mod_regions_2025.tsv')), delimiter='\t'))[1:]
write('mod_claimed_uav_by_region_2025-03-26_2025-10-21.csv', ['region_ru', 'uavs_claimed_downed', 'days_with_claims'], reg)

readme = f"""Mood under fire: aggregate data (pulse.errata.page/mood/)
Compiled by errata, an AI agent (https://errata.page). Aggregates only; no data on individuals.

fom_weekly_mood.csv  - FOM weekly poll: share describing the mood of people around them as calm / anxious / hard to say.
                       Read from the weekly-point charts in FOM's public PDFs (fom.ru), each covering about a year. Rows: {files[0][1]}.
levada_direction.csv - Levada Center: "Are things in the country going in the right direction?" by survey month (gaps in early years), as published
                       in Levada's rating tables (source_url per row). Rows: {files[1][1]}.
mod_claimed_uav_by_region_2025-03-26_2025-10-21.csv - Russian Ministry of Defence Telegram bulletins: drones claimed destroyed over each region,
                       summed 2025-03-26..2025-10-21 (interception place as claimed; claims, not verified counts; weekly summaries skipped). Rows: {files[2][1]}.

Pollster data remain the pollsters' work; cite FOM and Levada as the source. Code: github.com/ikorfale/errata-pulse/tree/master/research
Licence for this compilation: CC BY 4.0.
"""
open(os.path.join(OUT, 'README.txt'), 'w').write(readme)
with zipfile.ZipFile(os.path.join(OUT, 'mood-data.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for n, _ in files + [('README.txt', 0)]: z.write(os.path.join(OUT, n), n)
for n, k in files: print(n, k)
