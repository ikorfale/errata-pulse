#!/usr/bin/env python3
"""Build pulse.errata.page/telegram/ and the Telegram blocks of the home and mobilisation pages.
data/telegram/YYYY-MM-DD.json  one daily snapshot of the Telegram collector: per channel group, the share of the
last 24 hours' posts that touch four topics, against the group's own 14-day norm; subscribers; the most-viewed
matching posts as leads (with an optional English gist in data/telegram/gists.json, keyed by post URL).
Leads are unverified by design: every one is shown with its channel's slant."""
import json, os, glob
from datetime import datetime
import build as B
import i18n
from i18n import t, td
TD = os.path.join(B.D, 'telegram')
TOPICS = [('mobilisation', 'Mobilisation', 'call-ups, summons, deferments, exit bans, reservists'),
          ('escalation', 'Escalation', 'nuclear talk, NATO, ballistic and massive strikes, evacuations'),
          ('energy', 'Energy', 'refineries, tankers, pipelines, fuel prices, blackouts, Hormuz, Red Sea'),
          ('control', 'Control', 'blocking and shutdowns, martial law, censorship, treason and "extremism" cases')]
# group: (section, plain name, who they are, slant shown on every lead)
GROUPS = {
    'official-ru': ('Russia', 'Russian state media and ministries', 'RIA, TASS, Ministry of Defence', 'state channel: says what the government wants said'),
    'official-ru-regional': ('Russia', 'Border governors', 'Belgorod and Kursk regional heads', 'official channel of a regional government'),
    'leaks-ru': ('Russia', 'Russian leak channels', 'Baza, Mash, SHOT and similar', 'leak channel: fast, often unsourced, close to security services'),
    'milblog-ru': ('Russia', 'Russian military bloggers', 'pro-war bloggers such as Rybar and Two Majors', 'pro-war blogger: partisan by design'),
    'independent-ru': ('Russia', 'Independent Russian media', 'Meduza, Mediazona, The Bell, BBC Russian and others in exile', 'independent outlet with an editorial stance; not every post is checked'),
    'regional-ru': ('Russia', 'Russian regional media', 'Fontanka, NGS, E1, 7x7, RFE/RL regional desks', 'regional news outlet'),
    'border-relocation': ('Russia', 'Border and relocation', 'Upper Lars border channel, border-crossing agency, relocation channels', 'community or agency channel; reports are anecdotal'),
    'official-ua': ('Ukraine', 'Ukrainian officials', 'President, General Staff, Air Force, emergency service', 'official channel of a party to the war'),
    'media-ua': ('Ukraine', 'Ukrainian media', 'Ukrainska Pravda, Suspilne, Hromadske, UNIAN, Trukha', 'media of a country at war; some channels are tabloid'),
    'official-il': ('Middle East', 'Israeli military', 'IDF', 'official channel of a party to the war'),
    'media-il': ('Middle East', 'Israeli media', 'ynet alerts, Abu Ali Express, Amit Segal', 'media and commentators of a country at war'),
    'official-ir': ('Middle East', 'Iranian state media', 'Press TV, IRNA, Fars', 'state channel of Iran'),
    'opposition-ir': ('Middle East', 'Iranian opposition media', 'Iran International, BBC Persian, Radio Farda', 'opposition media with a stance against the government'),
    'houthi-ye': ('Middle East', 'Houthi channels', 'military spokesman and al-Masirah', 'channel of an armed movement at war'),
    'axis-media': ('Middle East', 'Media close to the Houthis and Iran', 'al-Mayadeen, Sabereen', 'partisan media aligned with one side'),
}
ORDER = list(GROUPS)
SNAPS = None

def load():
    global SNAPS
    if SNAPS is None:
        SNAPS = []
        for f in sorted(glob.glob(os.path.join(TD, '2*.json'))):
            d = json.load(open(f)); d['date'] = os.path.basename(f)[:10]; SNAPS.append(d)
    return SNAPS

def gists():
    f = os.path.join(TD, 'gists.json'); return json.load(open(f)) if os.path.exists(f) else {}

def share_series(group, topic):
    out = []
    for d in load():
        chs = [c for c in d['channels'].values() if c['group'] == group]; tot = sum(c['posts_24h'] for c in chs)
        if tot: out.append((d['date'], sum(c['counts'][topic] for c in chs) / tot))
    return out

