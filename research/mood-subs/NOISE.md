# H5 baseline: noise of exact subscriber counts (census 05.11 10:24Z – 12.11 03:44Z, 15 fetches, 110 channels)

Script: lab/mood/subs/noise.py (reads only census.jsonl, no strike data). Output: noise.json. Run 12.11 ~07:3xZ.

- Governor channels (55): median drift −0.011 % per 12 h (week −0.13 %, IQR −0.21…−0.03): audiences are slowly shrinking, not growing.
- Noise (robust SD of 12-h steps): governors median 0.012 %, IQR 0.007–0.023 %.
- Heavy tails: 18 of 55 governor channels had at least one step ≥ 5 robust SD within one week. A robust-z threshold
  would fire on a third of channels weekly with no defined event, so it cannot be the H5 test.
- MChS channels: 23 of 55 counters did not move at all in a week (small channels, exact count changes rarely);
  35 channels under 5 000 subscribers have median noise 0. They carry no signal for H5; drop them.
- Peek disclosure: the printed "largest jumps" list names 6 governor handles (top: Leningrad oblast +1.06 % in one step).
  I saw these names before freezing; the prereg must not choose regions, windows or thresholds that fit them.

Consequence for PREREG-H5 (to draft): unit = governor channels ≥ 5 000 subs; event window and threshold set from each
channel's own empirical step distribution over the previous 14 days (e.g. step above its 95th percentile), compared
struck vs matched far regions with the same rule, so the base rate of "jumps" is the same in both arms by construction.
