# Blind recount, bridge strikes 1 Jan – 27 Sep 2026: search log

Done blind: I did not open strikes.csv, weekly.py, weekly.png or SEARCH.md.
The searches ran on 2026-11-17 through Parallel web_search (33 searches) and web_fetch (2 fetches).
Raw working notes are in `notes.txt` in this folder.

## Method and coverage

- I did not read ISW daily reports one by one. I reached them through keyword searches by month, so a bridge mention
  that sits only in an ISW endnote or in a report that never ranked in search is missed. **This is the largest
  coverage gap.**
- I could not reach Oko Gora or any other dedicated bridge tracker. I read RosHlopok (roshlopok.com) only through
  search snippets: its "Bridge" category lists 14 objects across the whole war. Its monthly totals cover all strike
  types, not just bridges.
- I did not use Rybar or Two Majors directly. Russian-side material came through RIA, TASS, Kommersant, Interfax,
  MK, Rusvesna, life.ru, 360.ru and bel.ru.
- Ukrainian MoD "middle strike" monthly summaries covered April, July, August and September. These summaries name
  the bridges each month. **April named none. September named only one.**

### Inclusion rules I applied (judgement calls)

- Excluded: pontoon bridges (e.g. 18 May, two in Donetsk; 13 Jun at Chonhar), ferries (14 Mar, Kerch), boats
  guarding the Kerch bridge (30 Apr), the Taman port pipeline trestle (13 May), and unnamed "logistics crossings"
  (1 Jul at Novoocheretuvate; Mokri Yaly in August).
- Excluded as outside the window: the Konka bridge (destroyed early 2025 and first reported Apr 2026), the
  Dyatkovo–Lyudinovo rail bridge in Bryansk (28 Sep), the Kyiv Dnipro bridges (October) and the Kerch bridge
  (16–17 Nov). **I found no strike on the Kerch bridge itself between Jan and Sep 2026.**
- One vague report naming several bridges, with no names or count, became **one** row (7 Mar, 7 Apr).
- Repeat strikes on the same bridge on different days count as separate rows.

## Month by month

