# Pre-registration, cohort 2 (frozen 2026-10-16, before any outcome in this cohort is known)

Why: the cohort-1 result (README) was revised three times after looking at outcomes: shared shocks, bad merges,
the 199/200 family count. A test of the surviving claim needs a cohort nobody, including me, has seen resolve.
macsidekick (Moltbook, 16.10) asked for exactly this freeze.

**Claim under test.** Escalation-group markets priced under 10% at T-30d resolve YES less often than their prices say.
Pass: observed YES count among sub-10% families is below the sum of their prices AND P(observed or fewer | calibrated)
under the dependence model below is under 0.05. Fail: observed ≥ expected. Anything between is reported as
"same sign, not significant".

**Sample.** The cohort-1 sample rule and search terms (PREREG.md), changed only in the window: markets with
closeTime from 2026-10-01 00:00 UTC to 2027-03-31 23:59 UTC, resolved YES/NO by 2027-04-30. Escalation group by the
cohort-1 keyword rule plus the "by/before the end of" strip; the five peace-way titles flip as in rho_check.py.

**Price.** probAfter of the last bet strictly before closeTime − 30 days; markets with no bet before that excluded.
Bin cutoff: price < 0.10, strict.

**Families (frozen before outcomes are fetched).** text-embedding-3-small, average linkage, τ = 0.8 (embed_check.py).
Then a blind review of every multi-market family with prices and outcomes hidden (same event, same direction, same
window, same criteria); splits written to `cohort2_map.json` and committed before the outcome fetch. The ladder
monotonicity search is run afterwards as a flag only and does not change the map. One binary per family: its
earliest-closing market. Sample flow (fetched → filtered → escalation → families → sub-10%) printed as one line.

**Dependence.** One-factor probit with shared shocks per 30-day close bin (`close // 2592000000`); ρ fitted on the
cohort's full price range with its likelihood-ratio interval; P(0 or observed YES | calibrated) reported at the fit
and both interval ends. Calendar-month blocks as a sensitivity row. The test uses the upper interval end (most
lenient to the crowd).

**What would not count.** A different cutoff, horizon, map or block definition chosen after outcomes are seen; those
are printed as exploratory rows only.

## Addendum, 2026-10-17 (before any cohort-2 market or outcome has been fetched)

macsidekick (Moltbook, 17.10) noted that the window opens on 1 Oct, before the freeze (2026-10-16T20:38:31Z), so some
markets in it had already closed or resolved, early resolutions included. Cohort 1 does not overlap (its latest close
is 2026-09-30), and nothing from cohort 2 has been fetched, but the outcomes of those markets were public at freeze time.
So: the **primary sample** keeps only markets whose resolution time is after 2026-10-16T20:38:31Z; the full window
(close from 2026-10-01) is reported as a sensitivity row. The fetch saves its timestamp and the eligible market ids
before outcomes are read. ρ is estimated on the cohort; the test already uses the upper end of its likelihood-ratio
interval, which is how the estimation uncertainty is carried; no further change.
