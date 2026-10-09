#!/usr/bin/env python3
"""Build pulse.errata.page/forecasts/: errata's own probabilities for falsifiable questions, scored in public.
data/forecasts/site.json  written by the forecast ledger (`forecast export`): counts, Brier scores, calibration bins,
                          per-model scores and every question with its full history of updates.
Called from build.py once per language (after the other pages); home_block() feeds the home page.
Honesty rules on the page: track record first; dashes, not numbers, where nothing is resolved; with fewer than
MIN_RECORD resolved questions the record is labelled too short to judge; annulled questions are shown, never hidden."""
import json, os
from datetime import datetime, timezone, timedelta
import build as B
import i18n
from i18n import t
FD = os.path.join(B.D, 'forecasts')
MIN_RECORD = 10
CATS = [('war', 'War'), ('energy', 'Energy'), ('economy', 'Economy'), ('mobilisation', 'Mobilisation'), ('politics', 'Politics'), ('tech', 'Tech and AI'), ('other', 'Other')]
MODELS = [('base', 'Base rate', 'outside view: how often this kind of thing happened before'),
          ('signals', 'Signals', 'inside view: the base rate updated with evidence as likelihood ratios'),
          ('trend', 'Trend', 'for quantities: the current level and volatility of a series against the threshold'),
          ('second', 'Second model', 'an independent estimate by another AI model, given the evidence but not the number')]
CROWD = {'manifold': 'Manifold', 'polymarket': 'Polymarket', 'metaculus': 'Metaculus'}
DATA = None

def load():
    global DATA
    if DATA is None:
        f = os.environ.get('FORECASTS_JSON') or os.path.join(FD, 'site.json')
        DATA = json.load(open(f)) if os.path.exists(f) else {}
    return DATA

def today(): return datetime.now(timezone.utc).date()
def day(s): return datetime.strptime(str(s)[:10], '%Y-%m-%d').date()
def cat_name(c): return t(dict(CATS).get(c, c.capitalize()))
def model_name(m): return t(dict((k, n) for k, n, _ in MODELS).get(m, m))
def pct(p): return '—' if p is None else i18n.num_pct(p)
def dec(x, n=3):
    if x is None: return '—'
    s = f'{x:.{n}f}'
    return s.replace('.', ',') if i18n.LANG in ('ru', 'uk') else s
def en(s, tag='span'):
    """Question texts are written in English; mark them so screen readers and translators know."""
    return f'<{tag} lang="en">{B.esc(s)}</{tag}>' if i18n.LANG != 'en' else B.esc(s)
def en_note(): return '' if i18n.LANG == 'en' else f'<p class="fq-ennote">{t("Question texts are in English")}</p>'
def crowd_label(q):
    return ' + '.join(CROWD.get(c.partition(':')[0], c.partition(':')[0].capitalize()) for c in q.get('crowd') or [])
def crowd_now(q):
    ch = q.get('crowd_history') or []
    return ch[-1]['p'] if ch else None
def days_left(q):
    n = (day(q['deadline']) - today()).days
    if n < 0: return t('deadline passed, awaiting resolution')
    if n == 0: return t('deadline today')
    return f'{n} ' + i18n.plural(n, 'day left', 'days left')
def qpath(q): return f"/forecasts/q/{q['id']}/"
def latest(q): return (q.get('history') or [{}])[-1]

# ---------- charts ----------
def spark(q, w=150, h=36):
    """How errata's probability moved: a step line on a fixed 0-100% scale (so a flat line means unchanged, not small)."""
    hs = [(day(x['date']), x['p']) for x in q.get('history') or []]
    if not hs: return ''
    t0 = hs[0][0]; t1 = max(hs[-1][0], today() if q['status'] == 'open' else hs[-1][0], t0 + timedelta(days=1))
    span = (t1 - t0).days or 1
    X = lambda d: 3 + (d - t0).days / span * (w - 6); Y = lambda p: h - 3 - p * (h - 6)
    s = f'<line x1="0" x2="{w}" y1="{Y(.5):.1f}" y2="{Y(.5):.1f}" class="mid"/>'
    if len(hs) == 1 and today() <= hs[0][0]:          # a single reading: one dot, no invented line
        return f'<svg class="fq-spark" viewBox="0 0 {w} {h}" role="img" aria-label="{B.esc(t("First reading: {p}", p=pct(hs[0][1])))}"><line x1="0" x2="{w}" y1="{Y(.5):.1f}" y2="{Y(.5):.1f}" class="mid"/><circle cx="{w / 2}" cy="{Y(hs[0][1]):.1f}" r="3"/></svg>'
    if len(hs) > 1 or t1 > t0:
        d = f'M{X(hs[0][0]):.1f},{Y(hs[0][1]):.1f}'
        for (a, p0), (b, p1) in zip(hs, hs[1:]): d += f' H{X(b):.1f} V{Y(p1):.1f}'
        d += f' H{X(t1):.1f}'
        s += f'<path d="{d}"/>'
    s += f'<circle cx="{X(hs[-1][0]):.1f}" cy="{Y(hs[-1][1]):.1f}" r="3"/>'
    lab = t('Probability over time: {n} update(s), from {a} to {b}', n=len(hs), a=pct(hs[0][1]), b=pct(hs[-1][1]))
    return f'<svg class="fq-spark" viewBox="0 0 {w} {h}" role="img" aria-label="{B.esc(lab)}"><title>{B.esc(lab)}</title>{s}</svg>'

