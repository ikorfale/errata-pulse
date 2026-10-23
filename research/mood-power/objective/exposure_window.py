"""Respondent-matched exposure for a dated join (theone 99990, Fable review 23.10).
Exposure of a respondent interviewed on date t in region r = number of distinct dates in [t-183d, t-1d], both inclusive,
with >= 1 claimed UAV over r. The interview day itself is excluded (MoD bulletins appear the morning after the night
they describe). Wave 15 has no interview dates, so mod_join15.py cannot use this yet: it uses a common regional window,
and window_sensitivity.md reports the pre-fieldwork window and the min/max bounds over all fieldwork dates instead."""
import datetime as dt

LOOKBACK = 183


def exposure(days_by_region, region, interview):
    t = dt.date.fromisoformat(interview) if isinstance(interview, str) else interview
    lo, hi = t - dt.timedelta(LOOKBACK), t - dt.timedelta(1)
    return sum(lo <= dt.date.fromisoformat(d) <= hi for d in days_by_region.get(region, ()))


if __name__ == "__main__":
    ev = {"A": {"2025-10-01"}, "B": {"2025-09-26", "2025-03-27", "2025-03-26"}}
    cases = [
        ("A", "2025-09-26", 0),   # claim after the interview: no future exposure
        ("A", "2025-10-21", 1),   # claim 20 days before
        ("A", "2025-10-01", 0),   # claim on the interview day: excluded
        ("A", "2025-10-02", 1),   # the day before: included
        ("B", "2025-09-26", 1),   # 2025-03-27 is t-183 (included), 2025-03-26 is t-184 (excluded), 09-26 is the interview day
        ("C", "2025-10-21", 0),   # region without events
    ]
    ok = 0
    for r, t, want in cases:
        got = exposure(ev, r, t)
        assert got == want, (r, t, got, want)
        ok += 1
    assert exposure({"A": {"2025-10-01"}}, "B", "2025-10-21") == 0  # an event in A never reaches B
    print(ok + 1, "exposure-window cases pass")
