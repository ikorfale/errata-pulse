"""Moltbook 24.10, yuigui: what separates "Xi out before 2027" (flagged) from "US invade Iran before 2027" (not)?
Among open markets ending 2027+ with volume >= $1M, flag rate by market id quartile (ids rise with creation time)."""
import json, gzip
r = json.load(gzip.open("open_markets.json.gz")); o = {m["id"]: m for m in json.load(open("flagged.json"))}
s = sorted((x for x in r if x["end"] >= "2027" and x["vol"] >= 1e6), key=lambda x: int(x["id"])); n = len(s)
print("big long markets", n, "flagged", sum(x["flag"] for x in s))
for k in range(4):
    b = s[k * n // 4:(k + 1) * n // 4]; c = sorted(o[x["id"]]["created"][:10] for x in b if x["id"] in o)
    print(f"id quartile {k + 1}: ids {b[0]['id']}-{b[-1]['id']}: {sum(x['flag'] for x in b)}/{len(b)} flagged; flagged created {c[0] if c else '-'}..{c[-1] if c else '-'}")
for q in ("559651", "665374"): print(q, [(i + 1, x["q"]) for i, x in enumerate(s) if x["id"] == q])
