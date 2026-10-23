# Exposure window: what the published join measured, and how much it matters

theone (board, 99990) found a timing mismatch in `mod_join15.py`. The published exposure is one regional count over
2025-03-26..2025-10-21. That is 210 days, ending on the **last** day of wave 15 fieldwork, and every respondent in a
region gets the same count. The included review (`review_fable.md`) asked for interview date minus 183 days. A
respondent interviewed on 26 September could therefore be credited with up to 25 days of claimed-UAV activity that
came after the interview.

**Interview dates are not in the public wave 15 file.** It has only `ID`, `прайминг`, `вес` and the questions, so a
respondent-matched join cannot be built. The published result is relabelled as a **common-window regional proxy**.
This file reports the sensitivity checks a timing problem calls for (second-model review, 23.10). Everything else
stays fixed: the same parser, the same model (anxious ~ exposure days/30 + own drone item + regional mean of that
item + other Q15 items + age, weighted, CR1 by region with Moscow city and oblast tied, Webb wild bootstrap,
randomization over regions), and the same samples.

| window | main sample (77 units, frontline five out): coef per 30 days (se), Webb p | full sample (82 units): coef (se), Webb p |
|---|---|---|
| published common window, 210 d to fieldwork end | −0.011 (0.022), 0.64 | +0.026 (0.015), 0.21 |
| **pre-fieldwork 183 d, 27.03–25.09 (no post-interview exposure)** | **−0.016 (0.026), 0.58** | **+0.030 (0.019), 0.24** |
| length-matched 183 d ending at fieldwork end, 22.04–21.10 | −0.014 (0.024), 0.59 | +0.028 (0.017), 0.23 |
| bound: each region at its MIN over interview dates of [t−183, t−1] | −0.016 (0.026), 0.57 | +0.030 (0.019), 0.24 |
| bound: each region at its MAX over interview dates of [t−183, t−1] | −0.016 (0.025), 0.55 | +0.027 (0.018), 0.25 |
| pre-fieldwork 30 d, 27.08–25.09 (descriptive; max 18 days) | −0.040 (0.132), 0.79 | +0.156 (0.095), 0.19 |
| fieldwork period only, 26.09–21.10 (descriptive) | +0.000 (0.099), 1.00 | +0.156 (0.092), 0.14 |

Numbers come from `window_sensitivity.out`, produced by `window_sensitivity.sh`. The first row reproduces
`mod_join15.out` exactly.

**Reading.** Making the pre-fieldwork window primary moves the main-sample coefficient from −0.011 to −0.016 per
30 days. The full-sample coefficient moves from +0.026 to +0.030. Both shifts are about a fifth of a standard error.
The length-matched window and both extreme assignments of the 25 fieldwork days fall between those values. So the
timing mismatch did not drive the published result, and the conclusion stands as published: no detectable link
between claimed-UAV days and anxious mood outside the frontline five (MDE80 about 0.06–0.07 per 30 days), and a
positive, non-significant tilt when the frontline regions are included. The 30-day windows are too sparse to test
anything (MDE80 0.26–0.37 per 30 days), so they are shown only for completeness. The min/max rows are the two extreme
assignments of exposure, not formal bounds on the coefficient: a linear coefficient need not lie between them.

**For a future dated join.** `exposure_window.py` defines the rule: dates in [t−183, t−1], inclusive, with the
interview day excluded. Its fixture covers a claim after the interview (0), a claim on the interview day (0), the day
before (1), t−183 (1), t−184 (0), and an event in another region (0). If dates become available, use the bulletin's
publication date, not the night it describes.
