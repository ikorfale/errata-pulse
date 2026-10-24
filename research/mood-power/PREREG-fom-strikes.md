# PREREG (draft v1.5, 23.10.2026; v0-v1.5 each reviewed by a second model): do single strikes move national anxiety in the FOM weekly poll?

Status: DRAFT, not frozen. Freezes when committed with a sha256 in the board thread, after a second-model review.
No FOM value after 2026-10-20 has been looked at (the forward strike register, which opened 22.10, is read). Plan task #350, power check: errata-pulse research/mood-power.

## Question
H1-single: in the first FOM wave fielded 1-9 days after a qualifying strike, the "anxious" share is higher than
in the 2 preceding waves, beyond what the same statistic does in comparable weeks without a qualifying strike.

## Strike register (fixed criterion, chosen before outcomes)
Territory: Russia within its internationally recognised pre-2014 borders, plus Crimea. Annexed 2022 regions excluded.
A qualifying strike is an event in the window 2026-10-21..2027-04-30 meeting EITHER:
- (a) Moscow city or Moscow Oblast: >= 100 drones downed over the Moscow region in one calendar day (Moscow time),
  summing every MoD bulletin dated that day, Moscow-region line only (a night raid counts on the date of the morning
  bulletin). If the MoD stops giving a regional breakdown, Sobyanin's own count for the city is the fallback; OR
  (fallback detail, added 20.10 after the backfill showed his single posts cover 0.39-1.00 of his own window totals:
  use his daily 08:30-08:30 total when he posts one; otherwise each summary with a window <= 36 h counts as
  max(summary, singles inside it) on the summary's date and other singles by their own day; a day with no post of
  either kind is missing, not zero. errata-pulse research/mood-power/register.)
- (b) any region: >= 5 and < 20 civilians killed in one attack (one region, one day), per the first official
  statement of the governor or federal officials, toll frozen 72 h after the first official statement (v1.2).
  [v1.2, 21.10 15:10 UTC, date rule; second model proposed it, I took it with one change:] The strike date is the local
  calendar date, in the region's official time zone, of the publication timestamp of the first official statement
  (governor, regional government or operational HQ, federal body) reporting at least one civilian death from the
  attack. The attack's own start time and non-official reports are not used for dating. Every later official toll for
  the same attack, up to 72 h after that first statement, belongs to that date (my change: updates stay with their
  attack, so an overnight attack is never split). Different attacks in one region whose first statements fall on the
  same local date form one region-day and their frozen tolls are summed; a region-day qualifies at 5..19. Both dates
  (attack, first statement) are recorded. Examples from the candidate list: Dzhankoi 05.05 23:xx, post 06.05 00:12 ->
  06.05; Koloskovo evening 16.08 (local channel), official post 17.08 -> 17.08; Chekhov district overnight 3/4.08 -> 04.08.
  [v1.3, 21.10 18:20 UTC, who counts; second model reviewed it:] The count is every person killed whom the official
  statements do not identify as armed forces, Rosgvardia or another armed formation, double-tap deaths at the same site
  within the 72 h included. Each event carries three tags, recorded before any FOM series is read: rescuers (MChS,
  firefighters, medics), police (MVD, FSB, border service), and target type (residential, industrial or defence,
  transport, other). Primary analysis: the full count. Pre-declared sensitivity A: drop events that reach 5 only with
  rescuers or police. Exploratory only: toll as a continuous dose over all events with 3+ dead. Disclosure: this rule
  was written after seeing the Smolensk case (25.02.2026: first toll 4 plant workers, 7 within 72 h, 6 of them
  firefighters); Smolensk is the candidate whose inclusion depends on it. The v1.2 date rule is unchanged.
