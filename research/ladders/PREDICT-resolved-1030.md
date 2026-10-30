# Prediction before data: resolved ladders (plan #564), written 2026-10-30T11:11Z (date -u), before any resolved market was fetched

Question (glitchfox, board 107546): does a ladder break heal more slowly when the earlier rung's close is far away?
Data: resolved_ladders.py (rules in its docstring). Bins of ttc (days from episode start to the earlier rung's end):
<7, 7-30, 30-180, 180-365, >365. Heal measured by Kaplan-Meier (expired = censored at the cut).

Caveat I know in advance: heal <= ttc by construction, so a raw correlation of heal with ttc is partly mechanical.
The non-mechanical test is P2 (heal as a share of the time left) and P3.

- P1: KM median heal rises from the <7 bin to the >365 bin (monotone over bins with >= 20 episodes). Expect yes.
- P2: median of heal/ttc among healed episodes is lower (breaks heal faster relative to time left) in the >365 bin than in
  the 7-30 bin. Expect yes: far from close, a break is a small fraction of the remaining life.
- P3: share of episodes that expire (still broken at the earlier rung's end) is >= 20% among episodes starting < 7 days
  before the end. Expect yes: last-week breaks often run out the clock instead of healing by trading.
- Minimum: >= 10 families and >= 100 episodes, else report "not enough data" and no verdict.
Any of these can fail; the result is reported whichever way it goes.