def pbar(q, big=True):
    p = q['p']; cr = crowd_now(q)
    mark = ''
    if cr is not None:
        mark = (f'<span class="fq-crowd" style="left:{cr * 100:.1f}%" title="{B.esc(t("Crowd ({src}): {p}", src=crowd_label(q), p=pct(cr)))}"></span>'
                f'<span class="fq-crowdlab{" l" if cr < .15 else " r" if cr > .85 else ""}" style="left:{cr * 100:.1f}%">{B.esc(crowd_label(q))} {pct(cr)}</span>')
    return (f'<div class="fq-bar{" has-crowd" if cr is not None else ""}" role="img" aria-label="{B.esc(t("errata: {p}", p=pct(p)) + ("; " + t("Crowd ({src}): {p}", src=crowd_label(q), p=pct(cr)) if cr is not None else ""))}">'
            f'<span class="fq-fill" style="width:{p * 100:.1f}%"></span><i style="left:25%"></i><i style="left:50%"></i><i style="left:75%"></i>{mark}</div>')

def p_chart(q):
    """Probability over the life of a question: errata (step line), the crowd (dashed), the base rate (dotted), deadline."""
    W, H, L, R, T, Bm = 880, 280, 48, 24, 18, 34
    hs = [(day(x['date']), x['p']) for x in q.get('history') or []]
    cs = [(day(x['date']), x['p']) for x in q.get('crowd_history') or []]
    t0 = min([day(q['opened'])] + [d for d, _ in hs + cs]); dl = day(q['deadline'])
    end = day(q['resolved_at']) if q.get('resolved_at') else today()
    t1 = max(dl, end, t0 + timedelta(days=7))
    span = (t1 - t0).days or 1
    top = max([p for _, p in hs + cs] + [q.get('base_rate') or 0])
    ymax = 1 if q['status'] in ('yes', 'no') else next(m for m in (.1, .2, .4, .6, 1) if m >= top * 1.25 or m == 1)   # low probabilities stay readable
    X = lambda d: L + (d - t0).days / span * (W - L - R); Y = lambda p: T + (1 - p / ymax) * (H - T - Bm)
    s = ''
    for v in [ymax * i / 4 for i in range(5)]:
        s += f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" class="ax" text-anchor="end">{pct(v)}</text>'
    step = max(1, span // 6); d = t0
    while d <= t1 - timedelta(days=step // 2): s += f'<text x="{X(d):.1f}" y="{H - 10}" class="ax" text-anchor="middle">{i18n.date_short(d)}</text>'; d += timedelta(days=step)
    s += f'<line x1="{X(dl):.1f}" x2="{X(dl):.1f}" y1="{T}" y2="{H - Bm}" class="ev"/><text x="{X(dl) - 5:.1f}" y="{T + 12}" class="evlab" text-anchor="end">{t("deadline")} {i18n.date_short(dl)}</text>'
    now = min(end, t1)
    if q.get('base_rate') is not None:
        s += f'<line x1="{L}" x2="{W - R}" y1="{Y(q["base_rate"]):.1f}" y2="{Y(q["base_rate"]):.1f}" class="fq-base"/><text x="{L + 6}" y="{Y(q["base_rate"]) - 6:.1f}" class="bandlab">{t("base rate")} {pct(q["base_rate"])}</text>'
    def stepline(pts, cls):
        if not pts: return ''
        dd = f'M{X(pts[0][0]):.1f},{Y(pts[0][1]):.1f}'
        for (a, _), (b, p1) in zip(pts, pts[1:]): dd += f' H{X(b):.1f} V{Y(p1):.1f}'
        if now > pts[-1][0]: dd += f' H{X(now):.1f}'
        return f'<path d="{dd}" class="{cls}"/>'
    s += stepline(cs, 'fq-cline') + stepline(hs, 'line')
    for d_, p in cs: s += f'<circle cx="{X(d_):.1f}" cy="{Y(p):.1f}" r="3.5" class="fq-cpt"><title>{B.esc(crowd_label(q))} {B.fmt_date(d_.isoformat())}: {pct(p)}</title></circle>'
    for d_, p in hs: s += f'<circle cx="{X(d_):.1f}" cy="{Y(p):.1f}" r="5" class="fq-pt"><title>errata {B.fmt_date(d_.isoformat())}: {pct(p)}</title></circle>'
    up = not cs or not hs or hs[-1][1] >= cs[-1][1]          # the higher line is labelled above, the lower one below
    def lx(d_):
        x = X(max(now, d_)); return (f'{x - 4:.1f}" text-anchor="end' if x > (L + W - R) / 2 else f'{x + 4:.1f}" text-anchor="start')
    if hs: s += f'<text x="{lx(hs[-1][0])}" y="{Y(hs[-1][1]) + (-9 if up else 19):.1f}" class="ptlab">errata {pct(hs[-1][1])}</text>'
    if cs: s += f'<text x="{lx(cs[-1][0])}" y="{Y(cs[-1][1]) + (19 if up else -9):.1f}" class="fq-clab">{B.esc(crowd_label(q))} {pct(cs[-1][1])}</text>'
    if q['status'] in ('yes', 'no'):
        o = 1 if q['status'] == 'yes' else 0; x = X(day(q['resolved_at']))
        s += f'<rect x="{x - 6:.1f}" y="{Y(o) - 6:.1f}" width="12" height="12" class="fq-out"><title>{t("Outcome")}: {t(q["status"].upper())}</title></rect>'
    if ymax < 1: s += f'<text x="{W - R - 6}" y="{T + 28}" class="evlab" text-anchor="end">{t("scale 0–{m}", m=pct(ymax))}</text>'
    lab = t('Probability of “{q}” over time', q=q['title'][:80])
    legend = (f'<p class="fq-legend"><span><i class="lg-e"></i>errata</span>' + (f'<span><i class="lg-c"></i>{B.esc(t("crowd"))} ({B.esc(crowd_label(q))})</span>' if cs else '')
              + (f'<span><i class="lg-b"></i>{t("base rate")}</span>' if q.get('base_rate') is not None else '') + '</p>')
    return legend + f'<div class="chart" tabindex="0" role="region" aria-label="{B.esc(lab)}"><svg class="hist" viewBox="0 0 {W} {H}" role="img" aria-label="{B.esc(lab)}">{s}</svg></div>'

def calib_svg(cal, nres):
    W = H = 360; L, R, T, Bm = 52, 16, 16, 44
    X = lambda p: L + p * (W - L - R); Y = lambda p: T + (1 - p) * (H - T - Bm)
    s = ''
    for v in (0, .2, .4, .6, .8, 1):
        s += f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" class="ax" text-anchor="end">{pct(v)}</text>'
        s += f'<text x="{X(v):.1f}" y="{H - Bm + 18}" class="ax" text-anchor="middle">{pct(v)}</text>'
    s += f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(1)}" y2="{Y(1)}" class="fq-diag"/>'
    if any(b.get('n') for b in cal): s += f'<text x="{X(.62):.1f}" y="{Y(.62) - 10:.1f}" class="bandlab" transform="rotate(-45 {X(.62):.1f} {Y(.62) - 10:.1f})" text-anchor="middle">{t("perfect calibration")}</text>'
    s += f'<text x="{(L + W - R) / 2}" y="{H - 6}" class="ax" text-anchor="middle">{t("errata said")}</text><text x="14" y="{(T + H - Bm) / 2}" class="ax" text-anchor="middle" transform="rotate(-90 14 {(T + H - Bm) / 2})">{t("it happened")}</text>'
    pts = [b for b in cal if b.get('n')]
    if not pts:
        s += f'<rect x="{X(.1):.1f}" y="{Y(.62):.1f}" width="{X(.9) - X(.1):.1f}" height="54" class="fq-empty"/><text x="{X(.5):.1f}" y="{Y(.62) + 23:.1f}" class="fq-emptyt" text-anchor="middle">{t("No resolved forecasts yet.")}</text><text x="{X(.5):.1f}" y="{Y(.62) + 42:.1f}" class="ax" text-anchor="middle">{t("Points appear here as questions resolve.")}</text>'
    nmax = max([b['n'] for b in pts] or [1])
    for b in pts:
        r = 5 + 9 * (b['n'] / nmax) ** .5
        s += f'<circle cx="{X(b["mean_p"]):.1f}" cy="{Y(b["freq_yes"]):.1f}" r="{r:.1f}" class="fq-cal"><title>{B.esc(t("Said {a} on average; happened {b} of {n}", a=pct(b["mean_p"]), b=pct(b["freq_yes"]), n=b["n"]))}</title></circle>'
        s += f'<text x="{X(b["mean_p"]) + r + 4:.1f}" y="{Y(b["freq_yes"]) + 4:.1f}" class="ax">n={b["n"]}</text>'
    return f'<svg class="fq-calib" viewBox="0 0 {W} {H}" role="img" aria-label="{t("Calibration chart: what errata said against how often it happened, {n} resolved", n=nres)}">{s}</svg>'

def brier_bars(rows):
    """rows: [(label, value, n, cls)]; Brier on a 0..0.25+ scale with the 'always 50%' reference."""
    top = max([0.3] + [v for _, v, _, _ in rows if v is not None])
    out = ''
    for lab, v, n, cls in rows:
        w = 0 if v is None else max(v / top * 100, 0.8)
        out += (f'<div class="bb-row {cls}"><span class="bb-lab">{lab}</span><span class="bb-track"><span class="bb-fill" style="width:{w:.1f}%"></span>'
                f'<i class="bb-ref" style="left:{.25 / top * 100:.1f}%" title="{t("always 50%")}"></i></span><span class="bb-val">{dec(v)}</span><span class="bb-n">{"n=" + str(n) if n else ""}</span></div>')
    return (f'<div class="bb" role="table" aria-label="{t("Brier scores")}">{out}<div class="bb-row bb-axis"><span></span><span class="bb-track"><span class="bb-reflab" style="left:{.25 / top * 100:.1f}%">0{"," if i18n.LANG in ("ru", "uk") else "."}25 = {t("always 50%")}</span></span><span></span><span></span></div></div>')

# ---------- blocks ----------
def mean(vs): vs = [v for v in vs if v is not None]; return (sum(vs) / len(vs), len(vs)) if vs else (None, 0)

def track_record(d, qs):
    c = d.get('counts', {}); nres = c.get('resolved', 0); res = [q for q in qs if q['status'] in ('yes', 'no')]
    br = d.get('brier') or {}
    sc = lambda k: mean([(q.get('scores') or {}).get(k) for q in res])
    if nres == 0:
        short = t('<strong>No forecast has resolved yet</strong>, so there is no track record to show: every score below is a dash, not a number. The first questions resolve on {d}.', d=B.fmt_date(min((q['deadline'] for q in qs if q['status'] == 'open'), default=today().isoformat())))
    elif nres < MIN_RECORD:
        short = t('<strong>The record is too short to judge.</strong> Only {n} of the first {m} questions needed for a meaningful comparison have resolved; a few lucky or unlucky outcomes still swing every number below. Read them as a start, not a verdict.', n=nres, m=MIN_RECORD)
    else: short = ''
    rows = [(t('errata (every day)'), br.get('mine'), sc('brier')[1], 'bb-me'), (t('errata (final call)'), br.get('final'), sc('brier_final')[1], 'bb-me2'),
            (t('Base rates alone'), br.get('base'), sc('brier_base')[1], 'bb-base'), (t('Crowd, same questions'), br.get('crowd'), sc('brier_crowd')[1], 'bb-crowd')]
    facts = (f'<dl class="facts fq-facts"><div><dt>{t("Resolved")}</dt><dd>{nres}</dd></div><div><dt>{t("Open")}</dt><dd>{c.get("open", 0)}</dd></div>'
             f'<div><dt>{t("Annulled")}</dt><dd>{c.get("annulled", 0)}</dd></div><div><dt>{t("Brier, errata")}</dt><dd>{dec(br.get("mine"))}</dd></div></dl>')
    # by model and by category, computed from the questions so each carries its n
    mrows = ''
    for k, n, desc in MODELS:
        v, m = mean([((q.get('scores') or {}).get('models') or {}).get(k) for q in res])
        if v is None and k in (d.get('models') or {}): v = d['models'][k]
        used = sum(1 for q in qs if k in (latest(q).get('models') or {}))
        mrows += f'<tr><td><strong>{t(n)}</strong><span class="gdesc">{t(desc)}</span></td><td class="n">{dec(v)}</td><td class="n">{m or "—"}</td><td class="n">{used}</td></tr>'
    crows = ''
    for k, n in CATS:
        qq = [q for q in qs if q['category'] == k]
        if not qq: continue
        r = [q for q in qq if q['status'] in ('yes', 'no')]; v, m = mean([(q.get('scores') or {}).get('brier') for q in r]); vb, _ = mean([(q.get('scores') or {}).get('brier_base') for q in r])
        crows += f'<tr><td>{t(n)}</td><td class="n">{dec(v)}</td><td class="n">{dec(vb)}</td><td class="n">{len(r)}</td><td class="n">{sum(1 for q in qq if q["status"] == "open")}</td></tr>'
    return (f'<h2 class="sec" id="record">{t("Track record")}</h2>'
            + (f'<p class="fq-short">{short}</p>' if short else '') + facts
            + f'<div class="fq-rec"><div><h3 class="smh3">{t("Brier score: lower is better")}</h3><p class="meta">{t("The mean squared distance between the probability and what happened, averaged over every day a question was open. 0 is perfect; 0.25 is what saying 50% to everything earns.")}</p>{brier_bars(rows)}'
            + f'<p class="meta">{t("“Every day” scores each day’s standing probability, so early, confident and right beats late. “Final call” scores only the last probability before the deadline. Base rates and crowds are scored on the same questions, the crowd only where a market existed.")}</p></div>'
            + f'<div><h3 class="smh3">{t("Calibration")}</h3><p class="meta">{t("Of everything said at about 30%, about 30% should happen. Points on the diagonal are well calibrated; above it, errata was too cautious; below it, too confident. Bigger points hold more questions.")}</p><div class="chart fq-calbox">{calib_svg(d.get("calibration") or [], nres)}</div></div></div>'
            + f'<div class="fq-rec2"><div><h3 class="smh3">{t("By model")}</h3><p class="meta">{t("Every forecast is built from at least two models; each is scored on its own.")}</p><div class="tscroll"><table class="howt"><thead><tr><th>{t("Model")}</th><th class="n">Brier</th><th class="n">{t("resolved")}</th><th class="n">{t("in use")}</th></tr></thead><tbody>{mrows}</tbody></table></div></div>'
            + f'<div><h3 class="smh3">{t("By category")}</h3><p class="meta">{t("Where errata is better or worse than a plain base rate.")}</p>'
            + (f'<div class="tscroll"><table class="howt"><thead><tr><th>{t("Category")}</th><th class="n">Brier</th><th class="n">{t("base rate")}</th><th class="n">{t("resolved")}</th><th class="n">{t("open")}</th></tr></thead><tbody>{crows}</tbody></table></div>' if crows else f'<p>{t("No questions yet.")}</p>')
            + '</div></div>')

def chips(q):
    ms = latest(q).get('models') or {}
    order = [k for k, _, _ in MODELS] + sorted(set(ms) - {k for k, _, _ in MODELS})
    return ''.join(f'<span class="chip" title="{B.esc(t(dict((k, d) for k, _, d in MODELS).get(m, "")))}">{B.esc(model_name(m))} <b>{pct(ms[m])}</b></span>' for m in order if m in ms)

def card(q):
    r = latest(q).get('reason', '')
    return (f'<article class="fq"><div class="fq-h"><span class="badge">{cat_name(q["category"])}</span><span class="fq-dl">{t("by {d}", d=B.fmt_date(q["deadline"]))} · {days_left(q)}</span></div>'
            f'<h3><a href="{qpath(q)}">{en(q["title"])}</a></h3>'
            f'<div class="fq-p"><span class="fq-big">{pct(q["p"])}</span><span class="fq-pl">{t("errata’s probability")}</span>{spark(q)}</div>{pbar(q)}'
            f'<div class="chips">{chips(q)}</div>'
            + (f'<p class="fq-why"><b>{t("Latest reason")} ({B.fmt_date(latest(q)["date"])}):</b> {en(r)}</p>' if r else '')
            + f'<p class="fq-more"><a href="{qpath(q)}">{t("Criteria, method and every update →")}</a></p></article>')

def outcome_badge(q):
    if q['status'] == 'annulled': return f'<span class="ob ob-x">{t("Annulled")}</span>'
    return f'<span class="ob ob-{q["status"]}">{t(q["status"].upper())}</span>'

def closed_list(qs):
    res = sorted([q for q in qs if q['status'] in ('yes', 'no')], key=lambda q: q.get('resolved_at') or '', reverse=True)
    ann = sorted([q for q in qs if q['status'] == 'annulled'], key=lambda q: q.get('resolved_at') or '', reverse=True)
    out = f'<h2 class="sec" id="resolved">{t("Resolved")}</h2>'
    if res:
        out += '<ul class="fq-closed">' + ''.join(
            f'<li><a href="{qpath(q)}">{outcome_badge(q)}<span class="fq-ct"><strong>{en(q["title"])}</strong><span class="meta">{cat_name(q["category"])} · {t("resolved {d}", d=B.fmt_date(q["resolved_at"]))} · {t("final probability {p}", p=pct(q["p"]))}</span></span>'
            f'<span class="fq-cs"><span class="small">Brier</span>{dec((q.get("scores") or {}).get("brier"))}</span></a></li>' for q in res) + '</ul>'
    else: out += f'<p class="meta">{t("Nothing has resolved yet. Every question will appear here with its outcome, its score and the source that decided it, whether errata was right or wrong.")}</p>'
    out += f'<h3 class="smh3" id="annulled">{t("Annulled")}</h3>'
    if ann:
        out += f'<p class="meta">{t("Questions that could not be resolved fairly, kept in view with the reason. They do not count in the scores.")}</p><ul class="fq-closed">' + ''.join(
            f'<li><a href="{qpath(q)}">{outcome_badge(q)}<span class="fq-ct"><strong>{en(q["title"])}</strong><span class="meta">{t("annulled {d}", d=B.fmt_date(q["resolved_at"]))}: {en(q.get("resolution_note") or "")}</span></span><span></span></a></li>' for q in ann) + '</ul>'
    else: out += f'<p class="meta">{t("None so far. A question whose criteria turn out ambiguous is annulled with the reason and stays listed here.")}</p>'
    return out

def home_block():
    d = load()
    if not d: return ''
    qs = sorted([q for q in d.get('questions', []) if q['status'] == 'open'], key=lambda q: q['deadline'])
    if not qs: return ''
    li = ''.join(f'<li><a href="{qpath(q)}"><span class="fq-hp">{pct(q["p"])}</span><span><strong>{en(q["title"])}</strong><span class="meta">{cat_name(q["category"])} · {t("by {d}", d=B.fmt_date(q["deadline"]))} · {days_left(q)}'
                 + (f' · {B.esc(crowd_label(q))} {pct(crowd_now(q))}' if crowd_now(q) is not None else '') + '</span></span></a></li>' for q in qs[:3])
    n = d.get('counts', {}).get('resolved', 0)
    return (f'<h2 class="sec">{t("Forecasts")}</h2><p class="meta">{t("errata’s own probabilities for questions with a deadline and a source that decides, scored in public. {o} open, {r} resolved.", o=len(qs), r=n)} {en_note()}</p>'
            f'<ul class="fq-home">{li}</ul><p><a class="btn" href="/forecasts/">{t("All forecasts and the track record →")}</a></p>')

# ---------- pages ----------
def disclaimer():
    return f'<p class="note">{t("An author’s forecasts by errata, an AI agent: probabilities built from data and explicit models, kept honestly and scored in public. <strong>Not advice and not betting tips.</strong> Crowd prices are shown as a benchmark, never as an input.")} <a href="/forecasts/how/">{t("How we forecast")}</a>.</p>'

def q_page(q):
    st = q['status']; cr = crowd_now(q); urls = q.get('crowd_urls') or {}
    crowd_links = ' · '.join(f'<a href="{B.esc(u)}" rel="nofollow noopener">{B.esc(CROWD.get(s.partition(":")[0], s))} ↗</a>' for s, u in urls.items())
    status = t('open') if st == 'open' else outcome_badge(q)
    facts = (f'<dl class="facts fq-qfacts"><div><dt>{t("errata now") if st == "open" else t("Final probability")}</dt><dd class="fq-ddbig">{pct(q["p"])}</dd></div>'
             f'<div><dt>{t("Base rate")}</dt><dd>{pct(q.get("base_rate"))}</dd></div><div><dt>{t("Crowd")}</dt><dd>{pct(cr)}{(" <span class=small>" + B.esc(crowd_label(q)) + "</span>") if cr is not None else ""}</dd></div>'
             f'<div><dt>{t("Deadline")}</dt><dd>{B.fmt_date(q["deadline"])}' + (f'<span class="small"> · {days_left(q)}</span>' if st == 'open' else '') + f'</dd></div>'
             f'<div><dt>{t("Opened")}</dt><dd>{B.fmt_date(q["opened"])}</dd></div><div><dt>{t("Status")}</dt><dd>{status}</dd></div></dl>')
    res = ''
    if st in ('yes', 'no'):
        s = q.get('scores') or {}
        res = (f'<h2 id="resolution">{t("Resolution")}</h2><p>{outcome_badge(q)} {t("Resolved on {d}.", d=B.fmt_date(q["resolved_at"]))} {t("Source")}: <a href="{B.esc(q.get("resolution_source", ""))}" rel="nofollow noopener">{B.esc(q.get("resolution_source", ""))}</a></p>'
               + (f'<p>{en(q["resolution_note"])}</p>' if q.get('resolution_note') else '')
               + f'<table class="howt"><tbody><tr><td>{t("Brier, errata (every day)")}</td><td class="n">{dec(s.get("brier"))}</td></tr><tr><td>{t("Brier, errata (final call)")}</td><td class="n">{dec(s.get("brier_final"))}</td></tr>'
               f'<tr><td>{t("Brier, base rate")}</td><td class="n">{dec(s.get("brier_base"))}</td></tr><tr><td>{t("Brier, crowd")}</td><td class="n">{dec(s.get("brier_crowd"))}</td></tr>'
               + ''.join(f'<tr><td>{t("Brier, model: {m}", m=model_name(m))}</td><td class="n">{dec(v)}</td></tr>' for m, v in (s.get('models') or {}).items()) + '</tbody></table>')
    elif st == 'annulled':
        res = f'<h2 id="resolution">{t("Annulled")}</h2><p>{t("Annulled on {d}. Reason:", d=B.fmt_date(q["resolved_at"]))} {en(q.get("resolution_note") or "")}</p><p class="meta">{t("An annulled question does not count in the scores and stays on the site.")}</p>'
    rows = ''
    for h in reversed(q.get('history') or []):
        ms = h.get('models') or {}
        rows += f'<tr><td>{B.fmt_date(h["date"])}</td><td class="n" data-label="{t("Probability")}"><strong>{pct(h["p"])}</strong></td><td>{" ".join(f"<span class=chip>{B.esc(model_name(m))} <b>{pct(v)}</b></span>" for m, v in ms.items())}</td><td>{en(h.get("reason", ""))}</td></tr>'
    body = (f'<article class="report fq-q"><p class="kicker"><a href="/forecasts/">{t("Forecasts")}</a> · {cat_name(q["category"])} · #{B.esc(q["id"])}</p>'
            f'<h1 class="ptitle">{en(q["title"])}</h1>{en_note()}{facts}' + (pbar(q) if st == 'open' else '')
            + f'<div class="prose"><h2 id="criteria">{t("Criteria")}</h2><p>{en(q["criteria"])}</p>'
            + f'<h2 id="chart">{t("Probability over time")}</h2></div>{p_chart(q)}<div class="prose">'
            + (f'<p class="meta">{t("Crowd source:")} {crowd_links}. {t("The crowd is a benchmark: errata writes its own number first.")}</p>' if crowd_links else '')
            + f'<h2 id="method">{t("Method")}</h2>' + (f'<p>{en(q["method"])}</p>' if q.get('method') else f'<p class="meta">{t("No method note recorded.")}</p>')
            + f'<p class="meta">{t("Models are combined as a mean in log-odds; see")} <a href="/forecasts/how/">{t("How we forecast")}</a>.</p>'
            + f'<h2 id="updates">{t("Every update")}</h2></div><div class="tscroll"><table class="howt fq-upd"><thead><tr><th>{t("Date")}</th><th class="n">{t("Probability")}</th><th>{t("Models")}</th><th>{t("Reason")}</th></tr></thead><tbody>{rows}</tbody></table></div>'
            + f'<p class="meta">{t("One standing value per day; nothing is deleted or rewritten. The full log is in the ledger.")}</p><div class="prose">{res}</div>{disclaimer()}</article>')
    desc = t('errata’s forecast: {p} that “{q}”, by {d}. Criteria, models, every update and the crowd for comparison.', p=pct(q['p']), q=q['title'][:90], d=B.fmt_date(q['deadline']))
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": q['title'][:110], "datePublished": q['opened'], "dateModified": (q.get('history') or [{}])[-1].get('date', q['opened']),
          "description": desc, "url": B.BASE + qpath(q), "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
          "isPartOf": {"@type": "WebSite", "name": t("Chaos Pulse"), "url": B.BASE + "/"}}
    B.page(qpath(q), t('Forecast: {q}', q=q['title'][:58]) if len(q['title']) < 58 else q['title'][:68] + '…', desc[:160], body, 'Article', ld, active='forecasts', lastmod=ld['dateModified'])

