"""Helper for re-measure #182: for each ledger event published 2026-10-07..now, list alert hits that share a
source URL or many words with it. Output is a worksheet for hand labels, not the result."""
import json, re, datetime
P = "./"  # frozen copies of the event ledger and monitor hits sit next to this script
ev = [json.loads(l) for l in open(P + "events.jsonl")]
al = [json.loads(l) for l in open(P + "alerts.jsonl")]
T0 = datetime.datetime(2026, 10, 7, 21, 7, tzinfo=datetime.timezone.utc).timestamp()
def words(s): return {w for w in re.findall(r"[a-zа-я]{5,}", s.lower())}
H = []
for i, a in enumerate(al):
    if a.get("seen_at", 0) < T0: continue
    o = a["event"].get("output", {}); txt = o.get("content", "") if isinstance(o, dict) else str(o)
    urls = set(); 
    for b in (o.get("basis") or []) if isinstance(o, dict) else []:
        for c in b.get("citations", []): urls.add(c.get("url", "").split("?")[0]); txt += " " + c.get("title", "")
    H.append((i, a["monitor"], a["seen_at"], urls, words(txt), txt[:110]))
print("hits since T0:", len(H))
for e in ev:
    if str(e.get("date_published", "")) < "2026-10-07": continue
    eu = {s.split(" ")[0].split("?")[0] for s in e.get("sources", []) if isinstance(s, str)}
    ew = words(e.get("what", "") + " " + e.get("where", ""))
    best = sorted(((len(ew & h[4]) + 10 * len(eu & h[3]), h[0], h[1]) for h in H), reverse=True)[:2]
    print(f"{e['id'][:38]:<38} {str(e.get('date_published'))[:10]} fv={e.get('found_via','-')!s:<8} comp={e.get('component','')[:14]:<14} best={best}")
