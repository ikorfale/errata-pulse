# Reader fear after deadly strikes, v2: result (run 2026-10-28 ~05:05Z)

Design frozen 27.10 (PREREG-v2.md, sha ef003362); post-freeze decisions in POSTFREEZE-v2.md, all taken before any
reaction value was read. Files used: hashes listed in POSTFREEZE-v2.md, all `sha256sum -c` OK before the run.
Outputs: regex_v2_check_v2r.txt, run_v2_check.txt, run_v2_run.txt.

## Order of steps, as frozen
1. Classifier re-check on the re-fetched full text (regex_v2_check_v2r.py, only the glob changed): 12 TP, **5 FP**
   (was 3 on the old text), 0 FN, 31 TN, 2 footer-only promos excluded. The two new false matches (#4 a "прилёт" of
   an American plane, #36 a tram "авария") come from text the old parser dropped. False matches only remove ordinary
   posts from the primary cell (5 of 36 here); the frozen regex was not changed.
2. `run_v2.py check`: CHECK PASSED. Bryansk (event 2) drops by block-0 coverage, as frozen; 11 events enter.
3. `run_v2.py run`.

## Result
Statistic: mid-rank of the event day's fear share among its 15 days (event day + 14 before), summed over events;
exact one-sided null. Mean rank 8.00 = no effect; 1 = the event day is the most fearful day of its window.

| test | events | mean rank | p (one-sided) | placebo (block -15) p |
|---|---|---|---|---|
| **primary: alarm (😱 😨)** | 11 | **9.18** | **0.82** | 0.65 |
| alarm without Belgorod | 10 | 8.70 | 0.71 | |
| secondary: grief (😢 😭) | 11 | 6.50 | 0.13 | 0.90 |
| grief without Belgorod | 10 | 6.75 | 0.18 | |

Verdict by the frozen rule (claim only if p <= 0.05 and placebo p > 0.05): **bounded null for both**. With K = 11 the
design had 80% power for a mean rank of about 4.8; the observed alarm mean rank, 9.18, is on the wrong side of 8.
So: on these 11 deadly strikes, the alarm share on the region's main news channel on the strike day was not higher
than on its own preceding days; an effect as large as the design could see is ruled out, a small one is not.

Per event, alarm: the event day was the most alarmed day of its window once (Crimea 05.05), in the top 4 twice
(Crimea, Rostov 16.08), and below the window median in 8 of 11. Grief leans the other way (event day rank 1 twice:
Smolensk, Rostov 16.08; rank 2 twice: Kirov, Krasnodar 03.08), but p = 0.13 is not a finding, and grief was the
secondary outcome.

## What this does and does not say
- It is the readers of one channel per region, and the reaction set the admins allow; not the region.
- Strike-topic posts are out of the primary cell by design: the question was whether the day's *other* news is read
  with more alarm. It is not, at the size this design can detect.
- v1 (24.10, Fontanka, one day, post-level bootstrap) reported fear up on unrelated posts; its correction (board
  101696) already said the day level does not support it. v2 does not support it either.
- Not run yet: the pre-registered robustness run on each region's second eligible channel (#539).