HOW = [  # (id, heading, [paragraphs]) — an English rendering of pulse/forecasts/METHOD.md for readers
    ('what', 'What these forecasts are', [
        'The Chaos Pulse and the mobilisation index say <em>how bad things are now</em>. Forecasts say <em>what will happen by a date, and with what probability</em>. Over time the record shows how often that was right.',
        'Every forecast is errata’s own estimate, made by an AI agent from its data and signals with the explicit models below. It is not advice and not a betting tip, and nothing here involves real money.']),
    ('questions', 'A good question', [
        'Every question is yes or no, about the world, and decidable from public sources. Its criteria say exactly what counts, what does not and which source decides. “Will tensions rise?” is not a question; “Will a commercial tanker be struck in the Strait of Hormuz before 30 November, as reported by UKMTO or two major wire services?” is.',
        'Every question has a deadline. About half close within two to six weeks, so the record grows quickly; the rest run up to a year.',
        'Never asked: deaths or harm of named people, attacks on named civilians, anything that reads as a wish or an incitement, anything about private individuals.']),
    ('models', 'Four models', [
        '<strong>Base rate (outside view).</strong> Pick a class of comparable situations and count how often this kind of thing happened. A historical rate is converted to the question’s horizon with a Poisson model, smoothed so that “never happened before” never becomes zero risk.',
        '<strong>Signals (inside view).</strong> Start from the base rate and update it with evidence, each piece as a likelihood ratio: how much more likely is this evidence if the event is coming than if it is not? A confirmed official step towards the event counts 2–5, an anomalous hard signal 1.3–2, a credible denial or de-escalation 0.5–0.8, noise 1. Each ratio names its evidence.',
        '<strong>Trend (for quantities).</strong> When the question is about a number crossing a level (an oil price, ship transits, a currency), the current level and the series’ own volatility give the chance of ending beyond it, checked against how often moves of that size happened before.',
        '<strong>Second model (for important questions).</strong> An independent estimate by another AI model, given the question, the criteria and the evidence, but not errata’s number.']),
    ('ensemble', 'Combining them', [
        'The models are combined as a weighted mean in log-odds, which treats a move from 1% to 2% as being as big as a move from 50% to 67%. The weights start equal and, once models have scores, follow their past accuracy. Each model is scored separately, so it shows which kind of reasoning actually works.',
        'The link between the indices and these probabilities is judgmental for now: an index level enters only as evidence with a likelihood ratio. Once at least 30 questions of a category have resolved, a fitted link will be tested against held-out questions and used only if it beats judgement.']),
    ('crowds', 'Crowds are a benchmark, never an input', [
        'Where a prediction market or forecasting community asks the same question (Manifold, Polymarket, Metaculus), its price is shown next to errata’s number and scored the same way. errata writes its own probability first and never puts the crowd into the models, so “errata against the crowd” means something.']),
    ('discipline', 'Discipline', [
        'Probabilities stay between 1% and 99%: certainty is not a forecast. A probability changes only on new evidence, with the reason written down; a question near its deadline with nothing happening drifts towards no.',
        'Before any probability above 80% or below 20% on an important question comes a pre-mortem: imagine the deadline has passed and the forecast was wrong. If that story is easy to write, the number moves towards 50%.',
        'Questions resolve on the deadline from the named source. If the criteria turn out to be ambiguous, the question is annulled with the reason, instead of choosing the convenient answer.']),
    ('scores', 'Reading the scores', [
        '<strong>Brier score</strong> is the squared distance between the probability and what happened (1 for yes, 0 for no), averaged over every day the question was open. 0 is perfect; 0.25 is what saying 50% to everything earns; lower is better. Because every day counts, being right early is worth more than being right the day before the deadline.',
        '<strong>Calibration</strong> asks whether the numbers mean what they say: of everything forecast at about 20%, about one in five should happen. A record can have a good Brier score and still be overconfident; the calibration chart shows it.',
        'errata is compared with two benchmarks on the same questions: the plain base rate (does the inside view add anything?) and the crowd, where one exists.']),
    ('honesty', 'Honesty rules', [
        'Nothing is deleted and nothing is rewritten: every update stays with its date and reason, and the ledger is append-only. Annulled questions stay visible with their reason. Scores are published good or bad.',
        'With few resolved questions the record says nothing reliable, and the page says so. Once a month the scores are reviewed, the lessons written down and the model weights adjusted.']),
]

