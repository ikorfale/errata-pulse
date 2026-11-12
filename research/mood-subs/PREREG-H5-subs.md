# H5 behaviour layer: do people subscribe to their governor's channel when their region is under air alert? (pre-registration, 2026-11-12)

Status: FROZEN at the commit time below (FREEZE in h5_test.py). Canonical copy: github.com/ikorfale/errata-pulse,
research/mood-subs/. Nothing in either file may change after that commit except typo fixes recorded at the end.
Design reviewed by a second model (Fable, 12.11) before the freeze; all ten of its fixes applied.

## Question
H5 (pulse/mood/PLAN.md): behaviour moves more than survey answers. The behaviour measured here: subscribing to the
regional governor's Telegram channel, the main official source of local alert and strike news. If air alerts make
people seek official safety information, a region's governor channel should gain subscribers faster in 12-hour
windows with more alert hours in that region than in its own usual windows, compared with other regions at the same
time.

## Data (both forward-only, both collected by my own timers)
- Exposure: `pulse/alerts_live/` — snapshots every 5 min of officially declared region-level alerts (UAV, missile,
  both) from pulse.errata.page/api/alerts. Since 2026-11-02. Region level only; stale flags (`*`) ignored.
- Outcome: `pulse/mood/subs/census.jsonl` — exact subscriber counts of governor channels at ~03:40 and ~15:40 UTC.
  Since 2026-11-05. Counts only; nothing about readers.

## What I have already seen (peek disclosure)
- Census noise and drift (NOISE.md, 12.11): governors drift −0.13 %/week; 18 of 55 had a ≥5-robust-SD step in one week;
  the six largest-jump handles were printed (top: Leningrad oblast +1.06 %).
- Alert snapshot counts per region over 02–12.11 (top: Kursk, Bryansk, Belgorod, Oryol, Rostov) — exposure only.
- NOISE.md proposed a threshold rule with matched far regions; I switched to the continuous FE model because the
  noise finding (a third of channels jump ≥5 SD weekly) made any threshold arbitrary, not because of any outcome.
- None of the six largest-jump handles (Leningrad, Murmansk, Moscow, Stavropol, Chechnya, Tatarstan governors) is
  in the five top-alert regions. The border trio of secondary (c) was chosen from the exposure peek.
- The script's final-mode code path was exercised once on alert data with regions deliberately relabelled at random
  (a placebo, seed 7); no real exposure-outcome estimate has been computed.
- I have NOT joined the two series. The test period starts at the freeze, so the pre-freeze week enters only as the
  trailing norm, never as tested windows.

## Units and exclusions (fixed now)
- Governor channels whose count at the freeze is ≥ 5 000 (52 at the dry run), mapped to an RU-* region code (name table + 14 fixed aliases in the
  script). Crimea and Sevastopol excluded (not RU-* in the alert set; separate information space). MChS channels are
  not tested (23 of 55 counters flat).
- A step = two consecutive census counts 6–18 h apart. y = 100·ln(s₁/s₀), scaled to 12 h.
- Norm: the channel's own steps that end in [step end − 14 days, step start); needs ≥ 10. The norm includes earlier
  test-period steps, exposed ones too; this can only attenuate β. z = (y − median)/max(MAD·1.4826,
  0.005 %), winsorised at ±10 (purges and ad drives are not dropped, only capped). Channels with MAD 0 are dropped.
- Windows: 12-h bins centred on the 03:40/15:40 census slots; exposure x = hours under any declared alert in the
  region during the bin's nominal 12 h. A declared alert counts until cancelled, whether or not the API marks it stale
  (stale-as-absent is secondary d). A bin with < 90 % snapshot coverage (gaps > 15 min count as missing) is dropped for
  every channel.

## Test
- Model: z = β·x + channel FE + window FE (window FE absorb nationwide Telegram purges, ad waves, news days).
  β estimated by OLS after two-way demeaning.
- Inference, two nulls (neighbouring regions share alerts and news, so region permutation alone may be too narrow):
  (1) region permutation — alert series reassigned among sample regions, time structure kept; (2) window
  permutation — each window's whole cross-regional alert pattern moved to another window. 2 000 draws each, seed
  1113, p = (1 + #|β_perm| ≥ |β|)/(1 + 2000), two-sided.
- Direction stated: β > 0. Support for H5 = β > 0 with both p < 0.05. Otherwise "not detected", reported with
  the permutation band and the MDE from placebo injection. A negative β with p < 0.05 is reported as such.
- Test windows: from the freeze to 2026-12-14 04:00 UTC (~60 windows × ~52 channels). One run, `--final`, after
  that date; the script refuses earlier, with no override. Before then only `--placebo` (permuted exposure, never the
  real join). One placebo run once ≥ 10 windows exist; its MDE is recorded here before the final run.
- MDE = 2.8 × SD of the region-permutation null, printed in z per alert-hour and as % subscribers per fully alerted
  12-h window for a median-noise channel (0.012 %/12 h). Power rests on regions with intermittent alerts; the border
  trio has near-constant exposure, which channel FE absorbs.
- Secondary, labelled as such: (a) lag 1 — alert hours in the previous 12 h; (b) missile-only hours (missile or both);
  (c) without the three border regions with near-constant alerts (Kursk, Bryansk, Belgorod); (d) stale-as-absent.

## What a result would and would not mean
- A positive β shows people turn to the official channel when alerts sound. It does not show fear, approval or a change
  of opinion, and it cannot separate "people seek safety information" from "the channel posts alerts, posts get
  forwarded, forwards bring subscribers" (posting volume is not collected). Both readings are behaviour; only the first
  is mood. Stated as a limitation, not resolved.
- A null says the subscriber counter at 12-h resolution does not move with alert hours beyond the noise; with the
  MDE stated, not "alerts change nothing".
- Aggregate only; nothing about individuals; no claim about any single region.

## Log
- 2026-11-12: drafted, reviewed by Fable, fixes applied, frozen.
