# Mood H5, behaviour layer: do ru.wikipedia reads of shelter/alert articles rise on heavy drone days? (frozen 2026-11-04 15:50Z)

Written and committed before any pageview series was looked at by date (the 25.10 inventory looked at volume only).

- **Outcome:** daily user pageviews (Wikimedia REST, all-access, user agents) on ru.wikipedia, summed over the
  shelter+alert family fixed on 25.10: Бомбоубежище, Гражданская оборона, Автоматизированная система
  централизованного оповещения (target of "Воздушная тревога"), Эвакуация. Window 2025-11-09..2026-11-01.
- **Secondary outcome:** air-defence family (Противовоздушная оборона, Беспилотный летательный аппарат,
  Военное применение беспилотных летательных аппаратов, Shahed 136).
- **Exposure:** UAVs the Russian MoD claims destroyed over Russian regions per UTC date, parsed from its Telegram
  bulletins with the region parser of mod_regions_2025.py (weekly summaries skipped). Claimed interceptions, not impacts.
- **Statistic:** both series as log(1+x), minus a centred 29-day rolling median, minus weekday means of the residual;
  Spearman rho between the two residual series on the same day.
- **Placebo:** the same rho with the exposure circularly shifted by every lag in ±14..±120 days; p = share of placebo
  |rho| >= observed |rho|.
- **Claim rule:** "rises" only if rho > 0 and p < 0.05 for the primary family. Otherwise a null, reported as such.
- **Known confounds, stated now:** ru.wikipedia is read in Ukraine, Belarus, Kazakhstan and elsewhere; Russia's share
  of ru.wiki views cannot be isolated (Wikimedia withholds per-country data for Russia). Big drone nights over Russia
  also make news everywhere. So even a positive result is "Russian-language readers", not "people in Russia".
- **My guess before running:** small positive rho (0.05-0.15) for the primary family; a null would not surprise me.
