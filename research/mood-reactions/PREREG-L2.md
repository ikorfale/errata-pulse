# Mood layer 2: do local readers react differently after a strike on their city? (draft pre-registration, 2026-10-23)

Data: aggregate emoji reaction counts on public Telegram web previews of regional news channels
(reactions_fetch.py; first channel Fontanka, St Petersburg). Aggregate only. Design reviewed by a second model (Fable, 23.10).

**Sanity check first (no strike analysis before it passes).** Two snapshots of the same posts 24 h apart (23.10 and 24.10).
Pass if: (1) the reaction set offered per post is constant over the window; (2) counts on posts older than 72 h grow
less than 5% between snapshots; (3) the day-to-day SD of daily mean distress share over a quiet fortnight is reported,
and the smallest effect I will call meaningful is set to 2x that SD *before* looking at any strike window.

**Rules.** Only posts at age >= 72 h at scrape time. Post-weighted, not views-weighted. Distress = 😱😢🤯😨🙏💔;
anger = 🤬😡👎 (🤡 excluded: brigading). Every post in D-7..D+2 is hand-labelled strike / strike-adjacent / unrelated
with the date hidden where possible; only "unrelated" posts enter the primary metric.

**Primary:** per channel-event, mean distress share of unrelated posts on D..D+2 minus D-7..D-1.
Placebo: 500 fake D from the channel's prior 180 days, weekday-matched, excluding +-7 days around any confirmed strike on
that city or a major national event; two-sided p = share of placebo differences at least as large.
Secondary: anger share, reactions per 1000 views, same statistic.

**Claims.** 3 strikes = descriptive pilot, no direction stated. A direction only after >= 10 strikes across >= 5 cities.
Pilot events: St Petersburg 18.10.2026 (Fontanka). Moscow 23.10 (Moskva Seichas) only after 26.10 (72 h age).
Channels whose preview shows no reactions (checked 23.10: moscowmap, mash_moskva, bel_novosti, kursk_ru) cannot be used.
