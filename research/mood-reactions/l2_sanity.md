# PREREG-L2 sanity check, run 2026-11-04 ~16:05Z: CORRECTION, not blind

**Correction (04.11 ~16:15Z, same pass):** this check was run against a superseded draft (PREREG-L2, 23.10). The
Fontanka 18.10 pilot it was meant to precede had already been run on 24.10 under PREREG.md (RESULT.md), and v2 on 11
deadly strikes on 28.10 (RESULT-v2.md). So the threshold below was *not* frozen before the 18.10 window was seen, and
nothing here may be used as a pre-registered test. What remains valid is the snapshot stability check (1)-(2): settled
posts barely move in 24 h, which supports the 72 h age rule those results relied on.

```
posts in 24.10 snapshot 568 overlap 543
overlap posts aged >=72h at first snapshot 416
(1) old posts gaining a new reaction kind 1/416, losing one 0/416
(2) total reactions on old posts 188287 -> 188427, growth 0.07%; per-post median 0.00%, max 1.7%, posts >5%: 0
    contrast: 127 posts younger than 72h grew 5.1%
days with posts 185 2026-04-19 .. 2026-10-20
(3) quiet fortnight 2026-09-20..2026-10-03: daily mean distress share mean 0.1226, SD 0.0490, posts/day median 34.0; meaningful effect (2xSD) = 0.0981
    whole range SD 0.0599 over 185 days
```
    other fortnight (3) quiet fortnight 2026-05-01..2026-05-14: daily mean distress share mean 0.1305, SD 0.0475, posts/day median 32.5; meaningful effect (2xSD) = 0.0950
    other fortnight (3) quiet fortnight 2026-06-01..2026-06-14: daily mean distress share mean 0.1511, SD 0.0778, posts/day median 31.5; meaningful effect (2xSD) = 0.1556
    other fortnight (3) quiet fortnight 2026-07-01..2026-07-14: daily mean distress share mean 0.1374, SD 0.0434, posts/day median 33.0; meaningful effect (2xSD) = 0.0868
    other fortnight (3) quiet fortnight 2026-08-01..2026-08-14: daily mean distress share mean 0.1795, SD 0.0520, posts/day median 31.0; meaningful effect (2xSD) = 0.1039
    other fortnight (3) quiet fortnight 2026-09-01..2026-09-14: daily mean distress share mean 0.1524, SD 0.0458, posts/day median 35.5; meaningful effect (2xSD) = 0.0915

Verdict: (1) pass: 1 of 416 settled posts gained a reaction kind, none lost one. (2) pass: settled posts grew 0.07% in 24 h
(max 1.7% per post, 0 above 5%); posts younger than 72 h grew 5.1%, so the 72 h age rule is needed and enough.
(3) threshold frozen: smallest meaningful effect on the primary = 0.098 distress share (2 x SD 0.049 of the first
fortnight computed, 20.09-03.10; five other fortnights give 2xSD 0.087-0.156, median ~0.095).

Limits written before the strike window: the fortnights were not checked for strikes on St Petersburg, and SD here is
over all posts, while the primary uses only hand-labelled "unrelated" posts, so its noise may be larger. The placebo
distribution (500 weekday-matched fake days) is the real test; the threshold only says what size I will call meaningful.
Next: hand-label D-7..D+2 (11-20.10) posts from the 24.10 snapshot, text only, date hidden.

**Hole found while writing the next step (04.11):** the primary uses only "unrelated" posts in the strike window, but
the 500 placebo windows were never said to be filtered the same way. Placebo differences over unfiltered posts are not
comparable to a filtered strike difference. Options: (a) label all ~5.8k posts with one frozen model labeller plus a hand
check sample, then filter strike and placebo windows alike; (b) drop the filter and run strike and placebo on all posts,
reporting strike-related posts as a separate count. Decide before labelling; (a) keeps the prereg's intent.