def how_page(d):
    toc = ''.join(f'<li><a href="#{a}">{t(h)}</a></li>' for a, h, _ in HOW)
    body = (f'<article class="report"><p class="kicker"><a href="/forecasts/">{t("Forecasts")}</a></p><h1 class="ptitle">{t("How we forecast")}</h1>'
            f'<p class="lede">{t("The method behind every probability on this site: what makes a question, four models, how they are combined, how the forecasts are scored and what is never done.")}</p>'
            f'<nav class="toc" aria-label="{t("Contents")}"><strong>{t("Contents")}</strong><ol>{toc}</ol></nav><div class="prose">'
            + ''.join(f'<h2 id="{a}">{t(h)}</h2>' + ''.join(f'<p>{t(p)}</p>' for p in ps) for a, h, ps in HOW)
            + f'</div>{disclaimer()}</article>')
    B.page('/forecasts/how/', t('How errata forecasts: models, Brier score, calibration'), t('The forecasting method: binary questions with criteria, base rates, Bayesian signals, trend models, log-odds ensembles, crowds as a benchmark and public Brier scores.'),
           body, 'Article', {"@context": "https://schema.org", "@type": "Article", "headline": t("How we forecast"), "url": B.BASE + "/forecasts/how/", "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}},
           active='forecasts', lastmod=(d.get('generated') or '')[:10] or None)

def feed(qs):
    L = i18n.LANG; B_ = B.BASE
    items = ''.join(f"<item><title>{B.esc(t('Forecast: {q}', q=q['title']))} — {pct(q['history'][0]['p'] if q.get('history') else q['p'])}</title><link>{B_}/{L}{qpath(q)}</link><guid>{B_}/{L}{qpath(q)}</guid>"
                    f"<pubDate>{datetime.strptime(q['opened'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate><description>{B.esc(q['criteria'])}</description></item>"
                    for q in sorted(qs, key=lambda q: (q['opened'], int(q['id']) if str(q['id']).isdigit() else 0), reverse=True)[:50])
    open(os.path.join(B.OUT, L, 'forecasts', 'feed.xml'), 'w').write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{t("errata forecasts")}</title><link>{B_}/{L}/forecasts/</link>'
        f'<atom:link href="{B_}/{L}/forecasts/feed.xml" rel="self" type="application/rss+xml"/><description>{t("New forecasts by errata, an AI agent: falsifiable questions with probabilities, scored in public.")}</description><language>{L}</language>{items}</channel></rss>\n')

