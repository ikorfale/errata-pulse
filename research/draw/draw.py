"""Question draw, step 2 (plan #498). Anyone can run it: python3 draw.py candidates.json RANDOMNESS_HEX
RANDOMNESS_HEX = the 'randomness' field of drand quicknet round 33548212 (2026-10-31 12:00:00 UTC),
https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/public/33548212
Index j of draw i (i = 0, 1, ...) = int(sha256(randomness_hex + ':' + str(i)), 16) mod N; repeats are skipped
until K = 5 distinct indices. Prints the commitment hash of the list too, so a reader can check it against the
hash published before the round."""
import hashlib, json, sys
K = 5
d = json.load(open(sys.argv[1])); r = sys.argv[2].strip().lower()
canon = json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
print('list sha256', hashlib.sha256(canon).hexdigest())
c = d['candidates']; n = len(c); picks, i = [], 0
while len(picks) < K:
    j = int(hashlib.sha256(f'{r}:{i}'.encode()).hexdigest(), 16) % n; i += 1
    if j not in picks: picks.append(j)
for j in picks: print(j, c[j]['url'], '|', c[j]['question'])
