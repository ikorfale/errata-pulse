# H2 draft r3: negative reactions on neutral news after deadly strikes, against control regions (DRAFT, not frozen)

Written 2026-10-31 ~13:55Z for #517; r1 ~13:50Z after the first blocking review (fable-h2-1.txt, 13 points, all
adopted; r0 in archive_tmp/PREREG-H2-draft-r0.md); r2 ~13:55Z after round 2 (fable-h2-2.txt, 6 points, adopted;
r1 in archive_tmp/PREREG-H2-draft-r1.md); r3 ~14:02Z after round 3 (fable-h2-3.txt, 5 points, adopted). No H2 outcome value has been read for any channel or date in this
design. Freeze only after blocking-only second-model reviews answer NONE (fable-h2-*.txt next to this file).

## Why a new event set (the main constraint)
v2 (PREREG-v2.md, RESULT-v2.md) already read reaction shares of the treated channels on the 11 deadly-strike events of
Feb-Oct 2026 (alarm and grief, 24 h, non-strike posts): bounded null for both, on the primary and the second channel.
Those windows are not blind any more, and any outcome chosen now for them would be chosen after seeing alarm and grief.
So H2 is tested only on **prospective events**: hour 0 after the freeze timestamp, up to 2027-01-31 or K = 12, whichever
comes first. Events are logged in `h2_events.jsonl` within 72 h of hour 0, from toll data only, before any reaction of
that window is fetched. No retrospective events (a toll 1-3 set was rejected: near-daily tolls in border regions
contaminate baselines, and its windows overlap v2 windows on the same channels).
**v2-read spans.** For every v2 event and channel (primary and robustness), the span from v2 hour 0 minus 30 days to
plus 24 hours is "read". The table of these spans is committed with the freeze (`v2_read_spans.tsv`). No H2 window,
norm or pseudo window may touch a read span on its channel.
v2's null is the prior and is printed beside the H2 result whatever H2 shows.

## Question
In the 48 hours after an official statement that a Ukrainian strike killed civilians in a Russian region, does the share
of negative reactions on that region's main city-news channel, counted on neutral-topic posts only, rise above the
channel's own 14-day norm by more than the same change on control-region channels over the same hours?

## Regions
- **Treated-eligible:** regions of the Russian Federation within its pre-2022 borders plus Crimea and Sevastopol,
  minus the controls (CONTROLS.md, usernames-controls.tsv) and minus the excluded below. The list is written out in
  `h2_regions.tsv` and committed with the freeze, each with its channel (next section).
- **Excluded, logged and reported, never tested:** Belgorod, Kursk, Bryansk oblasts (near-daily tolls, no quiet
  baseline) and the four 2022 oblasts (Donetsk, Luhansk, Zaporizhzhia, Kherson; same reason, plus no comparable media).
- **Controls are never treated.** A toll event in a control region is logged and excludes that control per the rule
  below.

## Event register (toll data only)
- Official toll (governor, regional HQ, head of district, federal official) of >= 2 civilians killed within 72 h of
  the first statement, in a treated-eligible region. Toll printed beside each D_e; no second test by toll.
- Hour 0 = timestamp of the first official death statement (the post itself, linked).
- **Toll >= 1 register** (`h2_tolls.jsonl`): one entry per strike, keyed by region and the strike the statements
  describe, in every treated-eligible and control region, from freeze - 504 h to pool_end + 48 h. Hour 0 = the first
  statement by the officials above of >= 1 civilian killed by that strike; toll = the highest official count within
  72 h; later statements update the entry, never open a new one. v2's civilian definition (rescuers count).
  "Another event" anywhere below means a different entry.
  Toll data only. It may be compiled at any time, but it is closed and committed (sha in the log) before any
  reaction is fetched. Every "toll >= 1 event" rule below reads this file and nothing else.
- Excluded: another toll >= 1 event in the same region whose hours 0..48 overlap this event's hours -336..48; an event
  whose hours -336..48 touch a v2-read span on its channel.
- **Clustered events:** members are register events (toll >= 2) in regions listed in `h2_regions.tsv`, nothing else.
  They merge transitively: a unit is a maximal chain of hour 0s with gaps <= 48 h. Unit value = mean of the members'
  D_e; K counts the unit once. Control eligibility is per member, at the member's hours.
- **Stop:** fires when the log holds 12 units that survive the toll-based rules above (exclusions, merging); no
  reaction data is needed for it. Stop timestamp = hour 0 of the last member of the 12th unit + 48 h, or 2027-01-31
  if earlier. **K** = units remaining after the floor drops of the Outcome section; the K >= 6 minimum applies to it.

## Channels
- Treated: one channel per treated-eligible region, fixed before the freeze: v2 primary where it exists
  (usernames-v2.tsv), otherwise pick_v2.py's unchanged rule run and usernames resolved before the freeze, committed in
  `h2_regions.tsv`. A region without a resolved channel at freeze does not enter (its events are logged, reported).
- Controls: the 22 resolved channels of CONTROLS.md. The 4 pending regions are dropped and reported. A control is
  excluded for a member if its region has a toll >= 1 event (h2_tolls.jsonl) whose hours 0..48 overlap the member's
  hours -336..48.

## Neutral-topic posts (classified from text, before reactions are read)
- A frozen regex file `h2_topics.py` (sha256 in the freeze bundle) assigns weather, sport, or culture/leisure; neutral
  = any of the three. **Not neutral:** utilities, crime and courts, funerals, prices, transport (all can be
  strike-caused or security-driven).
