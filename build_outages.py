"""Outage Watch page (/outages/): outages of government networks, banks and payment systems, clouds and the internet.
data/outages/latest.json  official incidents only (status pages of the operators themselves, IODA network signals),
                          exported by the collector's public step; unverified news leads are never on this page.
data/outages/digests/YYYY-MM-DD.md  daily digest of verified outages (written by the evening Chaos Pulse pass);
                          data/outages/digests/ru/YYYY-MM-DD.md when translated."""
import os, json, glob
import build as B
import i18n

def L(en, ru): return ru if i18n.LANG == 'ru' else en
SECTORS = [('payments', 'Payments and fintech', 'Платежи и финтех'), ('banking', 'Banking infrastructure', 'Банковская инфраструктура'),
           ('crypto', 'Crypto exchanges', 'Криптобиржи'), ('cloud', 'Clouds and hosting', 'Облака и хостинг'),
           ('comms', 'Communications', 'Связь и коммуникации'), ('ai', 'AI services', 'ИИ-сервисы'), ('dev', 'Developer platforms', 'Платформы для разработчиков'),
           ('consumer', 'Consumer platforms', 'Потребительские сервисы')]
IMPACT = {'critical': ('Critical', 'Критично', 3), 'major': ('Major', 'Серьёзно', 2), 'minor': ('Minor', 'Частично', 1)}

def when(iso):
    if not iso: return ''
    return B.esc(iso[:16].replace('T', ' ')) + ' UTC'

def card(i, internet=False):
    imp = IMPACT.get(str(i.get('impact')).lower())
    badge = (L(*imp[:2]) if imp else (L('Network signal', 'Сетевой сигнал') if internet else L('Reported', 'Сообщено')))
    hot = ' is-hot' if (imp and imp[2] >= 2) or (internet and i.get('status') == 'ongoing') else ''
    st = {'ongoing': L('ongoing', 'продолжается'), 'ended': L('ended', 'закончился'), 'investigating': L('investigating', 'выясняют'),
          'identified': L('cause identified', 'причина найдена'), 'monitoring': L('fix applied, monitoring', 'исправлено, наблюдают'),
          'resolved': L('resolved', 'устранено')}.get(i.get('status'), B.esc(i.get('status') or ''))
    reg = f" · {B.esc(i['region'])}" if i.get('region') else ''
    return (f"<article class='sig{hot}'><div class='sh'><span class='badge{' hot' if hot else ''}'>{badge}</span><span class='comp'>{B.esc(i.get('source', ''))}{reg}</span></div>"
            f"<h4>{B.esc(i.get('title', ''))}</h4><p class='sb'>{L('Since', 'С')} {when(i.get('started'))} · {st}</p>"
            + (f"<p class='sn'>{B.esc((i.get('text') or '')[:260])}</p>" if i.get('text') else '')
            + f"<p class='src'><a href='{B.esc(i.get('url') or '#')}' rel='nofollow noopener'>{L('Official status page ↗', 'Официальная страница статуса ↗') if not internet else 'IODA ↗'}</a></p></article>")