National shock (excluded, not a strike): >= 20 civilians killed in one attack, any death in Moscow city from a strike,
a mobilisation decree, a new front, a mass-casualty terror attack (both defined in v1.4 item 6). Logged separately, +-35 days excluded.
Merge: an event within 21 days of the first date of an earlier qualifying strike joins it (no chaining; the first
date counts). The register is filled from these official sources only, by date, without reading the FOM series; each
entry is committed and hashed before FOM publishes the wave that would measure it.
The same criteria are applied backwards to 2025-10-21..2026-10-20 (for the placebo pool), before the pool is drawn.

## Measurement
- Treatment wave: first FOM wave whose fieldwork start (series date - 2 days) is 1..9 days after the strike date.
  Both baseline waves must have fieldwork ending before the strike date, and no baseline wave may be more than 10 days
  from the next (New Year break). Otherwise the strike is unmeasurable, reported as such, never replaced.
- Statistic: stat2 = anxious(treatment wave) - mean(anxious of the 2 preceding waves).
- Placebo pool: one pool for the whole test, all waves 2025-10-21..stop, excluding only waves whose stat2 window
  (the wave and its 2 baseline waves) contains a register treatment wave or the wave after one, and +-35 days of
  national shocks. ~~The pool must hold >= 60 waves (3-wave spacing needs about 6n); if not, no test, report underpowered.~~
  [v1.1, 20.10 20:00 UTC: the fixed ">= 60 waves" rule is replaced, see Test. Reason: with wave dates only (no FOM
  values joined), the backfill year has 46 waves and 7 merged register events leave 28; forward ~27 more, so the pool
  would end near 40-45 and the test would never run, and more strikes would make it less likely to run. Backfill
  register hashed before this change: errata-pulse 4f60b0a, sha256 sobyanin_register.tsv 599d9892b7730fcd...,
  moscow_daily_backfill.tsv 62c9fd09c59228d5..., criterion_b_candidates.md 61322e54ac8bc48d... (candidates, to be
  verified against official posts; any change is logged with its reason). Reviewed by a second model (Fable).]
  Pool exclusion (v1.1): for every register event, measurable or not, exclude the first wave fielded after the strike
  date, the following wave, and every wave whose stat2 window contains either; and +-35 days of national shocks.
  No backward extension before 2025-10-21 (a calmer or trending period shifts a non-centred null down).
  (v0's same-year / trailing-52 rule dropped: around frequent strikes it emptied the pool and drew the null from
  calmer months, which is anti-conservative.)
- Extraction: fom_geom.py v2 on FOM's published PDFs; a new wave is parsed once, the parsed value is committed with
  the PDF's sha256 before the strike list for that month is joined to it.

## Test
- Primary (v1.1): permutation. Units are the n treatment stat2 values plus all pool stat2 values. Statistic:
  mean(treatment) - mean(rest). Null: uniform over all relabellings that choose n units with no two within 3 waves of
  each other (treatment waves included in the spacing check). Enumerate all relabellings if fewer than 200,000, else
  draw 20,000 uniformly by dynamic programming over wave positions (no draw can fail). One-sided, 5%. No pool-size
  rule; the only no-test condition is n < 5. Report the exact number of relabellings and the MDE at the realised n and
  pool size. (v1's "mean of n placebo waves drawn from the pool" understated the null SD by 8-18% at pool 60-28 through
  finite-population shrinkage, which is anti-conservative.)
- Sensitivity, pre-specified: the same permutation restricted to relabellings matched by calendar quarter (strikes
  cluster in summer-autumn; a seasonal drift in anxiety would bias the unmatched primary).
- Stop: at 10 measurable strikes, or on 2027-04-30, whichever comes first (backfill measurability 5 of 7 suggests n near 5 at the date stop; n < 5 is the binding floor). If fewer than 5 are measurable at the
  stop, the result is reported as underpowered and no p-value is given.
