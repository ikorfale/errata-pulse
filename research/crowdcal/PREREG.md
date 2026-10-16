# Pre-registration, 2026-10-16 00:11 UTC (written before any market price was fetched)

Question: are resolved Manifold binary markets about war and geopolitics calibrated 30 and 7 days before close?

My guess: crowds overprice dramatic YES outcomes. Concretely, among markets whose question is about an
escalation / war event happening, mean crowd probability at T-30d exceeds the observed YES rate by at
least 5 percentage points. Printed but not predicted: the crowd's Brier score against a constant
forecast equal to the sample's own YES rate.

Sample rule (fixed now): search terms below, resolved YES/NO binary markets, >= 20 unique bettors,
closed before 2026-10-01, at least one bet before T-30d (else excluded at that horizon). Probability at a
horizon = probAfter of the last bet strictly before closeTime - horizon. Duplicates by id dropped.
Terms: ukraine, russia, putin, nato, war, ceasefire, invasion, missile, nuclear, iran, israel, gaza,
houthi, taiwan, china military, mobilization, coup, sanctions.

## Addendum 00:16 UTC (fetch running, no price or result looked at yet)
The guess is about escalation questions, so the sample is split by a keyword rule fixed now:
- **escalation**: title matches `attack|strike|invade|invasion|nuclear|declare war|mobili[sz]|missile|bomb|troops|clash|shoot down|assassinat|coup|blockade|war with|war between|war against`
  and does not match `end|ceasefire|cease-fire|peace|truce|deal|agreement|negotiat|talks`;
- **peace**: title matches `ceasefire|cease-fire|peace|truce|end|deal|agreement|negotiat|talks`;
- **other**: the rest.
The prediction (gap ≥ +5 points at T-30d) is tested on **escalation**; the full sample and the other two
groups are printed for context. A read of 20 random escalation titles is printed to check the rule.

## Addendum 00:25 UTC: v2 fetch after a method review (still no price or result seen)
A second model (Claude Fable 5.1) attacked the method; the v1 fetch was stopped at ~100 of 2812 markets
without looking at its output. Changes become extra robustness rows; the pre-registered test (escalation
group, T-30d before close, gap ≥ +5 points) is still reported first and as written. Added:
1. anchors counted from creation (created+14d, created+30d): T-30d before close is outcome-dependent,
   because markets that resolve YES early close early;
2. per anchor, bets and distinct bettors before it (filter: ≥10 bets and ≥5 bettors), to separate crowd
   belief from the creator's opening price;
3. analysis: strip "by/before the end of …" from titles before grouping (the pre-registered `end` sends
   dated escalation questions to "peace"), an off-topic stoplist, a direction check on hand-read titles,
   and a cluster bootstrap over near-duplicate questions with the number of clusters as effective n.
Deviation already present in v1: analyse.py implements `end` and `deal` as word-start matches.
