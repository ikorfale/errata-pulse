# validation_2024_25.jsonl: sources

This dataset pairs Houthi claims that name a ship with anonymised UKMTO incidents, covering the Red Sea crisis in 2024–2025. It was built on 2026-10-18.

It has 118 lines: 57 `pair`, 35 `ukmto_only` (distractors) and 26 `claim_only`.

## Where the data comes from

**Candidate list:** the Wikipedia article "Houthi attacks on commercial vessels". I used its raw wikitext, specifically the "List" table and its citations: https://en.wikipedia.org/wiki/Houthi_attacks_on_commercial_vessels

**UKMTO (ukmto.org):**
- **Incident warning PDFs** (`/-/media/ukmto/warnings/indian-ocean/<year>/<mon>/...`). These give the incident number, date and time, and the position text exactly as UKMTO wrote it. UKMTO updates sometimes add vessel type, flag or outcome. The 2024 index is at https://www.ukmto.org/indian-ocean/ukmto-products/warnings/2024.
- **UKMTO weekly and monthly summaries.** These list the ship's name and IMO next to the incident number. Most `ukmto_lat`/`ukmto_lon` values come from these summaries.
- **JMIC partner products hosted on ukmto.org** (InfoNotes and weekly dashboards). These cite the UKMTO incident number together with the ship name. Some copies are mirrored on sccd.royalnavy.mod.uk and hellenicshippingnews.com.

**Official statements:** CENTCOM press releases on centcom.mil, and EUNAVFOR Aspides as reported by gCaptain.

**Wire services and press** (for the Houthi claim and the ship's identity):
- Reuters, AP (via Times of Israel and ABC), BBC, NYT, Al Arabiya, Arab News
- Jerusalem Post, Xinhua, CGTN, Dawn, Tribune.pk, Yemen Monitor
- Lloyd's List, Maritime Executive, MarineLink, Marine Log, Container News, Safety4Sea, Seatrade, Baird Maritime, Professional Mariner, Steamship Mutual, defenceWeb

**Per line:** each line lists its exact source URLs in `sources`. For `pair` lines, the first source is the one that links the UKMTO incident to the ship.

## How the lines were built

- **Pairs:** a line is a `pair` only if a source explicitly ties the UKMTO incident (its number or position) to the named ship. The ship's name next to the incident number in a UKMTO summary or JMIC note counts. So does a news report that quotes UKMTO's position and names the ship.
- **Positions:** taken verbatim from UKMTO. `ukmto_lat`/`ukmto_lon` are filled only where UKMTO or JMIC gave coordinates themselves (26 of the 57 pairs). Nothing was geocoded from position text.
- **`ukmto_area`:** assigned by the researcher from UKMTO's position text or coordinates. This is a judgement call near the Bab el-Mandeb boundary.

## Known weaknesses

- **Weak links:** Chem Ranger (18 Jan 2024) rests on Ambrey's description plus "UKMTO reported an incident in the same area". Amjad (`ukmto_only`) was matched on time only. Mount Fuji was matched on date only, and JMIC's and UKMTO's positions for it disagree.
- **Incomplete distractors:** the `ukmto_only` lines do not exhaustively cover ±3 days around every pair. Thin spots are March 2024, late August 2024 (incidents 113, 114 and 116) and 2025.
- **Unchecked claims:** some distractors carry a ship name but were not exhaustively checked for a Houthi claim (Lila Lisbon, Seajoy, Lavender, Anya, Minoas, Agios Nektarios 1). Wind was demoted to `ukmto_only` because no claim naming it was found.
- **`claim_only` coverage:** this is a sample, not complete. Several lines rest on the absence of a matching incident in the UKMTO summaries that were read, or on a denial by CENTCOM, the owner, or Lloyd's List.
- **Repeated ships:** some ships appear in several `pair` lines because UKMTO logged separate incidents or positions: Hope Island, Norderney, Transworld Navigator, Groton (three lines) and Anadolu S.
- **Missing claim date:** Pumba has a known claim but no confirmed claim date (null).
