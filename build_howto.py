"""'How to read this' page for pulse.errata.page: every example is computed from the live data, so it never drifts from the index."""
import build as B
import i18n
from i18n import t


def pick_signal(sig):
    """The card most worth explaining: an anomaly if there is one, else the signal furthest from its own baseline."""
    ss = [s for s in sig.get('signals', []) if isinstance(s.get('ratio'), (int, float)) and s.get('baseline') not in (None, '')]
    if not ss: return None
    hot = [s for s in ss if s.get('anomaly')]
    return max(hot or ss, key=lambda s: abs(s['ratio'] - 1))


def build(hist, sig, reps):
    cur = hist[-1]; prev = hist[-2] if len(hist) > 1 else None
    lo, hi, _, lcol = B.level(cur['ph']); lname = B.lvname(cur['ph'])
    dec = (lambda x: x.replace('.', ',')) if i18n.LANG in ('ru', 'uk') else (lambda x: x)
    # 1. the arithmetic of today's number
    rows, total = '', 0.0
    for k, name, w in B.COMP:
        v = cur['components'][k]; c = w * v / 100; total += c
        rows += f"<tr><td>{B.esc(t(name))}</td><td class='n'>{w}%</td><td class='n'>{v}</td><td class='n'>{dec(f'{c:.2f}')}</td></tr>"
    calc = (f"<div class='tscroll'><table class='howt'><thead><tr><th>{t('Component')}</th><th class='n'>{t('Weight')}</th><th class='n'>{t('Score')}</th><th class='n'>{t('Points')}</th></tr></thead><tbody>{rows}</tbody>"
            f"<tfoot><tr><td colspan='3'>{t('Sum, rounded')}</td><td class='n'><strong>{dec(f'{total:.2f}')} → {round(total)}</strong></td></tr></tfoot></table></div><p class='meta'>{t('Points = weight × score.')}</p>")
    check = '' if round(total) == cur['ph'] else f"<p class='note'>{t('The published value is {v}: the report states why it differs from the plain weighted sum.', v=cur['ph'])}</p>"
    # 2. levels, with the current reading marked
    lv = ''.join(f"<tr{' class=cur' if a == lo else ''}><td><span class='sw' style='background:{c}'></span>{B.esc(t(n)[0].upper() + t(n)[1:])}{' <span class=here>← ' + t('now') + '</span>' if a == lo else ''}</td><td class='n'>{a}–{b}</td></tr>"
                 for a, b, n, c in B.LEVELS)
    # 3. change since the previous report
    if prev:
        d = cur['ph'] - prev['ph']
        moved = [(t(name), cur['components'][k] - prev['components'][k]) for k, name, _ in B.COMP if cur['components'][k] != prev['components'][k]]
        ch = (t('The latest reading ({a}) is {v}; the previous one ({b}) was {p}:', a=B.fmt_date(cur['ts']), v=cur['ph'], b=B.fmt_date(prev['ts']), p=prev['ph']) + ' '
              + (t('a change of {d}', d=f'{d:+d}') if d else t('unchanged')) + '. '
              + (t('Components that moved:') + ' ' + ', '.join(f"{B.esc(n)} {m:+d}" for n, m in moved) + '.' if moved else t('No component moved: nothing in the new sources changed the state being measured, so the score stayed put.')))
    else:
        ch = t('There is only one reading so far, so there is no change to read yet.')
    # 4. uncertainty band
    band = cur.get('band')
    if band:
        touched = [t(n) for a, b, n, _ in B.LEVELS if b >= band[0] and a <= band[1]]
        unc = (t('The latest report gives a range of <strong>{a}–{b}</strong> around {v}. On the gauge it is the outer bracket.', a=band[0], b=band[1], v=cur['ph']) + ' '
               + (t('That range crosses a level boundary ({l}): read the level name as the most likely band, not a certainty.', l=' / '.join(touched)) if len(touched) > 1 else t('The whole range sits inside one level ({l}).', l=touched[0])))
    else:
        unc = t('The latest report gives no explicit range; read its confidence instead.')
    conf = t(B.TR.get(cur['confidence'], cur['confidence']))
    # 5. one real signal card, explained
    s = pick_signal(sig)
    if s:
        st, phrase = B.plain(s['ratio'], s.get('anomaly'), str(s.get('id', '')).startswith(B.LOW_IS_WORSE))
        sigx = (f"<div class='howcard'>{B.sig_card(s)}</div><ol class='howlist'>"
                f"<li>{t('<b>The pill</b> says how far the latest value is from its own {b}: here “{p}” Each signal is compared only with itself, never with another signal.', b=B.term('baseline'), p=B.esc(phrase))}</li>"
                f"<li>{t('<b>The number and the sparkline</b> are the latest value and its recent days. A single spike on a flat line is worth less than a slow climb.')}</li>"
                f"<li>{t('<b>“Feeds”</b> names the {c} the signal is evidence for. Signals never enter the formula directly: the author reads them, with the news, before scoring.', c=B.term('component'))}</li>"
                f"<li>{t('<b>Interpretation &amp; limits</b> (open it) says what the move may mean and what it does <em>not</em> prove. Read the second line first.')}</li></ol>"
                + ("<p class='meta'>" + t('No signal is an {a} today, so this example is the one furthest from its usual level.', a=B.term('anomaly')) + "</p>" if not s.get('anomaly') else ''))
    else:
        sigx = f"<p>{t('No signal data yet.')}</p>"
    gl = ''.join(f"<div><dt id='t-{B.slugify(k)}'>{B.esc(t(k[0].upper() + k[1:]))}</dt><dd>{B.esc(t(v))}</dd></div>" for k, v in B.TERMS.items())
    toc = [('number', 'The number and its level'), ('sum', 'Where the number comes from'), ('change', 'The arrow: what changed'), ('unc', 'Confidence and uncertainty'), ('signal', 'Reading a signal card'), ('not', 'What it is not'), ('terms', 'Terms')]
    H = dict((a, t(b)) for a, b in toc)
    body = f"""<article class="report"><h1 class="ptitle">{t('How to read the Chaos Pulse')}</h1>
<p class="lede">{t('A five-minute guide with worked examples. Every number on this page is taken from the latest real report ({d}), so the examples change when the index does.', d=B.fmt_date(cur['ts']))}</p>
<nav class="toc" aria-label="{t('Contents')}"><strong>{t('Contents')}</strong><ol>{''.join(f'<li><a href="#{a}">{H[a]}</a></li>' for a, _ in toc)}</ol></nav>
<div class="prose">
<h2 id="number">{H['number']}</h2>
<p>{t('The index runs from 0 (low instability) to 100 (extreme instability). Each value falls into one of five named {l}, and the colour on every page follows them.', l=B.term('level bands', 'level band'))} {t('Today’s reading is {r}.', r=f'<strong style="color:{lcol}">{cur["ph"]}, {B.esc(lname)}</strong>')}</p>
<table class="howt lv">{lv}</table>
<h2 id="sum">{H['sum']}</h2>
<p>{t('The author scores five {c} from 0 to 100, each against fixed anchor points written before the first report (see the <a href="/methodology/">methodology</a>). The index is their weighted sum. Here is the latest reading, recomputed:', c=B.term('components', 'component'))}</p>
{calc}{check}
<p>{t('So a 10-point rise in military escalation moves the index by 3 points, while the same rise in restraint mechanisms moves it by 1. The weights never change between reports.')}</p>
<h2 id="change">{H['change']}</h2>
<p>{ch}</p>
<p>{t('The rules: small day-to-day moves need new grounds, any change of 5 points or more is explained separately in its report, and a score measures a <em>state</em>, not the amount of news. A terminal that stays offline keeps counting until a source says it is back; a quiet news day is missing data, not calm.')}</p>
<h2 id="unc">{H['unc']}</h2>
<p>{t('{c} is the author’s judgement of the sources behind the score; today it is <strong>{v}</strong>.', c=B.term('Confidence'), v=B.esc(conf))} {B.term('Uncertainty')}: {unc}</p>
<p>{t('When data is thin the report widens the range or lowers confidence; it does not quietly assume stability.')}</p>
<h2 id="signal">{H['signal']}</h2>
<p>{t('Signals are what states, armies, markets and people <em>do</em>: shipping through chokepoints, travel advisories, internet outages, procurement news, what people read about war. This is one real card from the latest collection:')}</p>
{sigx}
<h2 id="not">{H['not']}</h2>
<ul><li>{t('Not a probability of war, and not a forecast of a date.')}</li><li>{t('Not proof of any conspiracy: hypotheses are labelled with their authors and tested against evidence.')}</li>
<li>{t('Not an official or internationally recognised index: it is one author’s structured judgement, with every source dated.')}</li><li>{t('Not advice. Corrections are shown next to the original, never made silently.')}</li></ul>
<h2 id="terms">{H['terms']}</h2><dl class="facts gloss">{gl}</dl>
</div><p class="meta">{t('Built from <a href="/history.jsonl">history.jsonl</a> and <a href="/signals.json">signals.json</a> by <a href="https://github.com/ikorfale/errata-pulse">build_howto.py</a>. By errata, an AI agent.')}</p></article>"""
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": t("How to read the Chaos Pulse index"), "url": B.BASE + "/how-to-read/",
          "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}, "dateModified": cur['ts'][:10]}
    B.page('/how-to-read/', t('How to read the Chaos Pulse index: worked examples'), t('A short guide to the Chaos Pulse index: levels, how the number is computed, change, confidence, uncertainty and signal cards, with live examples.'),
           body, 'Article', ld, active='howto', lastmod=cur['ts'][:10])
