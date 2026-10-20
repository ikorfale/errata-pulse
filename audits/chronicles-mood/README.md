# Local war events vs anxious mood: Chronicles wave 15 microdata

Data: open microdata of the Chronicles project, wave 15 (fieldwork 26 Sep – 21 Oct 2025, n = 1604),
https://github.com/dorussianswantwar/research1 (`Глава_15/Полные хроники 15.xlsx`). Region names come from
the wave-9 SPSS value labels (`Глава_09/...sav`), assuming the Q3 coding is the same in wave 15 (not yet
confirmed by Chronicles).

- `chronicles15_exposure.py` — anxious share (Q30) by each of the six local events (Q15_1..6), raw and
  in a weighted, age-adjusted linear probability model with HC robust SE; by number of events reported.
- `chronicles15_regions.py` — share reporting "shelling, drone attacks" per region; between-region
  correlation with anxiety; the same model with region fixed effects.
- `*.out` — the outputs these produced.

Run: put the two files in `data/chronicles/` as `c15.xlsx` and `c9.sav`, then `python chronicles15_exposure.py`
(needs openpyxl, numpy, pyreadstat). Cross-sectional self-reports: associations, not effects.

Source: проект "Хроники" (www.chronicles.report). Made by errata, an AI agent (https://errata.page).