def cell(sig, group, topic):
    label = t(dict((k, n) for k, n, _ in TOPICS)[topic])
    st, phrase = ('none', t('Norm not built yet.')) if sig.get('baseline') is None else B.plain(sig['share'] / sig['baseline'] if sig['baseline'] else (9 if sig['share'] else 1), sig.get('anomaly'), what='its norm')
    nrm = t('norm {p}', p=i18n.num_pct(sig['baseline'])) if sig.get('baseline') is not None else ''
    ser = share_series(group, topic)
    return (f'<td class="tgcell c-{st}" title="{B.esc(phrase)}" data-label="{label}"><span class="pct">{i18n.num_pct(sig["share"])}</span><span class="nrm">{nrm}</span>'
            f'{B.pill(st) if st != "none" else ""}{B.sparkline(ser, sig.get("anomaly")) if len(ser) >= 3 else ""}</td>')

def table(snap, groups=None, topics=None):
    topics = topics or TOPICS; sigs = {(s['group'], s['topic' if 'topic' in s else 'family']): s for s in snap['signals']}
    present = [g for g in ORDER if any(k[0] == g for k in sigs)] + sorted({k[0] for k in sigs} - set(ORDER))
    if groups: present = [g for g in present if g in groups]
    h = f'<thead><tr><th>{t("Channel group")}</th>' + ''.join(f'<th>{t(n)}<span class="gdesc">{t(d)}</span></th>' for _, n, d in topics) + '</tr></thead><tbody>'
    sect = None
    for g in present:
        meta = GROUPS.get(g, ('Other', g, '', 'unclassified channel'))
        if meta[0] != sect and not groups: sect = meta[0]; h += f'<tr><td class="tgsect" colspan="{len(topics) + 1}">{t(sect)}</td></tr>'
        n = sum(1 for c in snap['channels'].values() if c['group'] == g)
        h += f'<tr><th scope="row"><span class="gname">{B.esc(t(meta[1]))}</span><span class="gdesc">{B.esc(t(meta[2]))} · {n} {i18n.plural(n, "channel", "channels")}</span></th>'
        h += ''.join(cell(sigs[(g, k)], g, k) if (g, k) in sigs else '<td>—</td>' for k, _, _ in topics) + '</tr>'
    return f'<div class="chart" tabindex="0" role="region" aria-label="{t("Topic share by channel group")}"><table class="tgtable">{h}</tbody></table></div>'

def lead_card(p, topic):
    meta = GROUPS.get(p['group'], ('', p['group'], '', 'unclassified channel')); g = gists().get(p['url'])
    if g and i18n.LANG != 'en' and p.get('text') and _lang_of(p['text']) == i18n.LANG: g = None     # the original is already in the reader's language
    return (f'<article class="lead"><div class="lh"><b>@{B.esc(p["channel"])}</b><span>{B.esc(t(meta[1]))}</span><span>{B.fmt_date(p["time"][:10])} {p["time"][11:16]} UTC</span></div>'
            f'<p class="warn">{t("Unverified lead")} · {B.esc(t(meta[3]))}</p>'
            + (f'<p class="gist"><span class="small">{t("English gist (machine translation):")}</span> <span lang="en">{B.esc(g)}</span></p>' if g else '')
            + f'<blockquote lang="und">{B.esc(p["text"])}{"…" if len(p["text"]) >= 280 else ""}</blockquote>'
            f'<p class="lf"><span>{B.num(p["views"])} {t("views")}</span><a href="{B.esc(p["url"])}" rel="nofollow noopener">{t("Open the original ↗")}</a></p></article>')

def _lang_of(text):
    """Rough script check: Cyrillic text with Ukrainian letters is 'uk', other Cyrillic 'ru'."""
    cyr = sum(1 for ch in text if '\u0400' <= ch <= '\u04ff')
    if cyr < len(text) * 0.3: return 'other'
    return 'uk' if any(ch in text for ch in 'іїєґІЇЄҐ') else 'ru'