- **Never neutral:** a post matching STRIKE_V2 (footer removed, regex_v2_check.py), or the frozen list NEVER =
  теракт, диверс, СБУ, ФСБ, агент, наводч, корректир, трагед, скорб, памят, отмен, перенес, траур (case-insensitive
  stems; "отмен"/"перенес" catch events cancelled for mourning, which are strike-driven).
- **Classifier checks before freeze, both blind (me and a second model, text only):**
  1. Precision: 100 posts, seed = freeze date, from control channels' posts dated before freeze - 504 h (the sampler
     drops reaction fields at fetch, only text is stored); classifier-neutral posts
     must reach precision >= 0.85 on consensus labels.
  2. Leak: 100 classifier-neutral posts from the treated channels' hours 0..48 of the 11 v2 events (text already read
     in v2; these events are not in the H2 set); at most 5 may be labelled strike-related in any way by consensus.
  Fail either -> revise the regex and redraw a fresh sample of the failed check. Recall is reported, not required.

## Outcome
- Negative set: 😱 😨 😢 😭 😡 🤬 👎 💔 😰 (U+1F631, U+1F628, U+1F622, U+1F62D, U+1F621, U+1F92C, U+1F44E,
  U+1F494, U+1F630). Every other reaction, custom emoji included, counts in the denominator only.
- Block value = sum of negative reactions / sum of all reactions over the block's neutral posts with >= 30 reactions.
- Event block = hours 0..48. Norm = hours -336..0, pooled the same way. Change = block value - norm value.
- Floor: a channel enters a member only with >= 5 neutral posts (>= 30 reactions) in the event block and >= 30 such
  posts in the norm, counted before any block value is computed. A member drops if its treated channel fails the floor
  or it has fewer than 8 eligible controls; a unit drops when no member remains (both reported).
- Posts are fetched at least 7 days after the block ends, so every post has aged >= 7 days.

## Statistic
For a member event: D_e = change(treated) - median over eligible controls of change(control), same hours. Unit value
= mean over its members. D = mean over units. One-sided: H2 predicts D > 0.

## Null (the shuffled input and what counts as a fail)
- **Pool:** pool_end = min(stop timestamp, 2027-01-31). The stop is final: no event logged after it enters, nothing is
  added after the fetch. Pseudo hour 0 is drawn from [freeze + 336 h, pool_end - 48 h], uniformly over hours, on the
  member's treated channel, eligible only if its hours -336..48 overlap no toll >= 1 event's hours 0..48 in that region
  (h2_tolls.jsonl) and touch no v2-read span. Pseudo windows of different draws may overlap. No extension before the
  freeze.
- **What is shuffled:** each unit's hour 0.
- **Pseudo events run the full pipeline** at the pseudo hour: control exclusion and floors. A pseudo unit carries the
  real unit's surviving members, offset from the pseudo hour as in the real unit; it is redrawn if any of them fails
  at the pseudo hour, up to 20 times; after that the draw skips that unit and the skip count is
  reported. A channel with no eligible hour drops its unit from the test, reported.
- 5000 draws of the full set of units, D* each time; seed = freeze date (numpy default_rng). p = (1 + #{D* >= D}) / 5001.
- **Claim only if p <= 0.05** and the placebo is not p <= 0.05. Otherwise a null, printed with D and the null's
  5th-95th percentile.
- **The null must have room to fail** (gavinagent, Clawk 31.10): before D is computed, a separate 500-draw run injects
  +delta into the treated block value at pseudo units and reports the detection rate at p <= 0.05; each injected draw's p is computed against the same 5000-draw null (not a
  nested one), so a rerun with the freeze seed gives the same rate. delta = 0.03, stated
  now as the smallest shift in negative share I would call a mood change (three points of share). If the rate is
  < 0.5, the result is "not testable at this K", reported before D is read, not a null. The pipeline also prints the
  smallest delta reaching 80% detection.
- **Placebo:** hour 0 moved to hour -168. A placebo unit drops (reported) if its hours -504..-120 overlap any toll >= 1
  event's hours 0..48 in its region (h2_tolls.jsonl) or touch a v2-read span on its channel; control exclusion at the
  placebo hour uses the same toll >= 1 rule; otherwise the full pipeline, same null. The placebo has the same minimum:
  fewer than 6 surviving placebo units -> no claim.
- **Fetch:** no earlier than pool_end + 48 h + 7 days, for treated and control channels over every window they serve
  (earliest: the first unit's hour -336). Coverage rule from v2: a channel's fetch must contain a post older than the
  earliest window start it serves, else re-fetch before anything is parsed; a 72-h stretch with zero posts inside a used
  window is reported as empty, never dropped silently.

## Minimum
The test is read only if K >= 6 units enter after all drops. With K < 6 at the stop: "not testable", reported with the
units and their D_e, no p.

## Blindness
Reaction values of any window are fetched only after the stop (K = 12 or 2027-01-31) and parsed only by the frozen
pipeline. Before that, the event log holds toll data only; channel checks never open a post page inside a logged
event's hours 0..48 (usernames are resolved before the freeze).

## What it cannot say
Readers of one channel per region, with the emoji the admins allow; not the region. Toll >= 2 is a weaker shock than
v2's >= 4; a null here does not cover large events. Excluding border regions removes the most exposed readers.
