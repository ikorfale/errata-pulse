# Governors on Max and Telegram, three weeks of 2026 (data: IONAFLOW, https://ionaflow.com)

Raw daily post counts per head of region on Max and on Telegram for 6-12 Apr, 15-21 Jul, 24-30 Oct 2026,
collected and sent by IONAFLOW (Timur Olevskiy, 03.11.2026). Matching by name, analysis: errata. Not published
yet: sent to IONAFLOW for comments first (promised 04.11).

Validation: for 20+ channels in my own t.me/s collection the IONAFLOW Telegram weekly counts agree within ±2
(Gusev 31/31, Moor 18/18, Sobyanin 23/23 and 37/37, Kovalchuk 46/46, Shuvaev 31/31). One clear gap: Leningrad
(Drozdenko) IONAFLOW 0 vs mine 33 (Apr) and 26 (Jul) -> excluded from the Telegram side.

Corrections from IONAFLOW (letter 07.11, all four questions answered; applied in crossref.py DROP and shift.py):
- Leningrad (Drozdenko): Telegram channel changed address and was not collected -> Telegram is missing, not zero.
- "Kurinny" on Max (183/186/313 posts) was a Vedomosti channel mislabelled as Ulyanovsk governor -> removed everywhere.
- Samara (Fedorishchev): Telegram not posting 22.05-05.09 (July zero is real); monitoring paused 20.08, so the October
  Telegram count is missing -> Samara removed from the October comparisons.
- Belgorod (Gladkov): governor until 13.05 -> April kept, July and October removed.
IONAFLOW cannot backfill periods when a source was not collected; the gaps stay gaps.

Result (80 governors listed on both platforms, Leningrad excluded; October n=79 without Samara):
- Max/Telegram post ratio: 1.11 (Apr) -> 1.18 (Jul) -> 1.17 (Oct; 1.19 before the Samara correction). Telegram volume flat (1621, 1657, 1630).
- About half (32-38 of 76-80 active) publish exactly the same number of posts per week on both: mirroring.
- Max-heavy (Max >= 1.5x Telegram): 5 -> 10 -> 9 (Samara out in Oct). Telegram-heavy: 1 -> 1 -> 0.
- Paired Apr->Oct (n=73): median change in Max/TG ratio 0.0; 21 up, 15 down, 37 flat.
- Max-only in October: Oryol, Pskov (both left Telegram end of March, Kommersant 09.04), Zabaikalye (no Telegram
  channel listed). Samara was Max-only in July (real Telegram silence); its October Telegram count is unknown.
- Telegram-only: Moscow (Sobyanin, no Max channel in the list).
Reading: the move to Max is an addition, not a migration. Exits are a handful of named governors, mostly done by April.

Earlier questions to IONAFLOW (Leningrad, Kurinny, Samara, Gladkov): answered 07.11, see Corrections. Scripts: crossref.py, shift.py; table: per_governor.csv.

Scope note (IONAFLOW, 07.11 15:13Z): law-enforcement bodies (Prosecutor's Office, Investigative Committee, MVD)
reportedly have a larger presence on Max than on Telegram, some Max-only. Not measured by me; publish as their
observation and state "governors only" up front. Asked for same-week counts for those bodies.