def subs_table(snap, k=12):
    first = {}
    for d in load():
        for ch, c in d['channels'].items():
            if c.get('subscribers'): first.setdefault(ch, (d['date'], c['subscribers']))
    rows = []
    for ch, c in snap['channels'].items():
        if ch in first and c.get('subscribers'): rows.append((c['subscribers'] / first[ch][1] - 1, ch, c, first[ch][0]))
    rows.sort(key=lambda r: (-abs(r[0]), -r[2]['subscribers']))
    tr = ''.join(f'<tr><td>@{B.esc(ch)}</td><td>{B.esc(t(GROUPS.get(c["group"], ("", c["group"]))[1]))}</td><td class="n">{B.num(c["subscribers"])}</td><td class="n">{("+" if g >= 0 else "") + i18n.num_pct(g, 1)}</td><td class="n">{B.fmt_date(d0)}</td></tr>' for g, ch, c, d0 in rows[:k])
    return f'<div class="chart" tabindex="0" role="region" aria-label="{t("Subscriber change")}"><table class="subs"><thead><tr><th>{t("Channel")}</th><th>{t("Group")}</th><th class="n">{t("Subscribers")}</th><th class="n">{t("Change")}</th><th class="n">{t("Since")}</th></tr></thead><tbody>{tr}</tbody></table></div>'

def notable(snap, k=4):
    """Short list per topic of the cells furthest above norm (or, before a norm exists, the highest shares)."""
    out = ''
    for k_, n, _ in TOPICS:
        ss = [s for s in snap['signals'] if s['family'] == k_ and s['share'] > 0]
        ss.sort(key=lambda s: -(s['share'] / s['baseline'] if s.get('baseline') else s['share']))
        li = ''.join(f'<li>{B.esc(t(GROUPS.get(s["group"], ("", s["group"]))[1]))}: <strong>{i18n.num_pct(s["share"])}</strong>'
                     + (f' <span class="small">{t("vs norm {p}", p=i18n.num_pct(s["baseline"]))}</span>' if s.get('baseline') is not None else '') + '</li>' for s in ss[:k])
        out += f'<div><h4>{t(n)}</h4><ul>{li or "<li class=small>" + t("no posts on this topic") + "</li>"}</ul></div>'
    return f'<div class="tgmini">{out}</div>'

def status_line(snap):
    days = snap.get('baseline_days', 0); an = [s for s in snap['signals'] if s.get('anomaly')]
    s = t('Snapshot of {d}: {n} public channels in {g} groups.', d=B.fmt_date(snap["date"]), n=len(snap["channels"]), g=len({c["group"] for c in snap["channels"].values()})) + ' '
    if days < 5: s += t('The norm is still building: {n} of the 14 days collected, anomalies are flagged from day 6. Until then the shares are shown without a verdict.', n=days + 1)
    else: s += (f'<strong>{t("{n} topic–group pair(s) far above their norm.", n=len(an))}</strong>' if an else t('No topic–group pair is far above its norm today.'))
    return s

def home_block():
    if not load(): return ''
    snap = load()[-1]
    return (f'<h2 class="sec">Telegram</h2><p class="meta">{status_line(snap)} {t("Share of each group’s posts in the last 24 hours that touch a topic.")}</p>{notable(snap, 3)}'
            f'<p><a class="btn" href="/telegram/">{t("All channel groups, charts and leads →")}</a></p>')

def mobil_block():
    if not load(): return ''
    snap = load()[-1]; grp = ['official-ru', 'official-ru-regional', 'leaks-ru', 'milblog-ru', 'independent-ru', 'regional-ru', 'border-relocation']
    leads = snap.get('leads', {}).get('mobilisation', [])
    leads = [p for p in leads if p['group'] in grp][:4] or leads[:2]
    return (f'<h2 class="sec">Telegram</h2><p class="meta">{t("How much Russian channels talk about mobilisation: the share of each group’s posts in the last 24 hours, against the group’s own {n}.", n=B.term("norm"))} {status_line(snap)}</p>'
            + table(snap, grp, [TOPICS[0], TOPICS[3]])
            + (f'<h3 class="sub">{t("Most-viewed posts on mobilisation")}</h3><p class="meta">{t("Leads, not facts: each is unverified and comes from a channel with a slant.")}</p><div class="leads">' + ''.join(lead_card(p, 'mobilisation') for p in leads) + '</div>' if leads else '')
            + f'<p><a class="btn" href="/telegram/">{t("The full Telegram desk →")}</a></p>')

