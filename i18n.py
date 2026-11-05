"""Languages of pulse.errata.page. English is the source language; every other language is one file
i18n/<lang>.json: {"English string": "translation"}. Interface strings are written in the builders as
t('English {x}', x=...); data strings (signal labels, reading guides, channel groups) go through td().
A missing translation falls back to English and is listed in i18n/missing.<lang>.json after a build,
so a new language can be added by copying ru.json, translating it and adding the code to LANGS."""
import json, os, re
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

_NUM = re.compile(r'(?<![\w{])\d+(?:[.,]\d+)*')
_tpls = {}

def _mask(s):
    """'3 of 40 files' -> ('{0} of {1} files', ['3', '40']): the numbers of a data string become positional slots."""
    nums = _NUM.findall(s); it = iter(range(len(nums)))
    return _NUM.sub(lambda m: '{%d}' % next(it), s), nums

def _pcls(nums):
    """Plural class of each number (one/few/many, Russian rules), so '3 дня' is not reused for 5: a learned template is
    used as is only when its numbers fall in the same classes."""
    out = []
    for x in nums:
        if not x.isdigit(): out.append('f'); continue
        n10, n100 = int(x) % 10, int(x) % 100
        out.append('1' if n10 == 1 and n100 != 11 else '2' if 2 <= n10 <= 4 and not 12 <= n100 <= 14 else '5')
    return tuple(out)

def _tpl(lang):
    """Number-free templates learned from the dictionary itself (05.11, #619): a key and its translation that carry the
    same numbers in the same order (decimal comma allowed) teach one template, so a signal note whose numbers change
    every day needs no new translation. Explicit template keys ('{0} of {1} ...') in the dictionary win."""
    if lang not in _tpls:
        T = {}
        for k, v in _dict(lang).items():
            if not isinstance(v, str): continue
            mk, nk = _mask(k)
            if not nk or '{' in k.replace('{0}', ''): continue
            mv, nv = _mask(v)
            if [x.replace(',', '.') for x in nk] == [x.replace(',', '.') for x in nv]: T.setdefault(mk, {})[_pcls(nk)] = mv
        T.update({k: {None: v} for k, v in _dict(lang).items() if re.search(r'\{\d+\}', k)})
        _tpls[lang] = T
    return _tpls[lang]

def td(s):
    """Translate a data string (no formatting); untranslated data stays in English. A string missing from the dictionary
    is tried again with its numbers masked; a miss is then listed as the template, so it is translated once, not daily."""
    if LANG == 'en' or not isinstance(s, str) or not s.strip(): return s
    d = _dict(LANG)
    if s in d: return d[s]
    k, nums = _mask(s)
    if not nums: return t(s)
    v = _tpl(LANG).get(k) or {}
    r = v.get(_pcls(nums)) or v.get(None)
    if r is None and v:                     # learned only for other plural classes: use it, but ask for a template
        MISSING.setdefault(LANG, set()).add(k); r = next(iter(v.values()))
    if r is None:
        MISSING.setdefault(LANG, set()).add(k); return s
    dec = ',' if LANG in ('ru', 'uk') else '.'
    return re.sub(r'\{(\d+)\}', lambda m: re.sub(r'^(\d+)\.(\d+)$', r'\1' + dec + r'\2', nums[int(m.group(1))]) if int(m.group(1)) < len(nums) else m.group(0), r)

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
