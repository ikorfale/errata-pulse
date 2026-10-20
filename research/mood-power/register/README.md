# Strike register backfill, criterion (a): Moscow, 2025-10-21 .. 2026-10-20

Part of the FOM strikes pre-registration (draft v1, not frozen yet). The backfill only decides which
waves leave the placebo pool. Nothing from the FOM series has been joined to it.

## Sources
- MoD bulletins (t.me/s/mod_russia), Moscow-region line, `mod_moscow_daily.py` -> `moscow_daily_backfill.tsv`.
  The MoD stopped giving per-region lines after 2026-03-17 (list totals only), so from 2026-03-18 the PREREG
  fallback applies: Sobyanin's own count (t.me/s/mos_sobyanin, posts 16502..22215, raw: `sobyanin_2026.jsonl.gz`,
  sha256 of the uncompressed file aa9b5f9f...fff2b; MoD raw files are 8-10 MB and kept by sha256 only:
  2025 2f74fb48...d9c237a, 2026 d1f7a7f1...ae57cf90).

## What the data showed (before any rule was fixed for the Sobyanin part)
1. **Single reports undercount.** On raid nights Sobyanin stops posting every downing and later gives one total.
   Against his own weekly and monthly totals ("N destroyed on approach to Moscow"), the sum of his single reports in
   the same window is 0.39 to 1.00 of the total (`sobyanin_check.txt`; July 551 of 780, August 515 of 795).
   The miss is largest on the biggest nights, which is where the >= 100 threshold sits.
2. **Overlap with the MoD (2025-10-21 .. 2026-03-17, 148 days):** MoD Moscow-region total 717, Sobyanin city total
   879; daily r = 0.74, two-day sums r = 0.85; MoD higher on 45 days, Sobyanin on 8. The gap in totals is one
   two-day post (16.03, "250 over the last two days, on approach and on the second line"), counted here as singles
   only because its window is longer than 36 h.

## Rule used (fixed 2026-10-20 after seeing finding 1, so it is disclosed as data-informed)
Each Sobyanin summary with a window of at most 36 h gets max(its number, singles posted inside the window), on the
date of the summary post (Moscow time). Singles outside every summary window count by their own date. Summaries were
copied by hand; ids and windows are in `sobyanin_register.py`.

## Result: days >= 100 (fallback era, 2026-03-18 .. 2026-10-20)
18.06 (194), 16.08 (201), 18.08 (197), 03.09 (147), 20.09 (450), 06.10 (173), 14.10 (180), 17.10 (144), 18.10 (127).
MoD era (2025-10-21 .. 2026-03-17): none (max 84 on 16.03).
After the 21-day merge (first date counts): **4 Moscow events: 18.06, 16.08, 20.09, 14.10.**
Days 60-99 in the fallback era, which a 30-40% undercount could have pushed over 100: 10, among them 17.05 (81),
22.06 (84), 28.07 (85), 13.10 (75); all in `sobyanin_register.tsv`. They change the pool by at most a few waves; listed, not counted.

## Consequence for the forward test (to go into PREREG before the freeze)
Since mid-October Sobyanin posts a daily 08:30-08:30 total ("N neutralised on approach to Moscow"). The forward
register should use that daily total when it exists, and the max rule above when it does not; a day without either is
logged as missing, not as zero.

Criterion (b) (5-19 civilians killed in one attack) is not done yet.
