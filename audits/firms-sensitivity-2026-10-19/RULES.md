# Rules fixed before scoring (2026-10-19 00:40 UTC)

Question: when my strike collector says "satellite: no clear fire" for a claimed strike on a Russian oil
site, what does that mean? Ground truth: strikes where a non-Ukrainian source (governor, company,
officials, Reuters/Bloomberg industry sources) confirmed a fire at the facility; negatives where the
governor said the attack was repelled without fire. Data: NASA FIRMS VIIRS (S-NPP, NOAA-20, NOAA-21),
SP archive to 2026-06-30, NRT after; days -33..+6 around each strike.

Rules (evaluate.py, unchanged after the ground truth is seen; any later rule is labelled post hoc):
- R0 current collector: 20 km box, S-NPP + NOAA-20, detections on day and day+1, fire if >=3 and
  mean per day >= baseline mean + 3 sd (sd floor 0.5), baseline days -32..-3.
- R1 = R0 plus NOAA-21.
- R2: 5 km, three satellites, Poisson tail p < 0.01 against the baseline mean, >=2 detections.
- R3: 5 km, three satellites, the brightest detection (FRP) in the window beats every baseline day.
- R4: R2 with window day-1..day+2 (night attacks and late reporting).
- R5: any detection within 3 km in day..day+1 (a lower bound on what the satellites can see at all).

Reported for each: sensitivity with a Wilson 95% interval, flag rate on no-fire cases, and the flag
rate on quiet 2-day windows before each strike (an upper bound on false alarms: unlisted strikes
may sit there). Expectation before scoring: R0 sensitivity under 30% (it flagged 8 of 100 claims,
with no difference between claims a Russian source acknowledged and Ukrainian-only claims);
R2/R4 higher at a false-alarm rate under 5%.

## Amendment v2 (2026-10-19, before any ground-truth event was scored; only a one-event smoke test)
A second model (Claude Fable 5.1) reviewed the design; applied: (1) other claimed strikes at the same site
(ground truth plus my collector's claims since 2026-08-31) are masked from baselines (days -1..+3 around
each) and quiet windows overlapping them are dropped; (2) day offsets use the local solar date of each
detection (UTC time + longitude/15 h), so a night overpass at ~01:30 local is not filed under the
previous UTC day; (3) failed or error chunks are recorded and never read as zero detections: a window
with missing data is not judged, a baseline needs >=15 clean days; SP/NRT seam at 2026-06-30 fixed;
(4) Poisson tail in log space; (5) quiet windows step by their own length, end before day -3, are
deduplicated by site and absolute dates, and are reported with their number of sites; (6) coordinates
are checked against the centroid of baseline detections. Ground truth also records size class (brief /
long / multi-day), attack hour and whether the confirming source cites satellite data (those are
reported separately as circular).

**Primary comparison: R0 vs R2.** Adoption rule: switch the collector to R2 if its sensitivity beats
R0 by >=15 points with a quiet-window rate <=5%. R1, R3, R4, R5 are descriptive. No-fire negatives are
descriptive only: a governor's "repelled, no fire" is not a verified absence.
