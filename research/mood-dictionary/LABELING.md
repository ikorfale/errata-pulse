# Blind hand-label rules (written before labeling, 2026-10-28)
Sample: sample.py (seed 353): 12 posts per channel from the 10 v2 regional channels (lab/mood_react/data_v2), 6 uniformly random
and 6 from the top quarter by (😱+🤬+😢+😡)/views (a text-independent enrichment so that rare categories have positives).
The labeler sees only channel, id and text (first 700 chars), never dict_v1 hits. dict_v1.py is frozen (FROZEN.sha256) first.
A category is present if the post expresses it in its own voice, or reports people expressing it, or (blame) attributes harm:
- fear: fear, alarm, panic, dread expressed or reported. A bare official threat warning ("угроза БПЛА") is not fear.
- anger: indignation, outrage, fury expressed or reported (incl. emoji-free wording like "возмутительно", residents "возмущены").
- revenge: calls for or promises of retaliation/punishment of an enemy or offender framed as payback.
- peace: negotiations, ceasefire, peace settlement or end of any armed conflict mentioned.
- fatigue: weariness with the war/situation, "how long", exhaustion expressed or reported.
- blame_auth: criticism of Russian authorities (any level) for failure, inaction or harm, incl. residents' complaints to officials.
- blame_enemy: attributes a harm (attack, casualty, damage) to Ukraine / Ukrainian forces / "Kyiv regime", factual or charged.
Unreadable/empty text: label "x" and excluded from scoring.