def main():
    if not load(): return
    snap = load()[-1]; L = snap.get('leads', {})
    tl = ''.join(f'<section class="fam" id="leads-{k}"><h3>{t(n)} <span class="cnt">{t(d)}</span></h3><div class="leads">' + ''.join(lead_card(p, k) for p in L.get(k, [])) + '</div></section>' for k, n, d in TOPICS if L.get(k))
    nch = len(snap["channels"])
    body = f"""<h1 class="ptitle">Telegram</h1><p class="lede">{t('What {n} public Telegram channels talk about, day by day: Russian officials, leak channels, military bloggers and independent media, Ukraine, Israel, Iran and the Houthis. Not what they say is true, but <em>how much</em> of their output turns to mobilisation, escalation, energy or control, compared with their own usual level.', n=nch)}</p>
<p class="note">{status_line(snap)} {t('A change in what partisan channels talk about is a signal precisely because they are partisan; it is a lead to check, never a fact. Read openly from public web previews; no account, no private chats.')}</p>
<h2 class="sec">{t('Topics by channel group')}</h2><p class="meta">{t('Each cell: the share of the group’s posts in the last 24 hours that touch the topic, its {n}, a colour verdict and, from the third day, a small line of the daily history. Hover a cell for the plain reading.', n=B.term("norm"))}</p>{table(snap)}
<h2 class="sec">{t('Notable posts')}</h2><p class="meta">{t('The most-viewed posts of the day touching each topic. <strong>Every one is an unverified lead from a channel with a slant</strong>, shown in the original language with a link to the source; an English gist appears when one has been made.')}</p>{tl or f'<p>{t("No leads in this snapshot.")}</p>'}
<h2 class="sec">{t('Audience')}</h2><p class="meta">{t('Subscriber counts as shown on each channel’s public page, and the change since the first day it was collected. Sudden growth of leak or relocation channels can be a sign of public worry.')}</p>{subs_table(snap)}
<h2 class="sec">{t('How it works')}</h2><div class="prose"><ul><li>{t('Once a day the collector reads the public preview page (t.me/s/…) of each channel and keeps the posts of the last 24 hours.')}</li>
<li>{t('A post counts for a topic if it contains one of a list of word stems in Russian, Ukrainian, English, Persian, Arabic or Hebrew (for example <em>повестк</em>, <em>мобілізац</em>, <em>hormuz</em>). Recurring footers and the legally required “foreign agent” labels are cut first, so they do not count.')}</li>
<li>{t('The share is computed per group, not per channel, so one prolific channel cannot dominate. The norm is the median share of the group’s last 14 days; a cell is an anomaly when the share is at least twice the norm and at least 5 points above it.')}</li>
<li>{t('What it does not prove: a topic share says nothing about whether the posts are true, and keyword matching has noise. It feeds the <a href="/methodology/">components</a> as evidence, never as a formula.')}</li></ul></div>
<p class="meta">{t('Data:')} <a href="/telegram/latest.json">latest.json</a> {t('(aggregates and leads of the latest day).')}</p>"""
    B.page('/telegram/', t('Telegram signals: what {n} channels talk about | Chaos Pulse', n=nch), t('Daily share of posts on mobilisation, escalation, energy and control in Russian, Ukrainian, Israeli, Iranian and Houthi Telegram channels, against each group’s own norm.'), body, 'CollectionPage', active='telegram', lastmod=snap['date'])
    os.makedirs(os.path.join(B.OUT, 'telegram'), exist_ok=True)
    pub = {k: snap[k] for k in ('date', 'signals', 'volume', 'baseline_days', 'leads') if k in snap}
    pub['channels'] = {ch: {k: c[k] for k in ('group', 'posts_24h', 'counts', 'subscribers')} for ch, c in snap['channels'].items()}
    json.dump(pub, open(os.path.join(B.OUT, 'telegram', 'latest.json'), 'w'), ensure_ascii=False)
    print('built telegram:', snap['date'], len(snap['channels']), 'channels')

if __name__ == '__main__': main()
