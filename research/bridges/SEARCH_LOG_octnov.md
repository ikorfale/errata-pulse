# Blind recount, bridge strikes 28 Sep – 17 Nov 2026: search log

Done blind. I did not open strikes.csv, SEARCH.md, durations.*, weekly.* or anything else about bridges under
my work folder. From the recency folder I read only SEARCH_LOG.md (the method template) and the header line of
jan_sep_blind.csv. The searches ran on 2026-11-18 through Parallel web_search (**32 searches**, most with 3–4 query
variants each) and web_fetch (**1 fetch call**, 2 URLs: the Telegraf Zatoka timeline and the Informator Zatoka
10 Nov piece). That is the same effort as the Jan–Sep recount (33 searches + 2 fetches).

Output: `oct_nov_blind.csv`, 40 rows.

## Totals

| | confirmed | claimed | total |
|---|---|---|---|
| RU strikes (bridges in Ukraine) | 11 | 12 | 23 |
| UA strikes (Russia + occupied areas) | 9 | 8 | 17 |
| all | 20 | 20 | 40 |

By week (Mon–Sun, event date). The last week is partial, 16–17 Nov only.

| Week | RU | UA | Main items |
|---|---|---|---|
| 28 Sep – 4 Oct | 4 | 3 | Kyiv Southern (1, 2 Oct) and Northern (3, 4 Oct); Dyatkovo–Lyudinovo rail bridge collapse (28 Sep); Trosna (29 Sep, weak); Chonhar span (26–30 Sep, date uncertain) |
| 5 – 11 Oct | 4 | 3 | Zaporizhzhia (6, 7 Oct); Oskil near Osynovo and Petrivka (RU claims); Rostov swing and Western bridges, Bryansk Vygonichi rail bridge (10 Oct) |
| 12 – 18 Oct | 1 | 4 | Dnipro city approach (13 Oct, SouthFront only); Unecha rail bridge (16–17 Oct); St Petersburg Korabelny Fairway and Finland railway bridges (18 Oct); "ammo-store bridge" near Huliaipole (weak) |
| 19 – 25 Oct | 3 | 0 | Kyiv Southern (22 Oct); Zaporizhzhia Vantovyi (22 Oct OSINT, 24 Oct footage, possibly one event) |
| 26 Oct – 1 Nov | 2 | 0 | Kyiv Southern (27 Oct); Dnipro Central (30/31 Oct) |
| 2 – 8 Nov | 4 | 1 | Zatoka (2 Nov); Kramatorsk Kazennyi Torets (≈5 Nov); Zaporizhzhia Preobrazhensky (6 Nov); Kyiv Northern (7 Nov); Mius R-280 (8 Nov) |
| 9 – 15 Nov | 2 | 3 | Zatoka (10 and 11 Nov); Huselshchykove (11 Nov); R-280 overpass km 64 and Mius near Mykolaivka (15 Nov) |
| 16 – 17 Nov (partial) | 3 | 3 | Zaporizhzhia Preobrazhensky (16 Nov); Kyiv Northern and Southern (night of 16–17 Nov); Kerch bridge (16 and 17 Nov); Mius R-280 again (17 Nov) |

## Queries per theme (32 searches)

- **Kyiv Dnipro bridges** (EN/UK/RU), 3 searches. These found every Kyiv row: 1, 2, 3, 4, 22 and 27 Oct, and 7 and 17 Nov.
- **Zaporizhzhia city bridges**, 3 searches. Rows for 6, 7, 22 and 24 Oct and 6 and 16 Nov. The DniproHES dam
  closure on 14 Nov is excluded as precautionary.
- **Dnipro city**, 1 search plus hits from other searches.
- **Odesa region (Zatoka, Mayaky)**, 2 searches + 1 fetch.
- **Crimean (Kerch) bridge**, 1 search; Chonhar/Henichesk, 2 searches; occupied south, Crimea and Melitopol, 2 searches.
- **Rostov R-280 / Mius / Novoazovsk / Don bridges**, 2 searches plus 1 Russia-wide rail-bridge search. The Oko Gora
  list came through Militarnyi and UNITED24.
- **Bryansk / Kursk / Belgorod**, 2 searches. Belgorod and Kursk produced nothing.
- **St Petersburg**, 1 search, after an ISW hit.
- **ISW / CTP by keyword** (Oct, Nov, Siverskyi Donets/Oskil/Kramatorsk), 3 searches.
- **Ukrainian MoD middle-strike October summary**, 1 search. It names only one bridge, the Unecha rail bridge.
- **Russian strikes on Ukrainian rail bridges and Russian MoD claims**, 1 search; Kharkiv/Sumy/Donetsk frontline, 1 search.
- **Confirmation checks** (Vantovyi 22 Oct, Dnipro 13 Oct), 1 search; window edge 28–30 Sep plus Kherson/Mykolaiv/Mayaky, 1 search.
- **General Staff claims** Oct/Nov, 1 search, and a Ukrainian-language General Staff query, 1 search.