def main():
    f = os.path.join(B.D, 'outages', 'latest.json')
    if not os.path.exists(f): return
    d = json.load(open(f))
    os.makedirs(os.path.join(B.OUT, 'data', 'outages'), exist_ok=True); __import__('shutil').copy(f, os.path.join(B.OUT, 'data', 'outages', 'latest.json'))
    off = [i for i in d['open'] if i.get('sector') != 'internet']; net = [i for i in d['open'] if i.get('sector') == 'internet']
    off.sort(key=lambda i: -(IMPACT.get(str(i.get('impact')).lower(), ('', '', 0))[2]))
    title = L('Outage Watch: banks, payments, government networks, clouds', 'Сбои: банки, платежи, госсети, облака')
    desc = L('Outages of banks, payment systems, government networks, clouds and the internet worldwide: official status pages, network signals and a daily digest of verified outages.',
             'Сбои банков, платёжных систем, госсетей, облаков и интернета в мире: официальные страницы статуса, сетевые сигналы и ежедневная сводка проверенных сбоев.')
    body = f"<h1 class='ptitle'>{L('Outage Watch', 'Сбои')}</h1><p class='lede'>{B.esc(L('Who is down right now: banks and payment systems, government networks, clouds, telecom and national internet. Official sources first; news reports only after two independent sources confirm them.', 'Что сейчас не работает: банки и платёжные системы, госсети, облака, связь и интернет целых стран. Сначала официальные источники; сообщения СМИ только после подтверждения двумя независимыми источниками.'))}</p>"
    body += f"<p class='note'>{L('Collected every 15 minutes; this page is rebuilt at least once a day, last snapshot', 'Сбор каждые 15 минут; страница пересобирается не реже раза в день, последний снимок')} {when(d.get('checked'))}. {L('Not continuous watching, and not a list of everything that breaks: only services with public status pages and outages confirmed in the news.', 'Это не непрерывное наблюдение и не список всего, что ломается: только сервисы с публичными страницами статуса и сбои, подтверждённые в новостях.')}</p>"
    digs = sorted(glob.glob(os.path.join(B.D, 'outages', 'digests', '2*.md')))
    if digs:
        lf, native = B.localized(digs[-1]); day = os.path.basename(digs[-1])[:10]
        body += f"<h2 class='sec' id='digest'>{L('Daily digest', 'Сводка за день')}: {B.esc(B.fmt_date(day))}</h2>"
        if not native: body += f"<p class='note'>{B.t('This page is available in English only for now.')}</p>"
        body += f"<div class='prose'>{B.md(open(lf).read())}</div>"
    body += f"<h2 class='sec' id='now'>{L('Open incidents on official status pages', 'Открытые сбои на официальных страницах статуса')}</h2>"
    if not off: body += f"<p>{L('No open incidents on the status pages we read.', 'На страницах статуса, которые мы читаем, открытых сбоев нет.')}</p>"
    # cards only for major/critical, or anything opened in the last 3 days; the rest (minor, long-running) in one compact list
    import time as _t
    fresh = _t.strftime('%Y-%m-%dT%H:%M', _t.gmtime(_t.time() - 3 * 86400))
    big = [i for i in off if IMPACT.get(str(i.get('impact')).lower(), ('', '', 0))[2] >= 2 or (i.get('started') or '') >= fresh]
    small = [i for i in off if i not in big]
    for key, en, ru in SECTORS:
        xs = [i for i in big if i.get('sector') == key]
        if xs: body += f"<section class='fam'><h3>{L(en, ru)}<span class='cnt'>{len(xs)}</span></h3><div class='cards'>{''.join(card(i) for i in xs)}</div></section>"
    if small:
        body += f"<details class='signal-context'><summary>{L('Minor and long-running partial incidents', 'Мелкие и затяжные частичные сбои')}: {len(small)}</summary><ul class='arch'>" + ''.join(
            f"<li><a href='{B.esc(i.get('url') or '#')}' rel='nofollow noopener'><span><strong>{B.esc(i.get('source', ''))}: {B.esc(i.get('title', ''))}</strong><br><span class='meta'>{L('since', 'с')} {when(i.get('started'))}</span></span></a></li>" for i in small) + '</ul></details>'
    body += f"<h2 class='sec' id='internet'>{L('National internet: drops seen from outside (last 24 h)', 'Интернет стран: провалы, видимые снаружи (24 часа)')}</h2><p class='meta'>{L('IODA (Georgia Tech) watches routing and probe signals per country. A drop is a signal, not a cause: a shutdown, a power cut, a cable cut or a measurement fault look alike.', 'IODA (Georgia Tech) следит за маршрутизацией и ответами сетей по странам. Провал — это сигнал, а не причина: отключение властями, обесточивание, обрыв кабеля и сбой измерений выглядят одинаково.')}</p>"
    body += f"<div class='cards'>{''.join(card(i, True) for i in sorted(net, key=lambda i: -(i.get('impact') or 0)))}</div>" if net else f"<p>{L('No large country-level drops in the last 24 hours.', 'Крупных провалов на уровне стран за 24 часа нет.')}</p>"
    rec = d.get('recent', [])[:40]
    if rec:
        body += f"<h2 class='sec' id='recent'>{L('Recently closed (30 days)', 'Недавно закрытые (30 дней)')}</h2><ul class='arch'>" + ''.join(
            f"<li><a href='{B.esc(i.get('url') or '#')}' rel='nofollow noopener'><span><strong>{B.esc(i.get('source', ''))}: {B.esc(i.get('title', ''))}</strong><br><span class='meta'>{when(i.get('started'))} → {when(i.get('last_ts'))}</span></span></a></li>" for i in rec) + '</ul>'
    body += f"<h2 class='sec' id='how'>{L('Sources and rules', 'Источники и правила')}</h2><div class='prose'><p>{L('Official: status pages of about 25 payment, banking-infrastructure, crypto, cloud, communications and AI providers; Google Cloud, AWS and Azure status feeds; IODA country signals. News: hourly web monitors for bank and payment outages and for government and public-sector network failures worldwide, including Russian-language media. A news lead appears here only in the daily digest, after two independent sources, with the date of the event and of the publication. Russian services without public status pages (Gosuslugi, Sber, SBP) are covered through the news monitors.', 'Официальные: страницы статуса примерно 25 платёжных, банковских инфраструктурных, криптовалютных, облачных, коммуникационных и ИИ-сервисов; ленты статуса Google Cloud, AWS и Azure; сигналы IODA по странам. Новости: ежечасные веб-мониторы сбоев банков и платёжных систем и отказов госсетей и госсервисов по всему миру, включая русскоязычные СМИ. Новостной сигнал попадает сюда только в сводку дня, после двух независимых источников, с датой события и публикации. Российские сервисы без публичных страниц статуса (Госуслуги, Сбер, СБП) отслеживаются через новостные мониторы.')}</p><p>{L('Large systemic outages also feed the institutions and economy components of the', 'Крупные системные сбои также учитываются в компонентах «институты» и «экономика»')} <a href='/'>{L('Chaos Pulse index', 'индекса Пульса хаоса')}</a>. <a href='/data/outages/latest.json'>JSON</a>.</p></div>"
    if len(digs) > 1:
        body += f"<h2 class='sec' id='archive'>{L('Earlier digests', 'Прошлые сводки')}</h2><ul class='arch'>" + ''.join(
            f"<li><a href='/outages/{os.path.basename(g)[:10]}/'><span><strong>{B.esc(B.fmt_date(os.path.basename(g)[:10]))}</strong></span></a></li>" for g in reversed(digs[:-1])) + '</ul>'
    body += f"<p class='meta'><a href='/outages/feed.xml'>RSS</a> · {L('one item per daily digest', 'одна запись на сводку дня')}</p>"
    B.page('/outages/', title, desc, body, 'CollectionPage', active='outages', lastmod=(d.get('checked') or '')[:10] or None)
    # 18.11 (#769): one page per daily digest and an RSS feed of digests
    items = ''
    for g in digs:
        day = os.path.basename(g)[:10]; lf, native = B.localized(g); html = B.md(open(lf).read())
        t2 = L(f'Outage Watch digest, {day}', f'Сводка сбоев, {day}')
        pb = f"<h1 class='ptitle'>{B.esc(t2)}</h1>" + ('' if native else f"<p class='note'>{B.t('This page is available in English only for now.')}</p>")
        pb += f"<div class='prose'>{html}</div><p class='meta'><a href='/outages/'>{L('← Outage Watch', '← Сбои')}</a></p>"
        B.page(f'/outages/{day}/', t2, L(f'Verified outages of banks, payment systems, government networks and clouds on {day}, with sources.', f'Проверенные сбои банков, платёжных систем, госсетей и облаков за {day}, с источниками.'), pb, 'Article', active='outages', lastmod=day)
        url = B.BASE + i18n.lpath(f'/outages/{day}/')
        items = f"<item><title>{B.esc(t2)}</title><link>{url}</link><guid>{url}</guid><pubDate>{__import__('email.utils').utils.format_datetime(__import__('datetime').datetime.fromisoformat(day + 'T23:30:00+00:00'))}</pubDate><description>{B.esc(html)}</description></item>" + items
    fdir = os.path.join(B.OUT, i18n.LANG, 'outages'); os.makedirs(fdir, exist_ok=True)
    furl = B.BASE + i18n.lpath('/outages/')
    open(os.path.join(fdir, 'feed.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{B.esc(L("Outage Watch digests", "Сводки сбоев"))}</title><link>{furl}</link><atom:link href="{furl}feed.xml" rel="self" type="application/rss+xml"/><description>{B.esc(desc)}</description><language>{i18n.LANG}</language>{items}</channel></rss>\n')
