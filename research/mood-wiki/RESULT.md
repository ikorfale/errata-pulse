# Mood H5 wiki: result (2026-11-04)

Prereg PREREG.md (3531524). Post-freeze exposure fix POSTFREEZE.md. Outputs out_frozen.txt, out_fix.txt; `run.py`.

| run | exposure days >0 | primary (shelter + alert) rho, placebo p | secondary (air defence, drones) rho, p |
|---|---|---|---|
| frozen (broken parser) | 145 / 358 | -0.047, 0.49 | -0.019, 0.74 |
| fixed exposure | 340 / 345 | -0.045, 0.39 | **+0.173, 0.014** |

**Primary: null.** Russian-language reads of the shelter, civil-defence, alert-system and evacuation articles do not
rise on the days the MoD claims more drones over Russia (10 heaviest days: x0.99 of the local norm). My guess before
running was a small positive rho; it was wrong.

**Secondary, with three caveats:** reads of the air-defence/drone articles move with the claimed drone count (rho +0.17,
p 0.014 against 214 shifted lags). (1) It is a secondary outcome, (2) in a run whose exposure was fixed after the
frozen run was seen, (3) those articles include Shahed 136, a Russian weapon: heavy Ukrainian drone nights may
coincide with heavy Russian strikes on Ukraine, and ru.wiki readers in Ukraine read the same pages. So this says
"Russian-language readers look up drones on big drone days", not "people in Russia prepare for strikes".

**What it means for the mood project:** reading about shelters is not a behaviour signal at national scale.
Russian-language Wikipedia cannot be attributed to Russia, and the per-region MoD numbers needed for a regional test no
longer exist after April 2026. Regional behaviour has to come from regional sources (Google Trends by region,
regional alert-channel subscribers), as the 25.10 review suggested.
