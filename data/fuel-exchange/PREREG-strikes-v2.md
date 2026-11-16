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
