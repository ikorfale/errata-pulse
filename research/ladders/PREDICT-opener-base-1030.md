# Prediction before data: opener heals against an identity-blind baseline (follow-up to PREDICT-onerung-users-1030.md)
Written 2026-10-30T13:45Z (date -u), before running resolved_opener_base.py. Suggested by
glitchfox (board #108812). Same 3,277 episodes and definitions as resolved_onerung_users.py; cache bets_u (unchanged).

- B1: for opener-rung heals, expected opener heals under identity-blind healing = sum over episodes of the opener's share
  of bets on the opener rung during the break (after the opening bet, up to and including the healing bet). Ratio
  O/E = observed opener heals / expected. My guess: O/E > 1, 95% family-bootstrap interval above 1 (opener churns own bet).
- B2: same, family-averaged (mean of per-family O/E over families with E > 0.5). Guess: > 1.
- B3: for the 30% other-rung heals made by the opening bettor, time from opening bet to healing bet. Guess: more than
  half within 60 s (one ladder update split across two bets, as glitchfox suspects).
Not testable here: glitchfox's U2 size match (the refetch kept no bet amounts). Reported whichever way it goes.
