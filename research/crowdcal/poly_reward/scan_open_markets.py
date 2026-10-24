import gzip,json,time,urllib.request,collections
URL="https://gamma-api.polymarket.com/events/keyset?limit=100&active=true&closed=false"
seen=set(); rows=[]; cur=None
for p in range(1000):
    req=urllib.request.Request(URL+(f"&after_cursor={cur}" if cur else ""),headers={"User-Agent":"errata-crowdcal/1 (errata@agentmail.to)"})
    d=json.load(urllib.request.urlopen(req,timeout=60))
    for e in d.get("events") or []:
        for m in e.get("markets") or []:
            if m.get("closed") or m["id"] in seen: continue
            seen.add(m["id"])
            rows.append({"id":m["id"],"end":(m.get("endDate") or "")[:10],"vol":float(m.get("volumeNum") or m.get("volume") or 0),"flag":bool(m.get("holdingRewardsEnabled")),"q":(m.get("question") or "")[:80]})
    cur=d.get("next_cursor")
    if not cur or not d.get("events"): break
    time.sleep(0.5)
json.dump(rows,gzip.open("open_markets.json.gz","wt"))
print("scanned",len(rows))
