"""MAX-side check (27.10): Telegram posts per channel in 22 Sep-21 Oct 2026 (Moscow time, inclusive), to set against
LiveDune's public '1 month' MAX post counts (snapshot table ends 21 Oct). Also each channel's most-linked max.ru profile."""
import json, collections, datetime as dt
rows=[l.rstrip('\n').split('\t') for l in open('verified.tsv')][1:]
KEEP={r[2]:r[0] for r in rows if r[3]=='yes'}
P=[p for p in map(json.loads,open('posts.jsonl')) if p['handle'] in KEEP]
D=[p for p in map(json.loads,open('posts_deep.jsonl')) if p['handle'] in KEEP]; dh={p['handle'] for p in D}
P=[p for p in P if p['handle'] not in dh]+D
a,b=dt.date(2026,9,22),dt.date(2026,10,21)
n=collections.Counter(); prof=collections.defaultdict(collections.Counter)
for p in P:
    d=(dt.datetime.fromisoformat(p['t'][:19])+dt.timedelta(hours=3)).date()
    if a<=d<=b: n[p['handle']]+=1
    for u in p['max_urls']:
        s=u.split('?')[0].replace('https://','').replace('http://','').rstrip('/').split('/')
        if len(s)==2 and s[1] not in ('join','u'): prof[p['handle']][s[1]]+=1
for h,r in sorted(KEEP.items(),key=lambda x:x[1]):
    print(f"{h}\t{r}\t{n[h]}\t{(prof[h].most_common(1) or [('-',0)])[0][0]}")
