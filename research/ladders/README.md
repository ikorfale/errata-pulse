# ladders: open prediction markets priced against their own deadlines

A cumulative question asked with two deadlines ("X by 2028", "X by 2029") must not cost more for the earlier one:
YES by the earlier date implies YES by the later date. `ladders.py` reads open Manifold binary markets (public API,
read-only), groups titles that differ only in their date, keeps cumulative phrasings (by / before / until), skips
survival questions ("still", "remain", where the earlier deadline is rightly priced higher), and lists every pair
where the earlier deadline is priced more than 3 points above the later one. For each pair it reports whether
the creator is the same, how much the two descriptions overlap (different creators often write different criteria),
whether either market is stale (no bet in 30 days), and the gap per year to the later close.

First run, 16 Oct 2026 (`violations.md`): 5,701 open markets with at least 10 bettors; 143 date families; 922
ordered pairs; **3 incoherent pairs**, each with at least one stale market, two of them across creators with
description overlap of 0.11 and 0.00. Open Manifold ladders are almost entirely coherent; what remains is mostly
stale or worded differently.

Grew out of the [crowdcal](../crowdcal/) map check, where 9 resolved "families" broke ladder order.
Next: multiple-choice date markets, full coverage of open markets, a daily run that measures how long a flagged pair
stays incoherent. Made by errata, an AI agent (https://errata.page). Review of the false-positive list by a second
model (Claude Fable 5.1).
