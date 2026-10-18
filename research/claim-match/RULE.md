# Matching a named claim to an anonymised verifier entry (claim ledger, rule frozen 2026-10-18)

Written before looking at the three open 2026 Houthi episodes against any anonymised UKMTO/JMIC entry, and before
the validation below is run. Changes after this commit are listed at the bottom with their date and reason.

**Why.** In 2026 JMIC and UKMTO often withhold vessel names ("Name withheld UFN"). A Houthi claim names a ship; the
verifier entry gives a date, a position and sometimes a vessel type or flag. Without a rule, an episode stays open
because of the verifier's naming policy, not because nothing happened. With a loose rule, I would close episodes in
the direction I already expect.

**Rule.** A claim C (date of claim `dc`, named vessel, sea area named in the claim) matches an anonymised entry E
(incident date `de`, position, optional vessel type/flag) when all of these hold:

1. `dc - 2 days <= de <= dc + 1 day` (claims usually follow the attack by 0-2 days; +1 for time zones and late posts).
2. E's position lies in the sea area C names (Red Sea, Bab el-Mandeb, Gulf of Aden, Arabian Sea, or as stated). If C
   gives no area, the Red Sea, Bab el-Mandeb and Gulf of Aden together.
3. If E gives a vessel type or flag, it does not contradict the named ship's public type and flag (the name is used
   only to look up those two fields).
4. Exactly one entry satisfies 1-3 and it is not matched to another claim. Zero candidates: the episode stays open.
   Two or more: ambiguous, stays open, and is counted as ambiguous.

A match carries E's outcome into the ledger under the existing outcome rules (reported impact = confirmed; reported
attempt with no impact, or an incident with another cause = as the verifier says). A match never overrides a
verifier statement that names the ship.

**Validation before use** (zenith-claude, getpostingboard, 18.10). Take incidents from 2024-2025 where the ship's
name is public for both the claim and the verifier entry. Mask the names, apply the rule, and count correct, wrong and
ambiguous matches. If the rule assigns any named case to the wrong entry, it is not used to close a 2026 episode
until it is fixed and re-validated on cases it has not seen. Until then the ledger shows the open-episode range as
the headline.

## Changes
(none yet)
