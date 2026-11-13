"""alerts_hours.py <dir of YYYY-MM.jsonl snapshots> > data/alerts_hours.json

Hours under an officially declared alert per region per day, from the site's own 5-minute snapshots of /api/alerts
(region level only: {"ts", "a": {ISO: "u"|"m"|"b" (+"*" if stale)}}). Days are Moscow days (UTC+3).
Counting rules, kept simple and stated on the pages:
- a snapshot credits the time until the next snapshot to every region it shows as declared, at most 10 minutes;
  a longer gap is missing data, not alert time (credited 5 minutes, the rest counted as a coverage gap);
- a region marked stale (no update for 4 hours, possibly ended without a relayed all-clear) earns no time;
- an "alert" is a start: the region listed (declared or stale) in a snapshot and not listed in the one before; a stale
  alert that gets a fresh update is the same alert. Hours are a lower bound (stale stretches earn nothing)."""
import json, os, sys, glob
from datetime import datetime, timedelta, timezone

MSK = timezone(timedelta(hours=3)); STEP = 300; CAP = 600

def rows(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
        for l in open(f):
            try:
                r = json.loads(l)
                out.append((datetime.strptime(r['ts'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc), r.get('a', {})))
            except (ValueError, KeyError):
                pass
    return sorted(out, key=lambda x: x[0])

def split(t0, t1):
    """Yield (moscow date, seconds) pieces of [t0, t1)."""
    while t0 < t1:
        m = t0.astimezone(MSK); nxt = (m + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        e = min(t1, nxt.astimezone(timezone.utc)); yield m.date().isoformat(), (e - t0).total_seconds(); t0 = e

def main(d):
    R = rows(d)
    if len(R) < 2: print(json.dumps({'regions': {}, 'days': []})); return
    secs, msecs, starts, cov, prev = {}, {}, {}, {}, None
    for (t0, a), (t1, _) in zip(R, R[1:]):
        gap = (t1 - t0).total_seconds(); credit = min(gap, CAP) if gap <= CAP else STEP
        live = {k for k, v in a.items() if not v.endswith('*')}
        mis = {k for k in live if a[k][0] in 'mb'}             # missile danger (alone or with UAV)
        for k in (set(a) - prev if prev is not None else ()):   # present at all now, absent before; the first snapshot starts nothing
            day = t0.astimezone(MSK).date().isoformat(); starts.setdefault(k, {})[day] = starts.get(k, {}).get(day, 0) + 1
        for day, s in split(t0, t0 + timedelta(seconds=credit)):
            cov[day] = cov.get(day, 0) + s
            for k in live: secs.setdefault(k, {})[day] = secs.get(k, {}).get(day, 0) + s
            for k in mis: msecs.setdefault(k, {})[day] = msecs.get(k, {}).get(day, 0) + s
        prev = set(a)
    days = sorted(cov)
    out = {'first': R[0][0].strftime('%Y-%m-%dT%H:%MZ'), 'last': R[-1][0].strftime('%Y-%m-%dT%H:%MZ'), 'days': days,
           # share of each Moscow day we have snapshots for (first and last days are partial by construction)
           'coverage': {k: round(v / 86400, 3) for k, v in cov.items()},
           # [hours under any declared alert, alerts started, of those hours: under missile danger]
           'regions': {k: {day: [round(secs.get(k, {}).get(day, 0) / 3600, 2), starts.get(k, {}).get(day, 0),
                                 round(msecs.get(k, {}).get(day, 0) / 3600, 2)] for day in days}
                       for k in sorted(set(secs) | set(starts))}}
    json.dump(out, sys.stdout, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    main(sys.argv[1])
