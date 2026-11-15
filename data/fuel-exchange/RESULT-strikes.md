# Result: refinery strikes vs exchange gasoline volume (prereg PREREG-strikes.md, committed 181afd1 before counting)

Run 2026-11-15T12:24Z. Strike coding: strikes_weekly.csv + strikes_coding_notes.md (coded by a helper agent under the fixed rules; spot-checked).

**Verdict: not supported.** Spearman rho(S lag 1 week, V per session) = +0.18, n = 6 (rule: supported only if rho <= -0.5 and sign stable leave-one-out; not supported if rho > 0).
Sensitivity (not the verdict): Novak 14.10 disputed claims dropped: rho = -0.09; anonymous Bloomberg source counted: +0.12.
The week after 3 confirmed strikes (26 Oct-1 Nov) was the strongest sales week in the series (19.2 kt/session, 2-6 Nov).

**What this does not show.** n = 6 can only detect a very strong link; this is low power, not evidence of no link.
Counts of struck refineries are not capacity offline (a strike on a halted plant removes nothing); the lag may be longer than a week;
buyers may front-run expected cuts (Reuters 06.11 described demand rising after strikes resumed). Any of these is exploratory now, not a re-test.
Full output: strikes_test_out.txt
