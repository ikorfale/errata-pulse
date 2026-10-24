# Strike-report filter, redesign: holdout 2 (written 2026-10-24 ~09:30 UTC, before any data of its window)

Why: holdout 1 (PREREG.md, result 24.10) kept 9/9 NEW but dropped only 1/3 FALSE, so it failed on the registered
point-estimate rule at n = 3. The two kept FALSE were one denial post ("fake", a minister's claim) counted for two
sites; the rule also kept 5/6 FOLLOW, including posts marked "archive".

## The rule under test (NEW2), frozen in rules2.py at this commit
NEW2 = the current strike_signals.py rule (site stem within 250 chars of a facility word and within 80 of a strike word;
every "night of <date>" 2+ days old -> not counted) AND the post matches neither
- ARCH (archive footage): `архив|архів|archive|кадры прошл|кадри минул|прошлогодн|минулоріч`
- DENY (denial): `опроверг|спростов|фейк|не поражен|не уражен|не пострадал[аио]? (нпз|завод|предприят|объект)|не соответству|не відповіда`
(case-insensitive, anywhere in the post). Applied per post, before the site-day is formed, exactly as the current rule.

Tuned on seen data (rules2.py -> rules2.txt, all 88 labelled items, 70 in-sample + 18 holdout 1): NEW kept 42/42 by
both; FALSE dropped 8/16 by the current rule, 10/16 by NEW2; FOLLOW kept 22/30 -> 19/30. Both extra FALSE drops are
the holdout-1 denial post. This is the data the rule was written on, so it proves nothing; it shows NEW2 costs no NEW
there.

## Holdout 2
- **Window**: posts dated 2026-10-24..2026-12-31 (UTC dates as the collector assigns them). No post of this window has
  been read by me in the strike context; the daily collector writes 24.10 at 22:30 UTC today.
- **Unit and label** (as Amendment 1 of PREREG.md): universe = every (date, site) that the CURRENT rule counts in the
  window (NEW2 only tightens it; site-days NEW2 counts and the current rule does not should not exist, are reported
  and excluded). Each is labelled NEW / FOLLOW / FALSE by a blind verdict on the current rule's first URL, with the
  same definitions and tie-breaks. Kept = NEW2 counts that (date, site) under any URL.
- **Rebuild**: holdout2_run.sh (committed now) into holdout2/{cur,new2}/, run once after 2026-12-31 is complete. The
  current rule is cur_strike_signals.py (a copy of tools/strike_signals.py at this commit) and NEW2 is
  new2_strike_signals.py (the same file plus three lines in classify(): a post matching ARCH2 or DENY2 counts no site;
  the patterns are byte-equal to rules2.py's). Both are frozen here; no later edit is used. A channel-day the rebuild
  cannot reach is missing, counted and reported, never filled.
- **Blinding**: shuffled sheet with date, site, full text only; key (URLs, NEW2 status) in a separate file opened only
  after the verdicts file is committed. Any rule status seen before judging is logged as a breach, with its item, and
  breached items are excluded from the ratios (reported separately).
- **Tie-breaks added for this test** (Fable review 24.10, written before any window data): a post whose claim is that
  reports of a strike on that site are false -> FALSE; an official post reporting an attack on that site with no damage
  claimed -> NEW; a post reporting a strike on that site and quoting a denial -> NEW; a post captioned as archive /
  earlier footage -> FOLLOW unless it also reports a strike on that site on its date or the night before (then NEW).
- **Success**: NEW2 keeps >= 90% of NEW site-days AND drops >= 40% of FALSE site-days (point estimates, k/n with
  Wilson 95%; wording "pass, confirmed / pass, not confirmed / fail" as in Amendment 1). Secondary, reported, not
  decisive: FOLLOW keep rate; the same ratios for the current rule on the same sheet.
- **Small n**: the current rule produced 8 FALSE site-days in 53 seen days (6 in-sample, 2 in holdout 1), so a 4-week
  window would very likely end underpowered; the window is therefore 2026-10-24..2026-12-31 (69 days, expected ~10
  FALSE), fixed now, judged once in one blind sheet after it closes, no interim look. Report distinct posts beside
  site-days (one multi-site post can supply several). If FALSE < 8 site-days or < 4 distinct posts: "underpowered", no
  verdict; NEW2 stays out of the Pulse, the current rule stays, and holdout 2 is not pooled with any later holdout.
- **Missing text**: retried once; still empty = excluded and counted.
- **Decision**: pass -> NEW2 goes into strike_signals.py and the Pulse strike card from the next report, said in that
  report. Fail -> keep the current rule, say so, and do not tune again on holdout-2 items.

## Frozen files (sha256; the scripts stay in the working lab because they carry local paths)
```
a21f5be30d5992ae78d4861c4d68904a1a2b79fda16bf90b7472e1edc1832d70  rules2.py
c3a2b446a2e5ff8856a18914f60be8358460d0cc8dd8ccaaaec5cb8e6ddd81d9  cur_strike_signals.py
efbc9472b40ed5b29e6d55b5597fc0d95d7ea7d4c96691849b3e0a3aef39fded  new2_strike_signals.py
8cc64cf04c9f6c04940a2f62b00ddf3e72afd575b7db39c80b13807de0155784  holdout2_run.sh
78bf52a6dbc38fb38dfc327697f494622d454472c8764283ebbc87f768d90c85  rules2.txt
```
