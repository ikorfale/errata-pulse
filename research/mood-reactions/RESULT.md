# Reader reactions after a local drone strike: result (run 2026-10-24, after the freeze in commit 0128cb8)

Outputs: out_all.txt (frozen analysis), out_placebo.txt (post hoc). Post-level data is not published (post texts
belong to the channels); fetch.py rebuilds it from the public previews. Reaction counts were fetched 24.10, i.e.
6 to 16 days after each strike.

## As pre-registered
- **St Petersburg 18.10, Fontanka** (largest attack on the city since 2022, oil terminal fire, 1 killed): all four
  cells above the minimum (strike posts 38 before / 43 after; other posts 273 / 57).
  - strike-topic posts: derision (clown, poop, laughing) median share 0.30 before -> 0.17 after
    (difference -0.128, 95% bootstrap [-0.273, -0.042]); pray 0.00 -> 0.09 [+0.051, +0.134];
    support -0.065 [-0.145, -0.004]; fear +0.071 [-0.008, +0.342] (does not clear zero); anger ~0.
  - unrelated posts on the same two days: derision 0.23 -> 0.13 (-0.105 [-0.188, -0.011]); fear 0.005 -> 0.03
    (+0.024 [+0.004, +0.088]); reactions per 1000 views fell (-2.08 [-3.20, -0.66]).
- **Omsk 08.10, Om1**: strike cell below the minimum (11 baseline posts, need 20): no claim. Unrelated posts
  (17 after): every bucket's interval crosses zero.
- **Ryazan 15.10, ryazan_chp62**: both cells below the minimum (8-9 posts after): no claim.
- Sign agreement across three cases, the most the design allowed: **not available**. Only one case had the data.

## What it can and cannot say
- Omsk's unrelated-posts cell (the contrast that moved in Petersburg) shows no movement: the Petersburg spillover did
  not replicate in the one other case with data.
- One city: in Petersburg's main news channel, readers stopped mocking. Derision fell on strike posts and, more
  tellingly, on posts about anything else; 🙏 appeared. Fear emoji moved little.
- 🙏 is not simply fear: its highest shares on 18.10 are on the all-clear (0.63), the airport reopening (0.60) and the
  injured in hospital (0.52): relief and sympathy as much as alarm.
- Derision before the strike was mostly on posts about strikes *elsewhere* (0.30 median). The shift is "it stopped
  being funny when it was here", but that sentence rests on one channel.
- The minimum reaction count (30 per post) is the bottleneck: regional channels of 60-90k subscribers rarely reach it.

## Post hoc: pseudo strike days (placebo.py, not pre-registered)
The same contrast on every day 13-22.10 in Fontanka: derision in unrelated posts moves +0.015 to +0.038 on the four
windows starting 13, 14, 21 and 22.10 (I did not check those for local alerts), falls on every window starting 15 to 19.10 (-0.055 to -0.105,
largest on 18.10) and is -0.009 on 20.10. This is not a clean placebo: Leningrad oblast had drone alerts on 16 and 17.10 (🙏 rises there
too) and missing children in Frunzensky district on 15.10. Read it as "local danger days" vs "quiet days", not as
an isolated strike-day effect.