- MDE of the v1.1 permutation test on real 2025-26 placebo waves (errata-pulse 265c8dd, research/mood-power/mde_perm.txt; null sd of the waves 2.08): n=5 about 2.7-2.9 points, n=7 2.2-2.5, n=10 1.9-2.3 for 33-50 units. With 33 units and n=10 only 3,003 spaced relabellings exist, so the smallest attainable p is 1/3003. Earlier estimate:
- MDE (to be recomputed for the permutation test at realised n and pool) at n=10 was about 1.6 points if variance stays at the 2023-26 level, 2.2 at the 2022 level (mde_sim.py).
- Secondary, pre-specified: median stat2, and the share of strikes above the placebo median (sign test), so one
  outlier cannot carry the mean. Descriptive: "hard to say" share, per-strike percentiles, and FOM waves not
  published in the window (omissions are not random).
- Always reported: the one-sided 95% upper bound on the effect (mean minus null q05), with an MDE table for n=5..10.

## Estimand
The effect of a qualifying strike *as covered by state media* on the national anxious share. A null is consistent with
coverage being suppressed, not only with indifference.

## What would count as what
- p < 0.05: single strikes move national anxiety on average by more than noise, at about the size estimated.
- p >= 0.05: no detectable effect; the upper bound says how large an effect the data still allow; not "no effect".
- Either way the earlier anecdote (Moscow raid 11.03.2025, +2.5) is not counted and not pooled.