## Inclusion rules and judgement calls

- **The same rules as Jan–Sep.**
  - Excluded: pontoons, ferries, unnamed crossings, and precautionary closures. Examples: the DniproHES dam closure
    on 14 Nov; "crossings over the Kryvyi Torets near Kindrativka" (16 Oct milblogger, unnamed); the Ukrainian
    "21/8 alternative crossings" programme.
  - Repeat strikes on the same bridge on different days are separate rows.
  - Several waves on the same day are one row. Examples: Kyiv Southern had 3 hits on 1 Oct and 2 on 2 Oct.
- **Mayaky bridge, 11 Nov: excluded.** OSINT trackers reported Kh-59/69 hits on it. Per AMK Mapping, the Russian MoD
  then corrected this and said the missiles hit substations near Mayaky, not the bridge. The Zatoka row for 11 Nov
  is kept as claimed.
- **Chonhar road bridge.** Satellite imagery shows holes on 26 Sep and a collapsed span on 30 Sep. I dated the row
  30 Sep (imagery date). The strike may have fallen on 26–27 Sep, which is outside the window. It may also be
  double-counted against the Jan–Sep recount's Sep 26 coverage. The General Staff wrote that "the Chonhar and
  Henichesk bridges went down this autumn". I found no autumn Henichesk strike (all Henichesk hits I found are from
  June), so there is no Henichesk row.
- **Dyatkovo–Lyudinovo (28 Sep).** It is in this window. The Jan–Sep log excluded it as outside its window, so there
  is no overlap.
- **Kyiv, night of 16–17 Nov.** The first impacts came at about 23:45 on 16 Nov and a second wave at 05:35 on
  17 Nov. Both are dated 17 Nov, one row per bridge.
- **Rostov swing and Western bridges.** Dated 10 Oct, following ISW and Oko Gora. LB says "night of 11 Oct".
- **St Petersburg Korabelny Fairway bridge: confirmed.** This is the imagery rule: ASTRA/Exilenova+ geolocated video
  and separate satellite imagery. There is no Russian official confirmation of this bridge. The satellite channel
  calls it the "Southern Fairway Bridge"; I treated that as the same structure.
- **Confirmed by attacker-side authority alone does not count.** Russian MoD statements (Kyiv 1–2 Oct and 7 Nov)
  were not used as confirmation; the owner side confirmed those anyway.
- **Weak rows a reviewer may want to drop:**
  - Trosna, 29 Sep: the governor reported only track damage.
  - "Bridge used as ammo store", 16 Oct: headline only.
  - Dnipro Southern approach, 13 Oct: SouthFront only.
  - Kramatorsk, ≈5 Nov: milbloggers only.

## Coverage gaps

1. **Frontline Russian strikes** (Kramatorsk/Sloviansk/Druzhkivka glide bombs, Oskil, Siverskyi Donets) reached me
   only through ISW keyword hits. As in Jan–Sep, this is the largest undercount. ISW calls Kazennyi Torets bridge
   strikes "regular", but I have only one row.
2. **Zatoka.** I found 3 rows (2, 10, 11 Nov) but no October row, and no Odesa OVA statement confirming damage. All
   Zatoka rows are claimed. Clément Molin's count, via bne, of "dozens of strikes" on Zatoka suggests an undercount.
3. **Zaporizhzhia city.** The OVA often closes bridges without naming a cause, so strike and closure are hard to
   separate. 22 Oct vs 24 Oct may be one event.
4. **Occupied south (Kherson left bank, Melitopol, Berdiansk, Crimea interior).** I found no rows apart from
   Chonhar. The October MoD summary lists no bridges there, which is weak evidence of a real low. Saldo and Balitsky
   statements for Oct–Nov were not swept day by day.
5. **Belgorod / Kursk.** Nothing found. Governors' daily summaries were not read one by one.
6. **Oko Gora** was reached only through media, and only its Rostov/Novoazovsk list ("at least six bridges since early
   October"). It mentions "earlier strikes" on the main Hruzkyi Yelanchyk crossing. Those strikes were not dated,
   so they have no row.
7. **Kyiv.** Informator mentions "over 10 ballistic strikes on Kyiv bridges since autumn". My rows count strike-days
   (8 Kyiv rows), not missiles.
