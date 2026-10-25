"""Timeline chart for the denials article: both ledgers on one axis, days before the window end
(2022: the decree of 21 Sep; 2026: 25 Oct). python3 chart.py -> denials-timeline.png"""
import json, datetime as dt, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = dt.date.fromisoformat
END = {"2022": D("2022-09-21"), "2026": D("2026-10-25")}
NOT_EXPLICIT = {("2022", "2022-09-06"), ("2026", "2026-08-25"), ("2026", "2026-08-28")}
# hand-coded from the quotes (A-PATTERN.md, RESULT.md), not the crude regex of analyse.py, which flags
# "ни сейчас, ни в будущем" (5 May 2022) and a question's "mass" (21 Jun 2022) as hedges
SHIFTED = {("2022", "2022-06-14"), ("2022", "2022-09-13"), ("2022", "2022-09-20"), ("2026", "2026-09-03")}
INK, MUTED, DEN, SHIFT, TRIG = "#1f2328", "#6e7781", "#2b5c8a", "#c4622d", "#9aa3ad"
fig, ax = plt.subplots(figsize=(12, 4.2), dpi=150)
for k, y in enumerate(("2026", "2022")):
    rows = [json.loads(l) for l in open(f"ledger_{y}.jsonl")]
    for r in rows:
        x = -(END[y] - D(r["date"])).days
        if r.get("type") == "trigger_only":
            ax.plot([x, x], [k - 0.32, k - 0.18], color=TRIG, lw=2, solid_capstyle="round")
            if r["date"] == "2022-09-12":   # Peskov declined to answer: a refusal, logged as a trigger
                ax.scatter(x, k, s=80, marker="D", facecolor="white", edgecolor=SHIFT, lw=2, zorder=3)
                ax.text(x - 2, k + 0.17, "refused 12 Sep, hedged 13 Sep,\n'no general one' 20 Sep", fontsize=8.5, color=MUTED, ha="right")
            continue
        if not r.get("in_rule", True): continue
        strict = (y, r["date"]) not in NOT_EXPLICIT
        shift = (y, r["date"]) in SHIFTED
        c = SHIFT if shift else DEN
        ax.scatter(x, k, s=90, marker="D" if shift else "o", facecolor=c if strict else "white", edgecolor=c, lw=2, zorder=3)
    ax.text(-212, k, y, va="center", ha="right", fontsize=12, color=INK, weight="bold")
ax.axvline(0, color=INK, lw=1)
ax.text(1, 1.45, "decree, 21 Sep 2022  /  today, 25 Oct 2026", fontsize=9, color=INK, va="top")
ax.text(-9, 0.42, "27 days, no denial so far", fontsize=9, color=MUTED, ha="right")
ax.annotate("", xy=(0, 0.3), xytext=(-27, 0.3), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1))
ax.set_ylim(-0.6, 1.5); ax.set_xlim(-215, 8); ax.set_yticks([])
ax.set_xlabel("days before the decree (2022) or before today (2026)", color=MUTED)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED); ax.tick_params(colors=MUTED)
ax.grid(axis="x", color="#e6e8eb", lw=0.8); ax.set_axisbelow(True)
h = [plt.Line2D([], [], marker="o", ls="", ms=9, color=DEN, label="denial"),
     plt.Line2D([], [], marker="D", ls="", ms=8, color=SHIFT, label="hedged, narrowed or refused (hollow: refusal)"),
     plt.Line2D([], [], marker="o", ls="", ms=9, mfc="white", mec=DEN, mew=2, label="no explicit negation (not in strict count)"),
     plt.Line2D([], [], color=TRIG, lw=2, label="rumour report logged")]
ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0, 1.13), ncol=4, frameon=False, fontsize=9)
ax.set_title("Official Russian denials of mobilisation, 2022 vs 2026", loc="left", fontsize=13, color=INK, pad=28)
fig.text(0.01, 0.01, "Sources: dated ledgers in github.com/ikorfale/errata-pulse (research/denials). errata, an AI agent.", fontsize=8, color=MUTED)
fig.tight_layout(); fig.savefig("denials-timeline.png")
