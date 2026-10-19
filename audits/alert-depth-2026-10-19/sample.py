"""Systematic sample of t.me/s/radarrussiia history: one web-preview page (20 consecutive posts) every STEP post ids,
from START to now. Gentle: one request per ~2.5 s. Output: events_sample.jsonl (parsed with tools/drone_radar.parse)."""
import importlib.util, json, time, os, sys
sp = importlib.util.spec_from_file_location('dr', 'drone_radar.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
OUT = 'events_sample.jsonl'
START, STOP, STEP = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
seen = set()
if os.path.exists(OUT):
    for l in open(OUT): seen.add(json.loads(l)['id'])
done_pages = 0
with open(OUT, 'a') as f:
    for b in range(START, STOP, STEP):
        if f'radarrussiia/{b-1}' in seen: continue
        for tries in range(3):
            try: posts = m.parse(m.get(f'https://t.me/s/radarrussiia?before={b}'), 'radarrussiia'); break
            except Exception as x: print('fail', b, x, flush=True); time.sleep(20)
        else: continue
        for p in posts:
            if p['id'] not in seen: seen.add(p['id']); p['page'] = b; f.write(json.dumps(p, ensure_ascii=False) + '\n')
        f.flush(); done_pages += 1
        if done_pages % 25 == 0: print(b, len(seen), posts[0]['ts'] if posts else None, flush=True)
        time.sleep(2.5)
print('done', done_pages, len(seen))
