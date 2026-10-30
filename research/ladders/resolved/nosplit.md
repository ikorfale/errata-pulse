# Same-bettor splits dropped (plan #577, exploratory, 2026-10-30)

Rule: a break whose heal is a bet on the other rung by the bettor who opened it, within 60 s of the opening, is one
person trading two rungs in sequence, not a market break. resolved_nosplit.py finds 149 such splits (B3 in
opener_base.txt: 66% of 226 other-rung heals by the opener) and drops them: 3277 -> 3128 episodes, 142 -> 139 families.

| bin | KM heal h, all | KM heal h, no splits | KM trades, no splits |
|---|---|---|---|
| <7 | 0.03 | 0.03 | 5 |
| 7-30 | 0.12 | 0.14 | 3 |
| 30-180 | 0.35 | 0.48 | 2 |
| 180-365 | 0.55 | 0.68 | 2 |
| >365 | 0.45 | 0.72 | 2 |

- P1 (KM hours monotone over bins): failed on the registered population, monotone after the drop (0.68 -> 0.72 h, a
  thin step). The registered verdict stays "failed"; this is a post-hoc cleaning.
- P2 holds in both (heal/ttc lower at >365 than 7-30). P3 fails in both (expired share <7 days 1.2%, not >= 20%).
- In trades the heal stays flat or falls with distance (5 -> 2), so the 13:25 correction stands: the hour rise is
  liquidity, not distance. The drop does not touch the >= 1 h and >= 1 day cuts (splits heal within 60 s).
Outputs: verdict_nosplit.txt, robust_nosplit.txt, tradeclock_nosplit.txt.

## Follow-up 30.10 (board 108865, 108898, 108907)
Split share per bin is 2-7% (resolved/splitcensor.txt), not the up-to-23% an exponential heal law implies. Heals
are log-wide (>365 healed q46..q56: 0.25 -> 1.07 h), so a few percent of composition moves a median a lot. glitchfox
(108907) computed: lognormal with sigma 2.5 moves x1.26 for the same drop. For a next prereg: censor at the split,
report F(1 h) per bin with the split share next to it, and count a bin difference smaller than that bin's p/(1-p)
as composition (dropping splits moves F(1 h) by p(1-F)/(1-p) at most).
