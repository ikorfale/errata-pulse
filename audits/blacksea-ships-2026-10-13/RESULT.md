# Result, 13 Oct 2026 (errata). Guess: GUESS.md, written before the ledger was collected.

Ledger: 64 named incidents, 1 Jun - 13 Oct 2026 (ledger.jsonl; collected by a helper model from press reports, then
spot-checked by me: Gas Lisbon and Christiana B re-found in independent sources; two sources added).

| guess | outcome |
|---|---|
| share off NATO coasts in Jun-Sep <= 20% | held on paper (3 of 56 = 5%), but the share is meaningless: the Russian side is undercounted ~5x (about 300 claimed, unnamed hits). Counts only. |
| "wrong if Jun-Sep already has several NATO-EEZ strikes" | **partly wrong**: July had 3 (Gas Lisbon 21.07 and Christiana B 23.07 about 20-22 nm off Sfantu Gheorghe, Romania; one single-source tanker position north of Turkey). |
| October >= 4 strikes in NATO EEZs | held: 4 incidents, 5 ships, 3 sunk (Royad Mammadov, Alfa Watan, Azov Concorde). No ship sank in a NATO EEZ before October. |
| distance shrinking (70 nm on 6 Oct -> 17 nm on 13 Oct) | **wrong as a trend**: the July hits off Romania were already ~20 nm out. The 13 Oct hits are as close as July's, not closer. |

What the ledger shows instead (reviewed by a second model, which caught my miscount 5 -> 4 and the missing control):
- It looks less like a zone creeping toward NATO coasts than like the Danube trade. Of 7 NATO-EEZ incidents, 4 (5 ships)
  were on voyages to or from Danube ports (Reni, Izmail, Sulina, Galati, Giurgiulesti); one more (Christiana B) was
  carrying coal to Ukraine, Danube- or Odesa-bound; two have no known route (Azov Concorde; a single-source tanker
  north of Turkey).
- Geography carries most of it: all three Romanian hits sit off Sfantu Gheorghe, water used by Danube- and Odesa-bound
  ships, north of Constanta's approach. The Bulgarian hits are on water shared with Constanta, Varna and Burgas
  traffic; there the Danube link rests on the ships' voyages alone.
- Control: no merchant ship on a voyage to or from Constanta (the largest Black Sea port), Varna or Burgas appears in
  the ledger. (One exception in spirit: the Ukrainian escort tug Tedy, hit near Odesa on 9 Sep and hit again while
  heading to Constanta.) That is
  the informative part; I have no call counts to make it a rate.
- What is new in October: Bulgaria's EEZ (no strike there before 6 Oct), frequency (4 in 13 days vs 2 confirmed + 1
  single-source in July), and lethality (3 sinkings).
- Attribution stays open: Bulgaria and Romania name no attacker; Ambrey and Zelensky say Russia for 5-6 Oct.

Limits: press-based ledger; NATO-EEZ events are likely complete (two states report them), others are not; positions on
the map for port-area incidents are drawing positions (coords_from = area-approx). build_ledger.py regenerates the
raw file without my two added sources and the place.py positions: rerun place.py after it.
