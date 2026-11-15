# Prereg: refinery strikes vs exchange gasoline volume (task #756)

Written 2026-11-15 12:19 UTC, BEFORE any weekly strike count was made. I have already seen the volume
series (series.csv), so this is not blind on the outcome side. It is blind only on the predictor side.

## Question
Do weeks with more confirmed drone strikes on Russian refineries come before weeks with lower per-session
exchange sales of AI-92+95 (Reuters/SPIMEX definition)?

## Predictor (counted after this file is committed)
S(w) = number of distinct refineries with a strike confirmed by an official (governor, ministry, company) or by
two independent outlets, in the calendar week Mon-Sun ending before the trading week w starts (lag 1 week).
"Claimed only" goes into a separate S_claimed and is not used in the main test. Sources: my events.jsonl from
October; for Jul-Sep, Reuters/Kommersant/independent media weekly roundups. Every count line keeps its source URL.

## Outcome
V(w) = total_t_per_session from series.csv, rows kind=week, Reuters definition only. The 21-25 Sep NBCA row
(different definition) is excluded from the main test and shown separately.

## Test
Spearman rho(S, V) over all weeks with both values. Prediction: rho < 0.
Main verdict: "supported" only if rho <= -0.5 AND the sign holds when any single week is dropped (leave-one-out).
"Not supported" if rho > 0. Anything between = "inconclusive". With n about 6-12 weeks this can only detect a
strong link; a null is NOT evidence of no link and will be reported as low power, with the n.

## Rivals named before looking
1. Off-exchange rule (10% norm, 8 points via addressed deals since 1 Jul): constant across all weeks, cannot
   explain week-to-week change, but lowers the level.
2. Grade migration to Euro-2/3/4 (since Sep): would lower V without fewer barrels. Check: low-grade volumes where
   published (task #759).
3. Planned maintenance and seasonal demand: note dates where Reuters names them.
4. Short weeks: already handled by per-session normalisation.

## What I will not do
No change of lag, of the window, or of the strike definition after seeing S. If I try another lag, it is labelled
exploratory and is not the verdict.
