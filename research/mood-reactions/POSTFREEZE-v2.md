# Mood v2: what changed after the freeze, before any reaction value was read (27.10, ~21:05-21:25Z)

PREREG-v2.md stays frozen (sha ef003362...). These are the decisions taken after it, each before the test windows'
reaction values were read. The claim rests on the frozen primary only; anything marked "sensitivity" is reported
beside it whatever it shows.

1. **Parser.** fetch.parse (data_v2/) kept only plain emoji: custom emoji (`<tg-emoji>`) and paid stars were missing
   from the denominator the PREREG defines ("custom emoji included"). On a current kazancity page 22 of 106 badges
   were custom and 1 paid. Fable review 1 also found that on reply posts the first text div is the quoted post.
   parse_v2r.py fixes both and keeps full text; data_v2r/ is a re-fetch with it (fetch_windows_v2r.py).
   The 50-post classifier check (regex_v2_check.py) ran on data_v2 text, which had both faults; it is re-run unchanged
   except for the glob (regex_v2_check_v2r.py) before the test, and any change is reported.
2. **Ryazan channel.** run_v2.py check: overheardryazan (11 posts in 30 days) shows no alarm emoji in blocks -21..-15
   of event 5 -> next eligible channel by the PREREG's rule: ryazan_smi ("Новости Рязани и Области", #3;
   usernames-v2.tsv, name + count match).
3. **Bryansk.** br_gorod has zero posts in the window; the alarm-set rule read literally would move to bryansk_smi,
   but the frozen pre-freeze note decides this case ("the Bryansk event drops"). Primary: Bryansk drops.
   bryansk_smi appears in the pre-registered 2nd-channel robustness run. (My lean was the other way; Fable review 1
   argued the frozen note governs, and I agree: a post-freeze addition triggered by a check is a fork.)
4. **K.** The power line says K = 10; the register holds 11 events after Bryansk drops (the 10 counted fetch windows;
   Rostov 11 and 17 share one). K = 11 needs a mean event rank of about 4.8 of 15 for 80% power.
5. **Code decisions D1-D8** are in run_v2.py's docstring; Fable review 1 (fable-run_v2-review-1.txt) found no
   deviation from the PREREG and judged D1-D8 direction-neutral.

## Hashes at the time of writing (the run must use these files)
0c81ced60f1e60ada2cee30bb3fcf6b10884dbf57e361b66696a4832b4478abd  run_v2.py
ce726d01e36cd8c5328424b153cfe583625847974b8dff91b59a82bd80ea3ad2  parse_v2r.py
36aecb3b9e7f3939fb0dc33e99f7a1827c0c64d405361c1565ddc34faecdafa6  fetch_windows_v2r.py
0b9ec58c24b8f4a4c48fb3042f0a27659a14c153a9fa25bc5a00df049f1e99c4  usernames-v2.tsv
da963939b02266ba8a863e66dc1fb813ca7601930bc8c94a4eb7e391ecc56733  ../mood/civ_verify_b.tsv
4163646dd55e1be51393b5c5d8418710471fc0767c68f36a1fe92a18f3fa2cd9  regex_v2_check_v2r.py
22408f588580d8f70770ff6ed0b18e7b848edfd5e59cfb7696e9a7f90003a18d  test_run_v2.py
