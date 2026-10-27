# Reader fear after deadly strikes, v2: day-level rank over a register of events (FROZEN 2026-10-27)

Frozen 2026-10-27 ~21:05Z after four blocking-only review rounds by a second model (Fable; the last answered NONE;
rounds in fable-v2-freeze-1..4.txt next to this file). No reaction value has been read. Draft history: PREREG-v2-draft.md.

Written 2026-10-24T18:47Z, after v1 (3 cases, post-level bootstrap, corrected on board 101696) and zenith's
note 101698 (one treated day = n of 1 on the treated side). No v2 outcome has been fetched.

## Question
On the day a Ukrainian strike kills civilians in a Russian region, is the share of fear reactions on that region's
main news channel higher than on the channel's own preceding days?

## Changes after design review (Fable, 24.10, tmp answer kept in review-v2-fable.txt)
All eight points adopted; the sections below are the revised design.

## Event register (fixed before any reaction data)
lab/mood/civ_candidates.md + civ_verify_b.tsv (compiled 20-21.10 by toll, not by mood). Included: an official toll
(governor, regional HQ, head of district or federal official) of >= 4 civilians within 72 h of the first statement;
rescuers counted as civilians (governor's own wording, NGE method); Kirov at its corrected 5; Moscow obl 17.05 out
(official 3). Excluded: another included event in the same region in the previous 14 days. Belgorod: before the
freeze, walk the governor's channel, plus the regional HQ where it posted that day, for every baseline day of the kept Belgorod events; a baseline day with
an official toll >= 4 removes that event (toll data only, blind). Secondary analysis without Belgorod.

## Clock
Hour 0 = timestamp of the first official death statement (civ_verify_b.tsv, or the official post found the same
way for events not yet verified). Event block = hours 0..24; baseline = the 14 preceding 24-hour blocks.

## Channel per region (fixed before any reaction data; revised 24.10 20:20Z, #499)
Source: telemetr.me regional catalog, first page (open to all, 10 channels by subscribers), read 2026-10-24, raw HTML
in ratings/2026-10-24/, table channels-v2-telemetr.tsv (telemetr_regions.py). livedune lacked 4 regions; tgstat 403
(not bypassed). Pick, mechanically (pick_v2.py, output pick_v2.txt): walk down by subscribers, first channel that
has the telemetr category "Новости"; is not a community page ("Подслушано" category or name, "Типичный" name); is
not an alert feed ("БПЛА", "Оповещ", "тревог" in name); is not a person's blog ("Авторский блог"); is not a federal
franchise (Mash, Baza, Shot, RIA/TASS regional); covers the region (a channel named for the regional capital counts;
one named for another city does not; for Moscow obl one named for Moscow city does not). No qualifying channel on
the first page -> the region's events drop out of v2, reported. Then the existing check: the channel's reaction set
on posts in blocks -21..-15 must include an alarm emoji, U+1F631 or U+1F628 (set only, no counts), else the next eligible channel.
Second review (Fable, 24.10 20:20Z), all adopted: "Радар" and "оператив" added to the alert-feed filter (the Радар
chain tracks drones); franchise list in code; all 10 rows printed with the eligible order.
Picks 24.10 (pick_v2.txt): Smolensk Инцидент; Bryansk Город Брянск; Belgorod Чё в Белгороде? (only eligible); Crimea
ЧП / Крым; Ryazan Рязань Читает; Tambov Новости Тамбова и Области; Kirov Киров без цензуры; Rostov Privet-Rostov.ru;
Krasnodar Краснодар и край; Tatarstan Казань на максималках; Moscow obl none (event 13 drops).
Ranking date: the ranking is read after the events (Feb-Oct 2026), so channels that grew on strike coverage may be
favoured. No pre-event copy exists (Wayback CDX holds only the catalog index, 2025-09, no region pages). Stated as a
limitation; robustness: the same test on the second eligible channel per region (pick_v2.txt), reported beside the
primary whatever it shows.
Fear-emoji check: blocks -21..-15 of the region's first included event.
Coverage per event: an event whose block 0 holds zero strike-regex posts on the channel is "not covered" and dropped
before any reaction is read (manipulation check with a consequence).
Usernames: telemetr hides them; resolve each by name on t.me before the freeze, with evidence (title and link).

## Coverage and minimum (zenith 101711, 24.10)
- Fetch coverage: a channel's fetch must contain a post older than the start of block -29 (placebo's oldest baseline
  block), else re-fetch before anything is read. v1's 14-day windows (Omsk 24.09, Ryazan 01.10) were a pager stopping
  one day short, not quiet days. A block with zero posts after a complete fetch is reported as empty, never dropped silently.
- Minimum: the test is read only if >= 2 events enter the statistic, after the coverage, floor and block-0 drops (smallest exact p with one event is 1/15 = 0.067);
  with 0-1 events it is reported as "not testable", not as a null. Same minimum for the placebo, whose floor is counted over
  blocks -29..-16 (same posts rule); an event whose block -15 is missing drops from the placebo, reported.

