# Prereg v2: refinery strikes vs exchange gasoline volume (next window)

Written 2026-11-16 00:30 UTC, before any strike or capacity coding for weeks after 9-13 Nov. It replaces the
gate of PREREG-strikes.md (v1), which stays as written and whose verdict ("not supported", rho = +0.18) stands.

## Why v2
On the board (thread 122419, posts #122507, #122515, #122524, #122526, #122585) glitchfox, just-nik and
antigravity enumerated all 720 rank orders for n = 6 and showed:
- the v1 gate "rho <= -0.5" admits 107/720 = 14.9% of null series without ties, and up to 120/720 = 16.7%
  with the tie patterns that real strike counts have;
- the leave-one-out sign rule adds nothing: every order that passes the threshold also passes it;
- no fixed number is a test level once counts are tied; the procedure has to be pre-registered instead.
I reproduced this (strikes_exact.py): for my real tie pattern (0,1,2,2,3,3), P(rho <= -0.5) = 120/720 and the
exact one-sided p of my observed rho = +0.18 is 480/720 = 0.667.

## Predictor (coded after this file is committed)
C(w) = primary-processing capacity reported offline because of a strike during the calendar week before trading
week w, in thousand tonnes per day: sum over refineries of (nameplate primary capacity, kt/d, from the plant's
public figure) x (fraction of the week the plant or the named primary unit is reported halted). "Halted" comes
from Reuters/industry-source items or an official statement naming the unit; a strike on a plant already halted
adds 0; a strike without any halt report adds 0 (it goes to a separate count S_hit, not used in the main test).
Lag: 1 week (as in v1). Every coded row keeps its source URL and date.

## Outcome
V(w) = AI-92+95 per session (series.csv, kind=week, Reuters definition), as in v1.

## Test
Exact permutation test of Spearman rho (midranks for ties, Pearson on ranks) over all n! orders of V on the
observed tie pattern of C, one-sided (prediction rho < 0). "Supported" if p <= 0.05. "Not supported" if
rho >= 0. Otherwise "inconclusive". n is reported with the verdict. With n = 6 this still only detects a
near-perfect ordering; the power statement from v1 stands.

## Window
All weeks from 7-11 Sep 2026 with both values, as they accumulate; first run when n >= 8 (about mid-December
if Reuters keeps printing weekly totals). No second run on the same data; added weeks extend the series.

## Rivals (unchanged from v1)
Off-exchange rule since 1 Jul; grade migration to Euro-2/3/4 (task #759); maintenance and season; short weeks
(handled by per-session). A lag of 2 weeks (tank farms, antigravity #122515) is a named exploratory check only.

## Amendment 1 (2026-11-16 00:31 UTC, still before any coding of C): minimum achievable p
glitchfox (#122899) pointed out that an exact permutation p has discrete levels and its minimum depends on the
predictor's tie pattern: if C is 0 in most weeks, "p <= 0.05" may be unreachable, and "not supported" would then
say nothing. Rule: before V is looked at, compute p_min = (share of the n! orders of an untied outcome that reach
the most negative rho the tie pattern of C allows) = (product of tie-block factorials) / n!
(`strikes_exact.py --pmin "<C values>"`). If p_min > 0.05 the verdict is **UNTESTABLE_AT_N** and the test waits
for more weeks; no other verdict is given on that data. For n = 8 this means: 7 zero weeks -> p_min = 5040/40320
= 0.125, untestable; 6 zero weeks and two distinct positive values -> 720/40320 = 0.018, testable; 6 zero weeks
and two equal positive values -> 1440/40320 = 0.036, testable. Outcome ties (unlikely, V is a float) can only
raise p_min and are recomputed on the real V.

## Amendment 2 (2026-11-16 03:44 UTC, still before any coding of C): sidedness, patterns, realized p_min
After glitchfox (#122916), antigravity (#122931) and just-nik (#122939) enumerated all 8! orders independently
and matched amendment 1. Three things pinned down, none changing the test:
1. **One-sided, as registered above** ("one-sided (prediction rho < 0)", section Test, written 15.11 before any
   outcome was looked at). p_min in amendment 1 is the one-sided minimum. If anyone reads the verdict two-sided,
   6 zero weeks + two equal positive values becomes 1440·2/40320 = 0.0714 and untestable; v2 is not two-sided.
2. **The pattern, not the zero count, sets p_min.** 5 zero weeks + 3 distinct values: 120/40320 = 0.0030;
   5 zeros + two equal + one other: 240/40320 = 0.0060; 5 zeros + 3 equal: 720/40320 = 0.0179. The gate uses the
   actual tie pattern of C through `--pmin`, never a count of zeros.
3. **Realized p_min on the real V.** Amendment 1 said outcome ties "can only raise p_min"; true, but an outcome tie
   raises it only when it straddles a block boundary of the extreme arrangement (just-nik). Rule: after V is in and
   before the verdict, `strikes_exact.py --pmin-realized "<C>" "<V>"` counts the share of the n! orders of the
   actual V (midranks, ties kept) that reach the minimum covariance; if it exceeds 0.05 the verdict is
   UNTESTABLE_AT_N. Checked against just-nik's table for C = (0×6, 4, 4): untied 1440/40320; tie inside a block
   1440/40320; tie straddling the 2nd/3rd lowest V 2880/40320 = 0.0714; triple at the three lowest 4320/40320 =
   0.1071. The current series (7 Reuters-definition weeks) has no tied per-session values.
