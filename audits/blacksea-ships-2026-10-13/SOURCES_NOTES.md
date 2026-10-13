# Black Sea merchant-ship strikes, 2026-06-01 to 2026-10-13: sources and gaps

Built 2026-10-13 in about 25 minutes of web search (Parallel search). `ledger.jsonl` holds 68 lines: 64 incidents
and 4 `aggregate:true` lines for Ukraine's claimed Operation MoLoChKa totals. `build_ledger.py` regenerates the file.
Line format: one incident is one attack event. A line lists several ships when they were hit together. Lines marked
`claim_only:true` are Russian MoD claims with no named ship.

## Trackers found
- **Funnel2Tunnel "West Asia Crisis" tracker** (funnel2tunnel.com/WestAsiaCrisis, CrisisBlackSea): 67 Black Sea
  items with coordinates. It quotes UKMTO-style reports that give real lat/lon (15, 18 and 19 Jul). It is an aggregator
  and its plotted coordinates are often wrong: Golden Leo is plotted at Novorossiysk, and many items sit on round
  numbers. I used its coordinates only where the text quotes degrees and minutes. It also re-dates old events:
  - "Altura attacked off Bosphorus 2026-08-25". Altura was hit on 26 Mar and on 28 May 2026 (AP, Kyiv Post), so the
    Aug item is probably a stale copy.
  - "Virat and Kairos 2026-08-06". These look like the Nov 2025 attacks; Kairos was lying abandoned in Burgas in Aug
    2026.
  Both items are excluded.
- **Wikipedia**: "Ukrainian attacks on the Russian shadow fleet" and "Operation MoLoChKa" (claimed totals, few names).
- **Ambrey** threat circular, 6 Oct (paywalled beyond the summary): attributes 5-6 Oct attacks as "highly likely Russian".
- **UKMTO/JMIC** 2026 advisories page lists monthly counts but the PDFs were not read. That is a gap.
- **ShipFinder maritime-security alerts**: good for vessel names and MMSI (Mariam M, Lider Bordo Mavi, Aframax Rio).
- Aggregate figures for context:
  - IMEAK (Turkish Chamber of Shipping): 163 vessels attacked in Jan-Aug 2026.
  - Ukraine to OSCE: 232 civilian vessels since 2022.
  - Infrastructure Ministry: 274 vessels damaged as of Sep.
  - USF (Brovdi): 215 vessels hit in Jul, 54 in Aug, 16 in 1-11 Sep, more than 300 by 22 Sep.

## Gaps and caveats
- **MoLoChKa is not itemised.** About 285 to 300+ Russian-linked vessels were claimed hit in the Sea of Azov and the
  Black Sea in Jul-Sep. Only about 25 are named in this ledger. RU-coast and Azov counts are therefore heavily
  undercounted, and the aggregate lines should not be summed with incidents.
- **July is the densest and the most single-sourced month** (15 single-source lines). Several UKMTO-style items are
  unnamed and could duplicate named ones: the 18 and 19 Jul bulkers at about 44.8N 36.55E, and the CPC tankers.
- **Russian MoD claims** (15 Jul, 22 Jul, 10 Oct) name no ships and may overlap with incidents Ukraine reported.
  The 10 Oct claim has only a Sputnik/RIA source.
- **June is thin**: 6 incidents, Russian-side incidents mostly from Azerbaijani media.
- **September is thin**: 5 incidents. Ukraine claimed 16 hits on 1-11 Sep, and only Armada Leader is named.
- **"Attacks near Turkey in October" were not found.** Searches in English and Turkish found no October 2026 strike on
  a merchant ship in Turkish waters. The closest are the 13 Oct Bulgarian-EEZ ships, which were Turkish-owned and
  Turkish-crewed. This needs a check of Turkish-language media and UKMTO for 7-13 Oct.
- Possible duplicate not entered: Odessa Journal, 5 Oct, "cargo ship hit near Odesa drifts towards Bulgarian waters".
  It may be one of the Bulgarian-EEZ ships or a separate incident. Unresolved.
- Coordinates marked `place-approx` are my rough geocoding from "N nm east of X". They are not source positions.
- Casualty figures conflict:
  - Golden Leo: 4, 5 or 10 killed.
  - Gas Lisbon: 3 injured, or 1 later dead.
  - Tedy: 2 or 8 wounded.
  The ledger keeps the conflicts in the text fields.
- Dates are approximate (`date_note`) for Blue, Avero, Yasar, Ural, the MSC vessel, Louise 1 and Banda.
- Excluded:
  - fishing vessels (Duru 67, 5 Jun);
  - Ukrainian SAR boats (6-8 Jun);
  - Lady Mariia (Mediterranean, 6 Sep);
  - port and terminal strikes with no ship named;
  - the 10 Sep Sochi port sea-drone attack (no ship).
