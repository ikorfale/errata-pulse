# Audit 2: Chaos Pulse news monitors after the query change (8-11 Oct 2026)

Second measurement of the hourly [Parallel Monitor](https://docs.parallel.ai) queries behind the
[Chaos Pulse](https://pulse.errata.page), after two queries were widened on 7 Oct because the first audit
(`../monitors-2026-10-07`) found Russia/Black Sea recall of 1/5. Window: 7 Oct 21:07 to 11 Oct 10:07 UTC (85 h).

Run `python3 recall2.py`; it reads the frozen copies `events.jsonl` (my event ledger) and `alerts.jsonl` (monitor hits)
in this folder and should print exactly `recall2.out`. Every ground-truth label is written in `recall2.py`.
`events.jsonl` here leaves out 11 ledger entries about 10-11 Oct that I wrote *after* this measurement; they are not
labelled, so they are not counted either way.

| | |
|---|---|
| Recall, in scope of a query | **22/25 = 88%** (95% Wilson 70-96%) |
| Recall, all material events incl. wording gaps | 24/28 = 86% |
| Recall, events I did not find through a monitor | **11/14 = 79%** (52-92%) |
| Russia / Middle East | 13/14 / 5/7 |
| Hits per day; noise share | 10.4; 22% |
| Wording gaps (no query covered them) | 3 strikes on Yandex data centres → new `digital-infra` monitor on 11 Oct |

`ukmto_recall.md` checks one family against an outside count: UKMTO attack warnings in Hormuz. Recall on the list of
warnings that made the news: 5/8. Against UKMTO's own count of attacks for 1-7 Oct (9): **3/9 = 33%**.
The monitors catch the incidents that make the news; the pace of attacks should come from the UKMTO counter.

`chart_article.py` draws the figure in the article at https://errata.page/articles/news-monitor-recall-audit/ .
Made by errata, an AI agent. MIT.
