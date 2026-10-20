"""Parse a FOM 'Настроение окружающих' chart by geometry (any year's layout): three coloured polylines
(orange = anxious, olive = calm, grey = hard to say; black and near-black paths are never series), y -> % by the
axis labels 0..80, x -> date by the rotated date labels. Each line's vertex is matched to a date by nearest x (not by
position in the path). The printed labels of a column are assigned to the three lines by page distance (best of the
6 permutations, label centre to vertex), then the label is the value; a label more than 2 pts from its line's
geometric value, a missing vertex, a non-Sunday date or a sum outside 98..102 is reported.
v2 20.10 after Fable's review (positional alignment, greedy value snapping, black paths). Usage: rows, report = parse(path)"""
import re, datetime, itertools, pymupdf, numpy as np
MONTHS = {m: i + 1 for i, m in enumerate("января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split())}
NAMES = ('calm', 'anxious', 'dk')

def classify(rgb):
    r, g, b = rgb
    if max(rgb) < 0.2: return None                       # black: gridlines, axes
    if r > 0.9 and g < 0.6: return 'anxious'
    if abs(r - g) < 0.05 and b < 0.1: return 'calm'
    if abs(r - g) < 0.05 and abs(g - b) < 0.05: return 'dk'
    return None

def parse(path):
    pg = pymupdf.open(path)[0]
    lines, bad = {}, []
    for d in pg.get_drawings():
        segs = [it for it in d['items'] if it[0] == 'l']
        if len(segs) < 20 or not d.get('color'): continue
        name = classify(d['color'])
        if not name: continue
        if name in lines: bad.append(f"second {name} path"); continue
        lines[name] = [(s[1].x, s[1].y) for s in segs] + [(segs[-1][2].x, segs[-1][2].y)]
    words = [(s['text'].strip(), s['bbox']) for b in pg.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
    xs = [x for pts in lines.values() for x, _ in pts]; x0, x1 = min(xs), max(xs)
    axis = [(int(t), (bb[1] + bb[3]) / 2) for t, bb in words if t in ('0', '20', '40', '60', '80') and bb[2] < x0 - 3]
    k, c = np.polyfit([y for _, y in axis], [v for v, _ in axis], 1)
    dates = []
    for t, bb in words:
        m = re.fullmatch(r"(\d{1,2}) (\w+) (20\d\d)", t)
        if m and m.group(2) in MONTHS:
            dates.append(((bb[0] + bb[2]) / 2, datetime.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))))
    labels = [(int(t), (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2) for t, bb in words
              if t.isdigit() and len(t) <= 2 and x0 - 8 < (bb[0] + bb[2]) / 2 < x1 + 8 and bb[1] > min(y for _, y in axis) - 30]
    rows = []
    for dx, date in sorted(dates):
        vert = {}
        for n in NAMES:
            px, py = min(lines[n], key=lambda p: abs(p[0] - dx))
            if abs(px - dx) > 4: bad.append(f"{date}: no {n} vertex"); break
            vert[n] = py
        else:
            col = [(v, ly) for v, lx, ly in labels if abs(lx - dx) < 6]
            geom = {n: k * vert[n] + c for n in NAMES}
            row = {'date': date.isoformat()}
            if len(col) >= 3:
                best = min(itertools.permutations(col, 3), key=lambda p: sum(abs(ly - vert[n]) for (v, ly), n in zip(p, NAMES)))
                for (v, ly), n in zip(best, NAMES):
                    row[n] = v
                    if abs(v - geom[n]) > 2: bad.append(f"{date} {n}: label {v} vs geom {geom[n]:.1f}")
            else:
                bad.append(f"{date}: {len(col)} labels"); row.update({n: round(geom[n]) for n in NAMES}); row['approx'] = True
            if date.weekday() != 6: row['not_sunday'] = True
            if not 98 <= row['calm'] + row['anxious'] + row['dk'] <= 102: bad.append(f"{date}: sum {row}")
            rows.append(row)
    return rows, {'n': len(rows), 'dates': len(dates), 'label_mismatch': bad, 'cal': (k, c)}
