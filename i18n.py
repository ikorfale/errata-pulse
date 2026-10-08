"""Languages of pulse.errata.page. English is the source language; every other language is one file
i18n/<lang>.json: {"English string": "translation"}. Interface strings are written in the builders as
t('English {x}', x=...); data strings (signal labels, reading guides, channel groups) go through td().
A missing translation falls back to English and is listed in i18n/missing.<lang>.json after a build,
so a new language can be added by copying ru.json, translating it and adding the code to LANGS."""
import json, os
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ['en', 'ru']                        # order of the switcher; 'en' is the default and x-default
LABEL = {'en': 'EN', 'ru': 'RU', 'uk': 'UK'}
NATIVE = {'en': 'English', 'ru': 'Русский', 'uk': 'Українська'}
LANG = 'en'
_dicts, MISSING = {}, {}

def use(lang):
    global LANG
    LANG = lang

def _dict(lang):
    if lang not in _dicts:
        f = os.path.join(HERE, 'i18n', f'{lang}.json')
        _dicts[lang] = json.load(open(f)) if os.path.exists(f) else {}
    return _dicts[lang]

def t(s, **kw):
    """Translate an interface string (a str.format template when keywords are given)."""
    if LANG != 'en' and s:
        r = _dict(LANG).get(s)
        if r is None: MISSING.setdefault(LANG, set()).add(s); r = s
        s = r
    return s.format(**kw) if kw else s

def td(s):
    """Translate a data string (no formatting); untranslated data stays in English."""
    if LANG == 'en' or not isinstance(s, str) or not s.strip(): return s
    return t(s)

def plural(n, one, few, many=None):
    """English needs one/other; Russian and Ukrainian need one/few/many. Pass the English forms; translations come from the dictionary."""
    if LANG in ('ru', 'uk'):
        forms = t(one + '|' + few).split('|')
        if len(forms) == 3:
            n10, n100 = abs(n) % 10, abs(n) % 100
            return forms[0] if n10 == 1 and n100 != 11 else forms[1] if 2 <= n10 <= 4 and not 12 <= n100 <= 14 else forms[2]
    return one if n == 1 else few

MONTHS = {'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'],
          'uk': ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']}
SHORT = {'ru': ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'],
         'uk': ['січ', 'лют', 'бер', 'кві', 'тра', 'чер', 'лип', 'сер', 'вер', 'жов', 'лис', 'гру']}

def date_long(d):
    """'7 October 2026' / '7 октября 2026'."""
    if isinstance(d, str): d = datetime.strptime(d[:10], '%Y-%m-%d')
    return f'{d.day} {MONTHS[LANG][d.month - 1]} {d.year}' if LANG in MONTHS else d.strftime('%-d %B %Y')

def date_short(d):
    """'7 Oct' / '7 окт' for chart axes."""
    return f'{d.day} {SHORT[LANG][d.month - 1]}' if LANG in SHORT else d.strftime('%-d %b')

def num_pct(x, digits=0):
    """A share as a percentage in the local style (decimal comma in Russian)."""
    s = f'{x * 100:.{digits}f}%'
    return s.replace('.', ',') if LANG in ('ru', 'uk') else s

def lpath(path, lang=None):
    return '/' + (lang or LANG) + path

def write_missing():
    for lang, ss in MISSING.items():
        json.dump(sorted(ss), open(os.path.join(HERE, 'i18n', f'missing.{lang}.json'), 'w'), ensure_ascii=False, indent=0)
    for lang in LANGS:
        f = os.path.join(HERE, 'i18n', f'missing.{lang}.json')
        if lang not in MISSING and os.path.exists(f): os.remove(f)
