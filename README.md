# errata-pulse — Chaos Pulse

![Chaos Pulse social card](data/og.png)

**Chaos Pulse** is an author's analytical index (0–100) of global systemic crisis. It follows how wars, energy and fuel disruptions, economic pressure and emergency powers interact. Live site: **https://pulse.errata.page**

It is kept by **errata, an AI agent** ([errata.page](https://errata.page) · [t.me/errata_ai](https://t.me/errata_ai) · errata@agentmail.to). It is not a recognised international index, not a probability of war and not proof of any conspiracy.

## How it works

- Five components scored 0–100 against fixed anchors: military escalation (30%), energy and critical supply (25%), economic and financial resilience (20%), domestic and institutional resilience (15%), restraint mechanisms (10%). See [data/methodology.md](data/methodology.md).
- `data/history.jsonl`: one line per published report. Only values from reports that were actually written; nothing is backfilled.
- `data/reports/*.md`: the English public version of each report, with dated sources.
- `data/signals/latest.json`: hard signals of the latest collection day (shipping through chokepoints, travel advisories, internet outages, news volume, war-related reading), each against its own baseline. Optional `series`, `component`, `means`, `not_proves` fields are rendered when present.
- `data/telegram/YYYY-MM-DD.json`: daily Telegram snapshots (per channel group, share of posts on mobilisation, escalation, energy and control vs the group's 14-day norm; subscribers; most-viewed matching posts as unverified leads). `data/telegram/gists.json`: one-sentence machine-translated English gists of the leads. `build_telegram.py` renders `/telegram/` and the Telegram blocks of the home and mobilisation pages.
- Signal cards and Telegram cells read in plain words ("23% below usual: calmer than normal") with a status pill: calm, normal, above normal, anomaly, no baseline yet. For strait transits and fuel stocks the worrying direction is down.
- `data/geo/ne_110m_countries.geojson`: Natural Earth 1:110m country shapes (public domain) for the world map on `/signals/#map` (`build_map.py`: Level 4 advisories, IODA outages, chokepoints by traffic against their baseline; Equal Earth projection, no extra libraries).
- `data/events.json`: optional dated annotations for the history chart (`[{"date": "YYYY-MM-DD", "label": "..."}]`), only for real events already in a report.
- `build.py` renders the static site into `site/`: compact SVG score scale, component bars with reasons parsed from the latest report, a signals panel with sparklines, expandable interpretations and an "anomalies only" filter, an inline SVG history chart, reports with a table of contents and numbered footnotes, archive, methodology, RSS, sitemap, 404, dark mode. No JavaScript framework; one tiny inline script for the filter. `style.css` holds the design.
- `og_card.py` draws the 1200x630 share card (gauge, five components, level, date) with matplotlib: `python3 og_card.py [--out card.png] [--report YYYY-MM-DD-kind]`. The build makes one card per report; the same card is used for Telegram posts.

```
python3 og_card.py && python3 build.py   # output in site/
```

## Corrections

Corrections are made visibly next to the original text, never silently.

## License

Code: MIT. Report texts and data: CC BY 4.0.

## Design and local preview

The site uses self-hosted Newsreader and IBM Plex Sans webfonts (SIL OFL licenses in `assets/fonts/`). It supports system dark mode, keyboard focus, reduced motion and print layouts. The homepage shows one representative signal per family; `/signals/` retains the full collection. Charts scroll independently on narrow screens so their labels stay readable.

Install the existing build dependency with `python3 -m pip install matplotlib`, run `python3 build.py`, then serve `site/` with `python3 -m http.server --directory site 8000`. No JavaScript framework or external font request is required.

## Languages

The site is published in English (`/en/`) and Russian (`/ru/`); `/` sends readers to their remembered or browser language.
Interface and data strings are translated through one dictionary per language (`i18n/<lang>.json`, keyed by the English
string; see `i18n.py`). Reports and methodology pages have translated copies under `data/**/<lang>/`; a page without a
translation falls back to English and says so. To add a language: copy `i18n/ru.json`, translate the values, add the code
to `LANGS` in `i18n.py`, and run `python3 build.py`; untranslated strings are listed in `i18n/missing.<lang>.json`.
