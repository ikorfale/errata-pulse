# Strike-report filter: holdout check (written 2026-10-10 03:40 UTC, before any holdout data)

In-sample audit (2026-10-10): 70 site-days from pulse/strikes/history.jsonl (2026-09-01..10-09); the first post of each
read by hand: 33 report a new strike on that site (NEW), 24 are about an earlier one (FOLLOW), 13 are not about a
strike on that site (FALSE). The published 7-day card averaged 7.45 sites where NEW-only gives 4.55 (corr 0.66).

Change to tools/strike_signals.py (same day): a site needs a strike word within 80 chars (on top of the facility
word within 250), and a post whose every "night of <date>" is 2+ days old is not counted. In sample: NEW 33/33 kept,
FALSE 13 -> 6, FOLLOW 24 -> 17. Widths 40/60/80/100 were tried; 80 chosen as the narrowest that kept all NEW. A
general "any date 2+ days old" rule was tried and rejected (it dropped 2 NEW). This is tuned on the same data.

Holdout: every site-day the NEW collector counts from 2026-10-10 to 2026-10-23, plus every site-day the OLD rule
would have counted (the pre-change script is kept as lab/strike-audit/old_strike_signals.py).
Judge each post by hand BEFORE looking at which rule kept it (shuffle, hide the rule column).
Success: the new rule keeps >= 90% of NEW site-days and drops >= 40% of FALSE ones. Otherwise revert or redesign,
and say so in the Pulse report that uses the strike card.

## Amendment 1 (2026-10-24 ~00:50 UTC, before any holdout text or rule column was seen; second-model review)

The holdout rebuild (holdout_run.sh) is running; no sheet exists yet.

- **Unit and label.** Universe = every (date, site) the OLD rule counts in 10-10..10-23. Each is labelled by a blind
  verdict on OLD's first URL, exactly as in-sample. Kept = NEW counts that (date, site) under any URL.
  Keep ratio = NEW-labelled site-days NEW counts / NEW-labelled site-days. Drop ratio = FALSE-labelled site-days NEW
  does not count / FALSE-labelled site-days. Site-days NEW counts and OLD does not should not exist (NEW only tightens);
  their number is reported and they are excluded. Verdicts on NEW's own first URL, where it differs, are judged in a
  second sheet only after the primary verdicts are committed, and are diagnostic only (never in the ratios).
- **Blinding.** Primary sheet: one item per OLD site-day, shuffled, showing date, site and FULL post text only (no URL,
  no message id, no rule). The key (urls, new_counted) is written to a separate file opened only after the verdicts
  file is committed.
- **Definitions and tie-breaks.** NEW: the post reports an attack on that facility on its date or the night before.
  A post with no explicit date that reports an attack (hit, fire, drones over it, "debris fell on") in the present or
  just-past and is not plainly a recap counts as NEW. FOLLOW: about an earlier attack on that facility (aftermath,
  repair, stoppage, recap, satellite images, a dated night 2+ days back). FALSE: not about an attack on that facility
  (facility named only as a location or landmark, regional list without that facility hit, pipeline route, fuel
  market, unrelated). Borderline calls are flagged while blind.
- **Missing text.** Fetch retried once; still empty or an error = excluded and counted, never labelled from memory.
- **Reporting.** Each ratio as k/n with a Wilson 95% interval; FOLLOW counts and a NEW+FOLLOW keep rate as a
  sensitivity; number of distinct sites. The decision stays on the point estimate (as above). Wording: "pass,
  confirmed" if point and lower bound clear the threshold; "pass, not confirmed" if only the point does (then say
  what the interval rules out); "fail" if the point is below (revert or redesign, as registered). With ~10 FALSE
  site-days the drop ratio will almost surely be "not confirmed".
