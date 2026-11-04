# Post-freeze change (2026-11-04, after the frozen run was seen)

The frozen run (out_frozen.txt) used the region parser of mod_regions_2025.py, as pre-registered. Checking its exposure
afterwards showed it is broken for this window: only 145 of 358 days had any parsed UAV, while 342 days carry an MoD
air-defence bulletin. From April 2026 the MoD stopped listing numbers per region ("N UAVs over the territories of
Belgorod, Kursk, ... regions"), so the per-region parser finds nothing (parsed bulletins: 105 in Jan, 11 in Apr, 0 from
May). Also the fetched bulletins end on 2026-10-20, so the frozen window's last 12 days were false zeros.

Change, made after seeing the frozen result: `--fix` adds the national headline total for bulletins with no per-region
items, and ends the window at 2026-10-19. Everything else (series, statistic, placebo, claim rule) is unchanged. Because
this was decided after the frozen numbers were seen, the fixed run is a corrected analysis, not a pre-registered one.
