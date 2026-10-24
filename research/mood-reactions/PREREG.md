# Reader reactions after a local strike: frozen design (2026-10-24, before any outcome was computed)

Question: in a city's main news Telegram channel, do reader emoji reactions shift after a confirmed drone strike on
that city, against the same channel's own previous 10 days?

Data: public t.me/s previews (fetch.py), final reaction counts fetched >= 72 h after day +1 for all three cases
(St Petersburg 18.10 Fontanka, Omsk 08.10 Om1_Omsk, Ryazan 15.10 ryazan_chp62).

Design (analyze.py, after a design review by a second model):
- unit = post with >= 30 reactions; buckets fear (scream, fearful, sad, crying), anger (angry, swearing),
  derision (clown, poop, grin, rofl, joy), support (heart, thumbs up, fire, salute), pray kept alone; plus
  reactions per 1000 views (audience influx warning).
- topic split by a fixed keyword regex (strike words); cells: strike-topic posts on days 0 and +1 vs strike-topic
  posts in the 10 days before (strikes elsewhere, alarms); non-strike posts days 0/+1 vs non-strike baseline
  (spillover; the cleanest mood claim).
- median difference with a 95% bootstrap over posts; no claim if a cell has < 10 outcome or < 20 baseline posts.
- the most I will claim from 3 cases: sign agreement per bucket and cell. No effect size, no "Russian mood".
- emoji present only before or only after are printed (a missing emoji may be a disabled reaction).