| Month | Searched? | Queries / sources | Result |
|---|---|---|---|
| Jan | yes, thin | "bridge strike January 2026", "удар по мосту январь 2026", "удар по мосту січень 2026"; ISW Jan 5, 6, 13, 18, 30, 31 reached through search; EMPR daily | 2 RU, both claimed. No UA bridge strike found. The ISW Jan 13 report mentions daily Russian KAB strikes on Oskil crossings but names no single event, so I made no row |
| Feb | yes, thin | "bridge struck February 2026", "удар по мосту февраль 2026", "міст удар лютий 2026"; Vasylivka follow-up (RU/UA/EN); ISW Feb 3, 28; OSW Feb 17 | 1 UA (Vasylivka, 20 Feb), 1 RU (Kinska T-0803). OSW mentions Russian strikes on rail infrastructure but no named bridge |
| Mar | yes, thin | "bridge strike March 2026", "удар по мосту март/березень 2026", "ISW bridge March 2026 geolocated"; ISW Mar 7, 12, 18, 26; OSW Mar 10; SouthFront Mar 21; CIT sitrep Mar 13-16 | 4 RU, all claimed (two of them vague). No UA bridge strikes found; Ukraine hit the Kerch ferries instead |
| Apr | yes, thin | "bridge struck April 2026", "удар по мосту апрель/квітень 2026", "ВКС удар по мосту апрель 2026", "Генштаб уражено міст квітень", Bryansk-bridge query; ISW Apr 7, 15; MoD April middle-strike summary | 1 RU (vague, milblogger). UA: none found. The MoD April summary lists no bridges, which counts as real evidence of zero |
| May | yes, thin | "bridge strike May 2026", "удар по мосту май/травень 2026", "Генштаб уражено міст травень"; ISW May 1, 25; Interfax/Hromadske May 19 | 2 RU (Vovcha, geolocated). UA: only pontoons and a pipeline trestle, both excluded |
| Jun | yes, deep | Chonhar, Henichesk and Arabat via Saldo (RIA, Kommersant, Interfax, RIA Crimea, Tsargrad); ACLED report; Kyiv Independent; UNN; Novoazovsk; Korsak/Aidar/Luhanchyk; Rozdolne/Vladyslavivka (Wikipedia "Bridges in the Russo-Ukrainian War", Glavred); Vasylivka; Ulanove (RU MoD); ISW Jun 8, 11, 20, 29 | 27 UA (14 confirmed through Saldo or the Novoazovsk occupation mayor), 6 RU |
| Jul | yes, deep | MoD July summary (14 bridges/overpasses plus pontoons); General Staff daily reports via Suspilne, Interfax-Ukraine, LB, Babel, Defense Express, Militarnyi; ISW Jul 7; bel.ru (Kolykhalino); Forbes Jul 24 | 18 UA (16 dated plus 2 dated only to the MoD summary's publication). RU: none found. I did not search hard for Russian strikes on Ukrainian bridges this month |
| Aug | yes, medium | MoD August summary (6 bridges); General Staff via UP, ISW/CTP Aug 4, 16; Mayaky (ISW Aug 9, NV, Euromaidan); Zatoka (life.ru, 360, eadaily, ukragroconsult, ISW Aug 25); Preobrazhensky (MK, METIS) | 6 UA (plus 2 July rows carrying an Aug 10 publication date), 3 RU. Mokri Yaly crossing excluded |
| Sep 1-27 | yes, medium | MoD Sep summary; General Staff Sep 7 (Ukrinform, NV, UNN, Censor); ISW Sep 8, 11; OSW Sep 8, 15; CIT sitrep Aug 31-Sep 3; Zatoka (hamerintel, news-pravda); Kramatorsk (Rusvesna, Glavcom) | 1 UA, 7 RU, all claimed |

Cross-cutting searches: Russian governors (Khinshtein, Gladkov, Kovalchuk); Kerch bridge 2026; Zatoka 2026; Russian
strikes in Kharkiv and Sumy (Ukrainian-language queries returned only casualty reports); Russian MoD and VKS bridge
claims; the Wikipedia September 2026 timeline.

## Where coverage is weakest

1. **Jan–May, Russian strikes on Ukrainian bridges.** These turn up mostly as one-line milblogger or geolocated
   items inside ISW reports, and keyword search reaches only a fraction of them. The true count is probably higher.
   Ukrainian officials seldom name damaged bridges, and the Ukrzaliznytsia "railway infrastructure" counts do not
   separate out bridges.
2. **Jul–Sep, Russian strikes on Ukrainian bridges.** In July I searched almost entirely the UA side. The
   Kramatorsk/Slovyansk glide-bomb series (Aug–Sep) is undercounted: a milblogger says three crossings were hit near
   Kramatorsk in Aug–Sep, and the Slovyansk road bridges were "destroyed earlier" with no date.
3. **Jan–May, UA strikes.** The searches support near-zero. Both ACLED and the MoD April summary describe the bridge
   campaign as starting in June. **Treat this as a measured low, not an unsearched month.**
4. **Russian-territory bridges** (Kursk, Belgorod, Bryansk): only three were found (Kolykhalino, Kozino, Zvannoye).
   The governors' daily summaries were not swept.

## Known duplication risks

- **Henichesk–Arabat Spit bridge vs. "Henichesk Strait road bridge".** These may be the same structure; I kept them
  under their source wording.
- **Preobrazhenka vs. Myrne canal bridges (11 Jun).** These may be a single bridge.
- **Malyi Kalchyk vs. Kalka near Hranitne (1 Jul).** Counted once.
- **Korsak (25 Jun) vs. ACLED "Volodymyrivka" (25–26 Jun).** Counted once.
- **Kramatorsk 5–6 Sep vs. Yasnohirka 8 Sep.** These may overlap.
