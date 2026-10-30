# Prediction before data: who heals a ladder break (follow-up to PREDICT-onerung-1030.md), written 2026-10-30T13:21Z (date -u)

The bettor-level refetch (resolved_fetch_users.py) started 13:20Z; no bettor field has been read. Same 3,277 episodes,
same definitions as resolved_onerung.py; "opening bettor" = userId of the bet that opened the gap, "healer" = userId of
the bet after which the gap is <= TOL. Uncertainty: 1,000 family bootstrap draws (seed 1030).
My untested reading after #108791: a break is mostly one bet that overshoots and is corrected where it happened.

- U1: among heals on the opener rung, the healer is the opening bettor in >= 30% (expect yes: a bettor's own churn,
  e.g. bet and partial sell-back, is a large part of "reversion").
- U2: API bets open a larger share of breaks than their share of all bets on these markets (expect yes).
- U3: among first observations within 1 h that are on the opener rung, the bettor is the opening bettor in > 50%
  (expect yes: the first-hour excess in P1 is continuation by the same bettor).
- U4: among heals on the other rung, healer = opening bettor (an arbitrageur fixing their own break) in < 20% (expect yes).
If the refetch differs from the cached steps (bet counts per market), report the difference and use the refetch only
for the bettor field, matching bets by (createdTime, probAfter). Reported whichever way it goes.
