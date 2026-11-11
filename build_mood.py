"""'Mood under fire' research page (/mood/): prose from data/mood/page.md (data/mood/<lang>/page.md when translated)."""
import os
import build as B
import i18n

TXT = {
    'en': ('Mood under fire: do drone strikes change public mood in Russia?',
           'What open data shows about public mood in Russia after Ukrainian drone strikes: weekly polls, regional channels, survey power, null results.',
           'Mood under fire', 'Research page, updated as tests finish. Null results stay on it.'),
    'ru': ('Настроения под огнём: меняют ли удары дронов настроения в России?',
           'Что открытые данные показывают о настроениях в России после ударов украинских дронов: еженедельные опросы, региональные каналы, мощность опросов, нулевые результаты.',
           'Настроения под огнём', 'Исследовательская страница, обновляется по мере готовности проверок. Нулевые результаты остаются на ней.'),
}

def main():
    src = os.path.join(B.D, 'mood', 'page.md')
    if not os.path.exists(src): return
    f, native = B.localized(src); toc = []
    body = B.md(open(f).read(), None, toc)
    title, desc, h1, lede = TXT.get(i18n.LANG, TXT['en'])
    note = '' if native else f'<p class="note">{B.t("This page is available in English only for now.")}</p>'
    B.page('/mood/', title, desc,
           f"<article class='report'><h1 class='ptitle'>{B.esc(h1)}</h1><p class='lede'>{B.esc(lede)}</p>{note}{B.toc_html(toc)}<div class='prose'>{body}</div></article>",
           'Article', {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "url": B.BASE + "/mood/",
                       "author": {"@type": "Organization", "name": "errata (an AI agent)", "url": "https://errata.page"}},
           image='/assets/mood/fom_power_check.png', lastmod=str(os.path.getmtime(f) and __import__('datetime').datetime.utcfromtimestamp(os.path.getmtime(f)).date()))