## Freeze postponed (23.10.2026, written by 01:28 UTC per date -u): open decisions before v1.4
The backfill register was assembled and hashed as a draft (errata-pulse 4ba3c54 and the next commit). A second model
(Fable) reviewed it and found 26 items; the ones that must be decided before the freeze:
1. Pool exclusion per qualifying DAY (members too) or per event start. Leaning per-day ("weeks without a qualifying
   strike"); report both, so the choice cannot decide the outcome.
2. Exclude also the wave in the field on a strike date (07-17 wave vs Kotovsk 07-18).
3. Spacing written as "gap >= 3 waves", asserted in code.
4. A forward strike within 21 days of the 10-06 backfill event (forward register opened with Moscow 22.10, 163):
   joins the backfill event (lean) or starts a forward event.
5. Baseline-inside-another-event tag, descriptive split.
6. National-shock thresholds: "mass-casualty terror attack" and "new front" are undefined. The 01.08 Moscow restaurant
   bombing (3 -> 5 killed) was found while checking; it would remove 27.06-05.09. Whatever threshold is set now is set
   knowing this case; both versions will be reported.
7. Pool size recomputed from real wave dates (v1.1's "28 of 46" does not reproduce: ~22 per-event, ~19 per-day).
8. Resolve the five "0?" tags; near-miss rows that could flip an event (12-23, 03-21, 04-28, 06-04) get full evidence.
9. Line 21 vs v1.2: the 72 h freeze runs from the first official statement (v1.2 wins). Sevastopol is its own region.
Disclosure: the FOM 2025-26 values were in the workspace (MDE table, 21.10) when v1.2, v1.3 and these decisions were
made. No per-wave placebo value has been read against the register dates.

## v1.4 (23.10.2026, ~09:20 UTC): decisions 1-7 and 9 (text drafted by a second model, Fable; checked and taken)
1. **Pool exclusion per qualifying day.** For every register day d meeting (a) or (b), event start or member,
   measurable or not: W0 = the wave whose fieldwork interval (series date - 2 .. series date) contains d; W1 = the first
   wave with fieldwork start after d; W2 = the wave after W1. Exclude W0, W1, W2 and every wave whose stat2 window
   (the wave and its 2 baseline waves) contains W1 or W2. Merging decides treatment units only; it never reduces pool
   exclusion. Pre-declared sensitivity B: the same rule applied to event-start days only.
   Reason: H1 compares with "weeks without a qualifying strike"; a wave fielded after a member strike is not one.
2. **Wave in the field on a strike date (W0)** is out of the pool, never a treatment wave, never a baseline.
   Example: the 07-17 wave is W0 for Kotovsk 07-18.
3. **Spacing, asserted in code.** Positions are indices in the ordered list of all published FOM waves from 2025-10-21,
   excluded waves included. Two units may be chosen together iff |pos_i - pos_j| >= 3. The code asserts this for every
   relabelling and for the observed treatment set. If the observed set violates it (only possible when a wave is
   unpublished), g is set to the set's minimum pairwise gap for that run, computed from dates before any value is
   joined, and reported.
4. **Forward strike within 21 days of the 10-06 backfill event** (up to 2026-10-27, so Moscow 22.10, 163 drones) joins
   that event, is not a treatment unit, and contributes its exclusions under rule 1. The first forward event starts
   with the first qualifying day on or after 2026-10-28.
5. **baseline_contaminated tag** = 1 if either baseline wave of a treatment unit is W0, W1 or W2 of any qualifying day,
   assigned from dates before values are joined. Primary uses all units; descriptive split only (mean and median
   stat2 by tag), no test.
6. **National-shock thresholds.** Mass-casualty terror attack (primary): an attack not meeting the strike definition
   in which >= 20 people are killed per the first official statement, frozen 72 h after it, perpetrators excluded
   (the v1.0 strike-shock threshold applied to all attack types). Pre-declared dual report S3: >= 3 killed,
   perpetrators excluded (US federal "mass killings": "3 or more killings in a single incident", 28 U.S.C.
   530C(b)(1)(M), Public Law 112-265; wording checked on uscode.house.gov 23.10). New front: the first day a federal
   source (MoD, FSB, NAK, Kremlin) or the governor acknowledges ground combat with regular foreign forces inside a
   region of the territory definition that had no counter-terrorist-operation regime in force on 2026-10-20, or on
   which such a regime or martial law is introduced there; the list of regions with a regime on 2026-10-20 is fixed at
   the freeze. Cross-border raids without that acknowledgement do not count. Disclosure: written knowing the
   01.08.2026 Moscow restaurant bombing; under primary it is not a shock, under S3 it is (27.06-05.09 out). Computed
   from dates (decision 7): in the backfill year S3 removes no additional wave, because rule 1 already excludes
   every wave in that window.
7. **Pool from real wave dates** (errata-pulse research/mood-power/register/pool_v14.py, output pool_v14.txt, dates
   only, no FOM value loaded). Added rule, like for like with treatment units: a pool unit must pass the same
   measurability rule (its 2 baselines and itself chained in steps <= 10 days), which removes 01-18 and 01-25 after the
   New Year break. Backfill year: 46 waves, 21 qualifying days, 7 events. Pool: 18 waves (per-day, primary; S3 the
   same), 20 (per event start, B). Spaced subsets of the backfill pool alone: n=5 888, n=7 111, n=10 0. So n=10 is only
   reachable with forward pool waves; the MDE table must be recomputed at the realised pool, and the minimum attainable
   p is reported with the result.
9. **72 h freeze** runs from the publication time of the first official statement reporting a civilian death (v1.2
   wins over line 21). Regions for (b) are federal subjects: Sevastopol and the Republic of Crimea are separate; Moscow
   city and Moscow Oblast are separate for (b), summed as "the Moscow region" only for (a).
8. **Tags and near misses** (evidence: errata-pulse research/mood-power/register/evidence_v14_item8.md, officials'
   Telegram posts with times). The five "0?" rescuer/police tags become 0: no official statement within 72 h names a
   rescuer, police or FSB officer among the dead (inferred from wording, none says so outright; sensitivity A therefore
   drops nothing). Near misses stay below 5: Belgorod 2025-12-23 (3+1), 2026-03-21 (4), 2026-04-28 (3+1; the
   Novaya Tavolzhanka death was posted 27.04), 2026-04-29 (bus, 3; no later death found through 4 May, excerpts only),
   Crimea 2026-06-04 (3+1; later hospital deaths not checked in the health ministry's channel: open, would flip only
   by one more death). Rule for the toll: only statements published by the official's or body's own channel or site
   count; a spoken figure reported by media does not (Bryansk 10.03: governor said "eight" at a Civic Chamber session
   ~72 h after the first post; the posted toll is 7; the event qualifies either way).

### v1.4 reconciliation (second-model review of v1.4, 23.10 ~09:00 UTC): where earlier lines are superseded
- "Fielded after d" everywhere means fieldwork start after d; the v1.1 pool-exclusion paragraph is superseded by v1.4
  items 1-2. Waves are named by series date (the rule-2 example "07-17 wave" is the wave dated 2026-07-19).
- Spacing is |pos_i - pos_j| >= 3 (item 3); "no two within 3 waves" means exactly that. Positions are positional across
  the New Year gap; excluded waves (01-18, 01-25) still count as positions.
- The 10-day rule has ONE reading for treatment and pool units alike: the unit's wave and its 2 baselines chained in
  steps <= 10 days. Under it backfill measurability is 4 of 7, not 5 of 7 (Crimea 05-06: 05-03 to 05-17 is 14 days).
- "No backward extension": units may not precede 2025-10-21; their baseline waves may.
- The MDE lines with "33-50 units, 3,003 relabellings" and the n=10 table are superseded by item 7 and by the table below.
- Power at the realised design (null sd 2.08): MDE80 about 2.6-2.9 points at n=5, 2.2-2.5 at n=7, for 23-30 pool
  units. p is discrete with floor 1/N, N reported. A null leaves effects up to about 3 points unrefuted (the 11.03.2025
  anecdote was +2.5: power against an effect that size is about one half). The sign test can reject only at 5/5
  (p = 0.031) for n=5 and only at 7/7 for n=7.
- Only the primary analysis is confirmatory. Sensitivities A, B, S3 and the quarter-matched test are reported whatever
  their outcome. The pool (Oct 2025 - Jun 2026 plus forward waves) and the treatment waves (winter-spring 2027) differ
  in season; a secular drift cannot be told apart from an effect, and quarter strata may be empty.

### Open before the freeze (25.10 12:00 UTC)
10. **n < 5 is the most likely outcome.** Expected forward n is 1-3: a strike on a fieldwork day (Fri-Sun) is
    unmeasurable because W0 is out, and 6 of 7 backfill events fell outside November-April. Options: (a) accept and
    say so; (b) let baselines skip W0 (the two latest waves ending before d), disclosing the variance mismatch;
    (c) move the stop date. Decide before the freeze, with the reason, before any forward FOM value is read.
    **Decided 23.10 ~12:15 UTC** (design attacked by a second model, Fable; my lean was (a) + skip-W0 as secondary
    without a date move; it showed a pool wave has no strike date, so skip-W0 has no same rule for the pool, and that a
    stop date fixed at the freeze is a design parameter, not a fork). Frozen text:
    Stop at 10 measurable strikes or on 2027-10-31, whichever comes first; the date is fixed at the freeze and does
    not move again. Primary unchanged: if n < 5 at the stop, no p-value; report per-strike percentiles, the sign count
    and the one-sided upper bound. Sensitivity C, pre-specified, same status as A, B, S3: stat3 = anxious(W1) -
    mean(anxious at positions W1-2, W1-3), one rule for every unit, treatment and pool alike, computed from dates
    before any value is joined. A unit is measurable iff the consecutive waves W1-3..W1 are each <= 10 days apart.
    Pool exclusion as rule 1 with the 4-wave window; spacing >= 4. C runs iff its n >= 5 and is then reported
    whatever its outcome; its null sd and MDE are computed from the 2025-26 waves and recorded at the freeze.
    Backfill events are never pooled into either test (the v1.2/v1.3 rules were written knowing which backfill cases
    they include). The "Stop" line in Test is superseded by this item.
    Before the freeze: pool_v14.py with the 4-wave window and spacing 4 (C's pool size and N of relabellings), and C's
    null sd and MDE from the 2025-26 waves, by the same computation as the primary's MDE table.
    **Done 23.10 ~12:53 UTC** (errata-pulse 4417db2: register/pool_v14.py --C -> pool_v14_C.txt; mde_perm_c.py -> mde_perm_c.txt;
    primary pool_v14.txt re-run byte-identical). C's backfill pool: 15 waves per-day (S3 the same), 17 per event start;
    spaced subsets of the backfill pool alone: n=5 9 (B 61), n=7 0. So C, like the primary at n=10, needs forward pool
    waves before it can reach a useful minimum p, and its minimum attainable p is reported with the result.
    C's null on the 61 2025-26 placebo waves that pass the 4-wave measurability rule: stat3 sd 2.63 (stat2 on the same
    waves 2.19). MDE80, one-sided 5%, C vs primary on the same units: 25 units n=5 3.62 vs 3.25; 33 units n=5 3.42 vs
    3.18, n=7 2.81 vs 2.63; 40 units n=5 3.31 vs 2.86, n=7 2.68 vs 2.42. Rows with fewer than 200 relabellings
    (20 units n=5 C 159; 25 units n=7 C 60) are not used for MDE claims. Reading: C buys about 1.7x the measurable
    strikes at the cost of a 7-15% larger MDE per strike; it stays a sensitivity, as decided.
11. **Fieldwork dates are assumed** ("series date - 2"); the archive has waves dated on a Tuesday (12-22) and a
    Wednesday (07-29). Read the fieldwork dates from each PDF, hash them, have pool_v14.py use them, recompute item 7.
    **Done 23.10 ~10:55 UTC.** register/fieldwork_dates.py read the fieldwork line of 54 weekly FOM issues
    (2025 no36 to 2026 no42; pdftotext -raw; sha256 of each PDF in fieldwork.tsv; 5 issues not on the server: 2025-52,
    2026-1, 2026-2, 2026-19, 2026-38, none of them a series date in the window). All 51 series dates in the window have
    a recorded interval. 49 follow the convention (Fri-Sun, 3 days); 2 do not: 19-22.12.2025 (4 days) and
    24-29.07.2026 (6 days). pool_v14.py now reads fieldwork.tsv and stops on any wave without one (no fallback).
    Recomputed item 7: pool_v14.txt is byte-identical to the convention-based output. The PDFs carry the weekly values;
    the script extracts only the fieldwork line and no mood value was parsed or printed (errata-pulse 6fa131d).
12. Crimea 06-04 hospital check (item 8), done 23.10 ~18:22 UTC: stays 4 (3+1). The Crimean health ministry's channel
    has no post on the attack 04-08.06; the federal ombudsman (own MAX channel, 06.06 13:59 UTC, ~9 h before the 72 h
    window closes) reports six in hospital and no death; Aksyonov's channel has no revision through 11.06. Operational
    HQ channel not checked. Evidence: errata-pulse 5404489. Next: a second-model review of the final text, hash, freeze.

## v1.5 (23.10.2026, ~18:24 UTC per date -u): final hostile review of the whole text by a second model (Fable), 8 items, all taken
No FOM value was read for this section. Where a line above disagrees with an item here, the item here wins.
1. **Register window = stop date.** The forward register runs 2026-10-21..2027-10-31 (line 12's "2027-04-30" is
   superseded, matching item 10's stop date).
2. **Treatment units near a national shock.** A qualifying strike whose treatment wave or either baseline wave lies
   within +-35 days of a national shock is unmeasurable, reported as such, never replaced (C: its own 4-wave window).
3. **Backfill register frozen with this hash.** Events, tags and near-miss tolls of 2025-10-21..2026-10-20 are as in
   errata-pulse up to commit a60ab79 (evidence_v14_item8.md and the register files; a60ab79 only corrects a timestamp in 5404489). No source not cited there is
   consulted for backfill cases after the freeze; a later-found error is reported next to the result, not applied.
4. **Fieldwork dates.** Every rule (treatment wave, W0/W1/W2, baselines, the 10-day chain, pool exclusion) uses the
   start and end dates in fieldwork.tsv, read from each wave's PDF (fieldwork line only) before its value is parsed.
   "Series date - 2" is the usual case, not the definition (line 47 superseded).
5. **Pool end.** At the strike-count stop the last pool wave is the treatment wave of the 10th measurable strike; at
   the date stop it is the last wave whose fieldwork ends on or before 2027-10-31.
6. **Terror attack** (both primary >= 20 and S3 >= 3) = an attack by means other than drone, missile, artillery,
   glide bomb or air strike. Sub-threshold strikes are never national shocks under S3. (Without this, every 3-4 death
   strike would be an S3 shock; line 145's "S3 removes no additional wave" was computed for the restaurant bombing
   only and stands under this definition.)
7. **"New front" regions with a counter-terrorist-operation regime on 2026-10-20:** Belgorod, Bryansk and Kursk
   oblasts (introduced 10.08.2024 by the NAK; in force per Bortnikov, Kommersant 10.03.2026; no lifting found in a
   search on 23.10.2026). Martial law on 2026-10-20 covers only the annexed regions, which are outside the territory.
8. **Spacing fallback for C and seeds.** Item 3's fallback applies to C with g = min(4, observed minimum gap). Every
   random draw (primary, B, S3, quarter-matched, C) uses numpy default_rng(20261025).

## v1.6 (24.10.2026, ~00:49 UTC per date -u): blocking-issue check of v1.5 by a second model (Fable), 5 items, all taken
No FOM value was read for this section. Where a line above disagrees with an item here, the item here wins.
1. **Pool end (replaces v1.5 item 5, first sentence).** At the strike-count stop the pool window ends with the
   treatment wave of the 10th measurable strike; rule-1 exclusions (W0, W1, W2 and every wave whose window contains
   them) still apply to every wave in the window, so that treatment wave is never a pool unit.
2. **"Within +-35 days of a shock"** means any fieldwork day of the wave (fieldwork.tsv) lies within 35 days of the
   shock date. An attack shock is dated by the v1.2 date rule; a decree or a CTO regime by its official publication
   date. (This is what pool_v14.py already computes for S3: fieldwork interval overlapping [c-35, c+35].)
3. **The count stop is final.** The 10th measurable strike counts once 35 days have passed after its treatment wave's
   fieldwork end with no national shock touching its treatment or baseline waves. A shock found or occurring after
   that is reported next to the result and never reopens the stop or moves the pool end.
4. **Criterion (b) means.** In the forward register, (b) counts only attacks by drone, missile, artillery, glide bomb
   or air strike; any other attack is a terror attack (v1.5 item 6) and never a (b) strike. The backfill register
   stays as frozen in v1.5 item 3.
5. **10-day chain.** Steps are measured between fieldwork end dates (the series date of each wave, as in pool_v14.py
   and pool_v14_C.txt), so the computed pool sizes and MDE tables above are unchanged.
6. **Which stop applies** (follow-up check of v1.6 by the same second model). The count stop applies iff the 10th
   measurable strike's treatment wave has fieldwork end on or before 2027-10-31, whatever date its 35-day
   confirmation completes; otherwise the date stop applies, and strikes dated on or before 2027-10-31 remain treatment
   units even if their treatment wave is fielded after that date.

## Freeze
This text is frozen at the commit that adds this line. Its sha256 is recorded in the commit message and in the plan;
any later change is an amendment dated by its own commit and listed next to the result.

## Amendment 1 (24.10.2026, after the freeze, before any forward FOM value is read; third blocking-only check by a second model)
Added to v1.6 item 3: at either stop (count or date), the register of national shocks is closed. A shock first
recorded after the stop is reached is reported next to the result only; no unit's measurability, pool membership or
tag changes because of it, as with backfill errors under v1.5 item 3.
