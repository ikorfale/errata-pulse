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

## Robustness: the second eligible channel per region (run 2026-10-28 ~15:55Z)
Pre-registered ("robustness: the same test on the second eligible channel per region, reported beside the primary
whatever it shows"). Channels resolved 27.10 ~21:35Z before any reaction value was read (channels-robust-v2.tsv).
Belgorod has no second eligible channel and keeps the primary one; Tambov #2 could not be resolved (telemetr behind
Cloudflare), so it keeps tambov_smi. Crimea's second channel (Crimeanwind) is Ukrainian-leaning: a different readership.
Outputs: run_v2r_robust_check.txt (CHECK PASSED), run_v2r_robust_run.txt.

Event set differs from the primary: Bryansk enters (bryansk_smi covers the strike, 35 strike posts in block 0), Ryazan
drops by the sensitivity floor (ya62ru readers put 0 alarm reactions over blocks -14..-1). 11 events again.

| test | events | mean rank | p (one-sided) | placebo (block -15) p |
|---|---|---|---|---|
| alarm (😱 😨) | 11 | 9.50 | 0.87 | 0.63 |
| alarm without Belgorod | 10 | 9.05 | 0.78 | |
| grief (😢 😭) | 11 | 6.05 | 0.067 | 0.15 |
| grief without Belgorod | 10 | 6.25 | 0.10 | |

Same verdict as the primary: bounded null for both. Alarm is again on the wrong side of 8 (event day below the window
median in 7 of 11; rank 1 only Rostov 16.08). Grief leans the same way as in the primary on a different set of
channels (rank 1 or 2 in 4 of 11: Smolensk, Kirov, Krasnodar 03.08 at 2, Rostov 16.08 at 1), but p = 0.067 does not pass
the frozen 0.05, and its placebo (0.15) also leans low, so the lean is not cleanly tied to the strike day. Two runs
leaning the same way are not two findings: they share 10 of 11 events (Belgorod and Tambov on the same channel) and the same outcome definition.