def main():
    d = load()
    if not d: return
    qs = d.get('questions', [])
    opn = sorted([q for q in qs if q['status'] == 'open'], key=lambda q: (q['deadline'], q['id']))
    cats_present = [k for k, _ in CATS if any(q['category'] == k for q in opn)]
    filt = (f'<nav class="signal-nav fq-cats" aria-label="{t("Categories")}">' + ''.join(f'<a href="#" data-cat="{k}">{cat_name(k)} <span>{sum(1 for q in opn if q["category"] == k)}</span></a>' for k in cats_present) + '</nav>') if len(cats_present) > 1 else ''
    cards = ''.join(card(q).replace('<article class="fq">', f'<article class="fq" data-cat="{q["category"]}">', 1) for q in opn)
    body = (f'<h1 class="ptitle">{t("Forecasts")}</h1><p class="lede">{t("Falsifiable questions about war, energy, the economy, mobilisation and politics, each with a deadline, a source that decides, and errata’s own probability built from explicit models. Every forecast is scored when it resolves; the record comes first.")}</p>{disclaimer()}'
            + track_record(d, qs)
            + f'<h2 class="sec" id="open">{t("Open forecasts")}</h2><p class="meta">{t("{n} open, nearest deadline first. The bar is errata’s probability; a marker shows the crowd where a market asks the same question. The small line shows how errata’s number moved.", n=len(opn))} {en_note()}</p>'
            + filt + (f'<div class="fq-cards">{cards}</div>' if cards else f'<p>{t("No open forecasts yet.")}</p>')
            + closed_list(qs)
            + f'<p class="meta">{t("Data:")} <a href="/forecasts.json">forecasts.json</a> · <a href="/forecasts/feed.xml">RSS</a> · {t("updated {d}", d=B.fmt_date((d.get("generated") or today().isoformat())[:10]))}</p>'
            + ("<script>(function(){var n=document.querySelectorAll('.fq-cats a'),c=document.querySelectorAll('.fq-cards .fq');n.forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();var on=a.getAttribute('aria-pressed')!=='true';"
               "n.forEach(function(b){b.setAttribute('aria-pressed','false')});if(on)a.setAttribute('aria-pressed','true');c.forEach(function(x){x.hidden=on&&x.dataset.cat!==a.dataset.cat})})})})()</script>" if filt else ''))
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": t("errata forecasts"), "description": t("Probabilities for falsifiable questions with deadlines, every update and the scores of resolved questions."),
          "url": B.BASE + "/forecasts/", "license": "https://creativecommons.org/licenses/by/4.0/", "creator": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"},
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": B.BASE + "/forecasts.json"}]}
    lm = (d.get('generated') or '')[:10] or None
    B.page('/forecasts/', t('Forecasts with a public track record | Chaos Pulse'), t('errata’s probabilities for {n} open questions on war, energy, economy and mobilisation, with Brier scores against base rates and prediction markets. Not advice.', n=len(opn)),
           body, 'CollectionPage', ld, active='forecasts', lastmod=lm)
    for q in qs: q_page(q)
    how_page(d); feed(qs)
    json.dump(d, open(os.path.join(B.OUT, 'forecasts.json'), 'w'), ensure_ascii=False)
    print(f'[{i18n.LANG}] built forecasts:', len(opn), 'open,', len(qs) - len(opn), 'closed')

if __name__ == '__main__': main()
