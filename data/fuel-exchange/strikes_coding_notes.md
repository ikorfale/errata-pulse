# Refinery strike coding — judgement calls (coded 2026-11-15)

Rules as given; no fuel-volume data looked at. Date = local morning date of the overnight attack.

## Operational reading of the rule
1. **Independent outlet** = an outlet with its own sourcing: own OSINT geolocation (ASTRA, Militarnyi, Reuters video analysis, RFE/RL Schemes satellite image) or own sources (Reuters industry sources). An outlet that only relays ASTRA is not a second outlet (it is not independent of ASTRA), same as one relaying Exilenova+/General Staff.
2. **Reuters industry-source reports** that a refinery halted "after the drone attack of <date>" count as the outlet reporting the refinery hit.
3. **Bloomberg "person familiar"** (Ufa 31 Oct, Afipsky 6 Nov) is treated as an unofficial Ukrainian-side claim, so it does not count. Counting it would flip Ufa 31 Oct and Afipsky 6 Nov to confirmed (W6 +1, W7 +1).
4. **Militarnyi's own geolocation** of the Syzran 15 Sep fire is counted as the second outlet (with Reuters). If it is excluded, Syzran becomes claimed (W3 3 to 2 confirmed).

## Specific calls
- **Novak 14 Oct (Saratov, Ryazan)**: coded as 2 confirmed. A deputy PM names a refinery "in the Saratov / Ryazan region", and each region has a single refinery. But both governors reported no refinery damage, Ukraine denied it, and ASTRA saw nothing. This is the weakest "confirmed" in the table; dropping it gives W4 = 1 confirmed.
- **Novak 30 Oct**: 3 refineries, none named. Novokuibyshevsk (the only refinery reported hit that night, also confirmed through ASTRA + Schemes) is matched to it, plus 2 unnamed confirmed rows. Ufa is not matched because that attack came the following night. The gas-chemical complex is excluded.
- **Ryazan 7 Sep**: Zelensky's 7 Sep statement about Ryazan is taken as the 6 Sep strike (ASTRA reported it on 6 Sep). No separate row.
- **Tatarstan 7 Sep**: Zelensky said "refineries in Tatarstan" without a name. Kept as one claimed row, "unnamed refinery (Tatarstan)".
- **Perm 7 Sep**: claimed. Meduza says the refinery hit is unconfirmed, and some reports point to the Zakamsk powder plant.
- **Saratov 8 Sep and 11 Sep**: two separate rows. Reuters sources describe a halt on 8 Sep from strike damage and a new halt from 11 Sep after "another drone attack".
- **Slavyansk ECO 13 Sep, TANECO 13 Sep, Kstovo 1 Nov, Afipsky 6 Nov, Saratov 7 Nov**: claimed. In each case the official named only an "enterprise", or nothing, and the refinery was identified by ASTRA alone. Kstovo district also has a SIBUR petrochemical plant, and Nizhnekamsk also has TAIF-NK and Nizhnekamskneftekhim.
- **Yaroslavl 17 Sep**: the governor said "an oil refinery". Taken as YANOS, because the city has one refinery.
- **Moscow 20 Sep**: authorities said "an oil refinery in the capital", which can only be Kapotnya.

## Exclusions (not refineries)
- Novatek Ust-Luga, 1 Sep (W1): gas-condensate fractionation complex. Ukrainian sources call it a "refinery", but it is excluded under the gas-processing rule.
- Surgut, 16 Oct (W4): Gazprom condensate stabilisation plant. Excluded.
- St Petersburg oil terminal, 18 Oct; Sochi/Adler depot, 3–7 Sep; Samara LPDS (Transneft), 2 Nov; Tolyattikauchuk, 12 Sep (petrochemical): excluded.

## Empty weeks
- W5 (19–25 Oct): no refinery strike found. Reuters (27 Oct) cites Russian authorities: no refinery strikes after 16 Oct. Novak on 30 Oct: "attacks resumed". bne and Kyiv Post describe a roughly two-week gap.
- W1 has only Ryazan on 6 Sep. Searches for 31 Aug–5 Sep found only Ust-Luga (excluded) and depots.

## Coverage limits
roshlopok.com and Reuters' "What has been hit" page were not walked date by date (budget). Small refineries (mini-refineries) may be missing in any week. Sources used: deepstrike.info, energywar.net, bne Missile War Monitor ledger, uk.wikipedia list (partial).

## External comparison (added 2026-11-20, not used in the test)
Sergey Vakulenko (Carnegie Russia Eurasia Center, X thread "Russian Refining Chronicles – Part Two", 18 Nov 2026): refining
in operation ~4.7 mb/d at end of October (Kuibyshev, Syzran, Tuapse down), ~3.1 mb/d after the 13 Nov Volgograd strike, 2.7–2.8
mb/d by the evening of 17 Nov against ~5.5 mb/d full capacity; of the refineries attacked 1–13 Nov only Omsk still running; his
13 Nov "55%" is the share of petrol output of plants *attacked*, not output lost (he says so). His estimates come from
"several sources" he does not name. Under my v2 rule (C counts only halts reported by Reuters industry sources or an official
statement naming the unit) the weeks 9–15 Nov and 16–22 Nov carry C = 0.0 with 4 and 1 hits: the floor is far below any
analyst estimate, which is the price of coding from reports only. Keep as a sanity bound for #760; do not mix into C.
