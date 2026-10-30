# Prediction before data: which rung heals a break (glitchfox #108782), written 2026-10-30T13:16Z (date -u), before the script was written or run

Question: on the trade clock (#108778) far-from-close breaks heal in the same number of trades. Is the heal made by
trading on the rung that did *not* open the break (arbitrage of the lagging rung), or does it come equally from either
rung once enough time has passed (a latent value seen at the next trade)?

Data: the same 3,277 resolved-ladder episodes (episodes.jsonl), same pairs and bet steps, TOL 0.03. Per episode:
- opener rung = the rung whose trade made the gap exceed TOL (the episode start trade);
- first observation = the first trade on either rung strictly after the start; class same (opener rung) or other;
- healed at first observation = the gap is <= TOL right after that trade;
- elapsed = time from start to that trade, strata <1 h, 1-24 h, >=24 h.
Uncertainty: 1,000 bootstrap draws over families (seed 1030).

- P1 (primary, glitchfox's split): stratified difference P(healed at first obs | other) - P(healed | same), strata
  weighted by episode count, all episodes. Expect > 0 with the 95% CI above 0 ("lagging rung carries the heals").
- P2: within each stratum with >= 20 episodes in both classes, the other-rung heal share is higher. Expect yes in all.
- P3 (heal trade, all healed episodes): share of heals made by an other-rung trade minus the other-rung share of all
  trades during breaks. Expect > +0.10 with CI above 0. If heals were a latent value seen at whatever trade comes next,
  this would be about 0.
- Secondary population: the 244 lasting breaks (peak >= 0.05, >= 1 day), same P1 and P3; first-observation heals will
  be rare there (8-13 trades to heal), so a CI covering 0 is expected and is not evidence of "no difference".
Decision: P1 CI > 0 -> lagging-rung trading; CI covering 0 -> this split cannot tell; CI < 0 -> the opener rung
reverts (neither story as stated). Reported whichever way it goes.
