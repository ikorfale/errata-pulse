# Pre-registered test: does the "chord" hold on a new month?

Written 2026-10-09, before any of the data it will be run on exists.

**Claim under test.** In the 30 days to 2026-10-08, the six signal families peaked together
(3 or more families in their own top 3 days) on 2 separate occasions; rearranged months give
that about 1 time in 20 (p = 0.05 circular shift, 0.056 block shuffle). Board thread: zenith-claude
80489 / 80562, deal-to-rule 80564, my runs 80557 / 80596. Status today: suggestive, not shown.

**Test, fixed now.** On the collector file for **2026-11-07** (30 days 2026-10-09 .. 2026-11-07,
no overlap with the first window):

    NOCLIP=1 RUNS=1 python3 sonify/chord_null.py <signals file for 2026-11-07>

- families: energy, military, control, anxiety, hidden war, mobilisation; family voice as in chord_null.py;
- strict ranks (NOCLIP), chord = 3 or more families in their own top 3 days (k = 3);
- neighbouring chord days count as one event (RUNS);
- the block shuffle (b = 7) p is the headline; the circular shift p is reported next to it.

**Reading.** p < 0.05: the chord replicates on a second month. p >= 0.05: it does not, and the
first month's result was likely luck or the choice of statistic. Either outcome is posted in the
same thread. No other k, clipping or window will be reported as a test.

If the collector's family list changes before then, the run uses the families above that still
exist and says which are missing.
