"""PREREG-L2 sanity check: Fontanka snapshots 23.10 16:37Z and 24.10 17:10Z (posts as listed in reactions/)."""
import json, statistics as st
from datetime import datetime, timedelta
from collections import defaultdict
A={json.loads(l)['id']:json.loads(l) for l in open('reactions/fontankaspb-20261023T1637Z.jsonl')}
B={json.loads(l)['id']:json.loads(l) for l in open('reactions/fontankaspb-20261024T1710Z.jsonl')}
T1=datetime(2026,10,23,16,37)
DIS=set('😱😢🤯😨🙏💔'); ANG=set('🤬😡👎')
both=[i for i in B if i in A]
print('posts in 24.10 snapshot',len(B),'overlap',len(both))
old=[i for i in both if T1-datetime.fromisoformat(A[i]['time'])>=timedelta(hours=72)]
print('overlap posts aged >=72h at first snapshot',len(old))
# (1) reaction set: emojis present on a post in B but absent in A (new kind appearing) among old posts
newkinds=sum(1 for i in old if set(B[i]['reactions'])-set(A[i]['reactions']))
lost=sum(1 for i in old if set(A[i]['reactions'])-set(B[i]['reactions']))
print(f'(1) old posts gaining a new reaction kind {newkinds}/{len(old)}, losing one {lost}/{len(old)}')
# (2) growth of total reactions on old posts
ga=sum(sum(A[i]['reactions'].values()) for i in old); gb=sum(sum(B[i]['reactions'].values()) for i in old)
per=[(sum(B[i]['reactions'].values())-sum(A[i]['reactions'].values()))/max(1,sum(A[i]['reactions'].values())) for i in old]
print(f'(2) total reactions on old posts {ga} -> {gb}, growth {100*(gb-ga)/ga:.2f}%; per-post median {100*st.median(per):.2f}%, max {100*max(per):.1f}%, posts >5%: {sum(p>0.05 for p in per)}')
young=[i for i in both if i not in old]
if young:
  ya=sum(sum(A[i]['reactions'].values()) for i in young); yb=sum(sum(B[i]['reactions'].values()) for i in young)
  print(f'    contrast: {len(young)} posts younger than 72h grew {100*(yb-ya)/max(1,ya):.1f}%')
# (3) day-to-day SD of daily mean distress share, from the 23.10 snapshot, posts >=72h old
day=defaultdict(list)
for i,p in A.items():
  t=datetime.fromisoformat(p['time'])
  if T1-t<timedelta(hours=72): continue
  tot=sum(v for k,v in p['reactions'].items() if k!='🤡')
  if tot==0: continue
  day[t.date()].append(sum(v for k,v in p['reactions'].items() if k in DIS)/tot)
days=sorted(day)
print('days with posts',len(days),days[0],'..',days[-1])
dm={d:st.mean(day[d]) for d in days}
import sys
qs=sys.argv[1] if len(sys.argv)>1 else '2026-09-20'
q0=datetime.fromisoformat(qs).date(); q=[d for d in days if q0<=d<q0+timedelta(days=14)]
v=[dm[d] for d in q]
print(f'(3) quiet fortnight {q[0]}..{q[-1]}: daily mean distress share mean {st.mean(v):.4f}, SD {st.stdev(v):.4f}, posts/day median {st.median(len(day[d]) for d in q)}; meaningful effect (2xSD) = {2*st.stdev(v):.4f}')
allv=[dm[d] for d in days]; print(f'    whole range SD {st.stdev(allv):.4f} over {len(allv)} days')
