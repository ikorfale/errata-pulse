#!/bin/bash
# Exposure-window sensitivity for mod_join15.py (theone 99990, Fable review 23.10). Each window runs in its own temp dir
# because mod_regions_2025.py writes mod_regions_2025.tsv. Needs mod_claims_2025.jsonl here (build it with
# ../register/mod_claims_fetch.py; not committed, 8 MB) and CHRONICLES_DIR set.
set -e; HERE=$(cd "$(dirname "$0")" && pwd); PY=${PY:-~/venv/bin/python}
one() { T=$(mktemp -d); cp "$HERE"/mod_regions_2025.py "$HERE"/mod_join15.py "$HERE"/exposure_window.py "$HERE"/mod_claims_2025.jsonl "$T"; cd "$T"
  BOUNDS=$4 $PY mod_regions_2025.py $2 $3 >/dev/null; [ -n "$5" ] && cp "$5" mod_regions_2025.tsv
  echo "=== $1"; $PY mod_join15.py 2>&1 | grep -E "^  (main|full)"; cd "$HERE"; rm -rf "$T"; }
one "published common window 2025-03-26..2025-10-21 (210 d)" 2025-03-26 2025-10-21
one "pre-fieldwork 183 d 2025-03-27..2025-09-25" 2025-03-27 2025-09-25
one "length-matched 183 d ending at fieldwork end 2025-04-22..2025-10-21" 2025-04-22 2025-10-21
one "pre-fieldwork 30 d 2025-08-27..2025-09-25 (descriptive)" 2025-08-27 2025-09-25
one "fieldwork period only 2025-09-26..2025-10-21 (descriptive)" 2025-09-26 2025-10-21
one "bound: per-region MIN over interview dates of [t-183, t-1]" 2025-03-27 2025-10-20 1 bounds_min.tsv
one "bound: per-region MAX over interview dates of [t-183, t-1]" 2025-03-27 2025-10-20 1 bounds_max.tsv