## Measure
- posts classified BEFORE reactions are read, by a frozen regex (strike words: погиб, удар, БПЛА, беспилот, дрон,
  ракет, атак, обстрел, ВСУ, ранен, траур, соболезн, ПВО, сирен, укрыти, взрыв, прил[её]т);
- the regex runs on the text with the channels' promo footer removed: FOOTER = `вс[юя] информаци[юя] (по|об) (атак|бпла)[^\n]*`
  (case-insensitive; Rostov "Всю информацию по атакам на Ростов и область публикуем тут — max.ru/...", Krasnodar
  "Вся информация по БПЛА / об атаках на край ... в MAX"). Without it 609 of 1418 Rostov posts and 88 of 3526 Krasnodar
  posts match only through the footer, and the footer's use changes over time (MAX migration), so it would move posts
  between cells by date. A post with no strike word and under 30 letters after removing the footer, URLs and @handles
  is excluded from both cells (footer-only promos);
- classifier check before freeze (27.10, regex_v2_sample.py seed 20261027, 50 posts, text only, hand labels in
  regex_v2_labels.tsv written before regex_v2_check.py was run on them; output regex_v2_check.txt): 14 labelled S: 12 matched,
  2 were footer-only promos removed by the exclusion rule (their S label came from the footer text); 3 false matches (criminal "смертельный удар", a WWII veteran's "ранения", Iran's threat of "ударов"),
  False matches only remove ordinary posts from the primary cell (3 of 36 here);
- primary cell = posts NOT matching; strike posts are a manipulation check only;
- block value = sum of fear reactions / sum of all reactions over the block's posts with >= 30 reactions;
  fear split: alarm = U+1F631 😱 and U+1F628 😨 (primary), grief = U+1F622 😢 and U+1F62D 😭
  (secondary); every other reaction, custom emoji included, is non-fear and counts in the denominator.
  Secondary: block value = grief / all reactions, same posts, same test and placebo, own floor >= 50 grief reactions
  over the 14 baseline blocks;
- floor (computed before the event block is extracted): >= 50 alarm reactions over the 14 baseline blocks, counted over
  the same posts that enter block values (primary cell, >= 30 reactions).
- FOOTER, URL, letters() and STRIKE_V2 are exactly the objects in regex_v2_check.py, frozen with this file (sha256 in
  FROZEN-v2.sha256); the main pipeline imports them, and the block-0 coverage check uses the same footer-removed
  classification. "Letter" = Python str.isalpha; URL = `https?://\S+|\S+\.(ru|me|com)/\S*|@\w+`.

## Test
Mid-rank (from top) of the event block in its 15 blocks; statistic = sum over events; exact null by convolution of
the per-event uniform mid-rank distributions (a block is missing when it has no primary-cell post with >= 30 reactions; an event whose block 0 is
missing drops, reported; an event's list is whatever blocks remain, with no minimum). One-sided p <= 0.05.
Placebo: the same statistic with block -15 as a pseudo-event in its own preceding 14 blocks; must be p > 0.05, else
no claim. Power (Fable): with K = 10 events, the most that can enter after #514 (Bryansk dropped), 80% power needs a mean event
rank of about 4.6 of 15 (normal approximation; it was 4.9 at K = 12); a null is a
bounded null ("no effect of that size"), not "no effect".

## What it cannot say
Reaction mix is a channel's readers, not the region; admins set the emoji; counts are final (old posts), so age is
uniform within a window. Non-strike posts on the day may still be read in the shadow of the news; that is the
point of the cell, not a confound.

## Pre-freeze results (27.10 ~19:35Z; toll and coverage data only, no reaction read)
- Belgorod baseline walk (#500, belg_baseline.py -> belg_baseline.txt): event 9 kept; 14 (baseline days 07-28, 08-02
  at toll 4), 18 (08-09) and 20 (08-25) dropped. Event 9's baseline (07-06..07-19) rests on the governor channel walked
  post by post, and (27.10 ~21:00Z) on the opershtab walked back to 07-04 (lab/mood/belg/opershtab_early.jsonl, 506 posts;
  scan in belg_op_event9.txt): no baseline day has an official toll >= 4 (largest 2 on 07-06, where the scan prints 3 because it counts "двое получили ранения"; the "6" on 07-08 is a weekly
  summary, not a day toll). Event 9 stays.
- Fetch coverage (#514, data_v2/coverage.tsv): all 11 windows reach their start (oldest post before hour0 - 30 d).
  Bryansk br_gorod: 0 posts in its window (newest fetched post 2026-01-27) -> blocks empty, reported, not dropped
  silently. Checked: br_gorod is the pick ("Город Брянск", usernames-v2.tsv) and is alive (posts 27.10), but its public
  preview holds no post between id 47985 (2026-01-28) and ~50688 (2026-04-21): t.me/s/br_gorod?before=48500, 49300,
  50000 and 50600 all return 47961-47985. Deleted or hidden, not quiet. By the coverage rule (block 0 without a strike
  post = not covered) the Bryansk event drops before any reaction is read. Ryazan: 15 posts in 32 days.
