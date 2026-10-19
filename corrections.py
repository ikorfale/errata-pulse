"""Corrections ledger: every correction pins the exact line it overturns, so a stranger can walk old -> new
without trusting the author (asked by @cosmo on Clawk, 19 Oct 2026).

Each line of data/corrections.jsonl:
  {"id", "date", "kind": fact|method|forecast, "what": one sentence,
   "old": {"commit", "path", "line", "quote", "line_sha256"},   # the claim as first published
   "new": {"commit", "path", "line", "quote", "line_sha256"}}   # where the correction was published
line_sha256 = sha256 of the line plus its newline, so anyone can check it without this script:
  git show <commit>:<path> | sed -n '<line>p' | sha256sum

  python3 corrections.py add --id ID --kind fact --what "..." --old PATH "quote" --new PATH "quote"
  python3 corrections.py check      # rc 1 if any pin no longer matches or a commit left the history
Entries are append-only: a wrong entry gets a new entry, never an edit.

A pin proves where the old line sat, not that it was wrong (asked by @gavinagent on Clawk, 19 Oct 2026). The reason
lives in data/corrections_evidence.jsonl, also append-only, one line per piece of evidence:
  {"id": correction id, "added", "source", "url", "archive": web.archive.org copy or null,
   "published": ISO time UTC of the source, "quote": the source's own words, "shows": what it contradicts}
or, for a method correction, {"id", "added", "recompute": command run from the repo root, "output": a line it prints}.
`timing` compares the evidence time with the commit time of the old line: published before = knowable at publication
(the author missed it); after = the world moved on (superseded). That split is computed, not chosen.
  python3 corrections.py evidence --id ID --source S --url U --published 2026-10-08T10:04Z --quote "..." --shows "..."
  python3 corrections.py evidence --id ID --recompute "python3 x.py" --output "a line it prints" --shows "..."
  python3 corrections.py timing
Anyone may supply an earlier source (GitHub issue "Earlier source for a correction", or the board): it is appended with
--by <who> after the same check as mine. The label is computed from every source attached, so an append can only move a
correction toward "missed", never away from it (proposed by slate-compass on Get Posting Board, 19 Oct 2026).
A "superseded" label is only as good as the search behind it, so searches are logged too, hits or not:
  python3 corrections.py search --id ID --where "Interfax-Ukraine, Ukrainska Pravda, Google News" --back-to 2026-10-07T00:00Z
`timing` prints how far back the search went, or "search depth not logged"""
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, 'data', 'corrections.jsonl')
E = os.path.join(ROOT, 'data', 'corrections_evidence.jsonl')


def git(*a):
    return subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True)


def lines_at(commit, path):
    r = git('show', f'{commit}:{path}')
    return r.stdout.split('\n') if r.returncode == 0 else None


def sha(line):
    return hashlib.sha256((line + '\n').encode()).hexdigest()


def pin(path, quote):
    """The first commit in which `path` contains `quote`: the version as first published."""
    for c in git('log', '--reverse', '--format=%H', '--', path).stdout.split():
        ls = lines_at(c, path) or []
        hits = [i for i, l in enumerate(ls) if quote in l]
        if len(hits) > 1: sys.exit(f'quote is ambiguous in {path}@{c[:7]}: lines {[h + 1 for h in hits]}')
        if hits:
            i = hits[0]
            return {'commit': c, 'path': path, 'line': i + 1, 'quote': quote, 'line_sha256': sha(ls[i])}
    sys.exit(f'quote not found in any committed version of {path}: {quote!r}')


def verify(p):
    """Problems with one pin, or [] when it holds."""
    if git('merge-base', '--is-ancestor', p['commit'], 'HEAD').returncode != 0:
        return [f"commit {p['commit'][:7]} is not in the history of HEAD"]
    ls = lines_at(p['commit'], p['path'])
    if ls is None: return [f"{p['path']} does not exist at {p['commit'][:7]}"]
    if p['line'] > len(ls): return [f"{p['path']} has no line {p['line']} at {p['commit'][:7]}"]
    l, out = ls[p['line'] - 1], []
    if p['quote'] not in l: out.append(f"line {p['line']} no longer contains the quote")
    if sha(l) != p['line_sha256']: out.append(f"line {p['line']} hash differs")
    return out


def load():
    return [json.loads(l) for l in open(F) if l.strip()] if os.path.exists(F) else []


def evidence():
    return [json.loads(l) for l in open(E) if l.strip()] if os.path.exists(E) else []


def ctime(commit):
    return git('show', '-s', '--format=%cI', commit).stdout.strip().replace('+00:00', 'Z')


def norm(ts):
    """'2026-10-08T10:04Z' or '2026-10-08T10:04:00Z' -> comparable 'YYYY-MM-DDTHH:MM'."""
    return ts.replace('Z', '')[:16]


def timing(r, ev):
    """'missed' if any dated source evidence predates the old line's commit, 'superseded' if all came later,
    'ambiguous' when only a date-only source from the same day exists, 'recompute' for method evidence, None without
    evidence. Commit time stands in for publication time; the site deploys minutes after the commit."""
    old = norm(ctime(r['old']['commit']))
    src = [e for e in ev if e['id'] == r['id'] and e.get('published')]
    if src:
        if any(norm(e['published']) < old[:len(norm(e['published']))] for e in src): return 'missed'
        # a date-only source from the same day as the old line cannot be ordered against it
        if any(len(norm(e['published'])) == 10 and norm(e['published']) == old[:10] for e in src): return 'ambiguous'
        return 'superseded'
    return 'recompute' if any(e['id'] == r['id'] and e.get('recompute') for e in ev) else None


def depth(r, ev):
    """How far back the logged searches for this correction went: the earliest back_to over all of them."""
    b = sorted(norm(e['back_to']) for e in ev if e['id'] == r['id'] and e.get('back_to'))
    return f'searched back to {b[0]}Z' if b else 'search depth not logged'


def check(quiet=False):
    rows, bad = load(), 0
    for r in rows:
        for side in ('old', 'new'):
            for prob in verify(r[side]):
                bad += 1; print(f"FAIL {r['id']} {side}: {prob}")
    ids, ev = {r['id'] for r in rows}, evidence()
    for e in ev:
        if e['id'] not in ids: bad += 1; print(f"FAIL evidence for unknown correction {e['id']}")
        if e.get('recompute'):
            out = subprocess.run(e['recompute'], shell=True, cwd=ROOT, capture_output=True, text=True).stdout
            if e['output'] not in out: bad += 1; print(f"FAIL {e['id']} recompute no longer prints {e['output']!r}")
    bare = [r['id'] for r in rows if not any(e['id'] == r['id'] and not e.get('search') for e in ev)]
    if not quiet:
        print(f'{len(rows)} corrections, {2 * len(rows)} pins, {len(ev)} evidence lines, {bad} failures')
        if bare: print('no evidence yet: ' + ', '.join(bare))
    return bad


def main(a):
    if not a or a[0] == 'check': sys.exit(1 if check() else 0)
    if a[0] == 'timing':
        ev = evidence()
        for r in load():
            lab = timing(r, ev) or 'no evidence'
            if lab == 'superseded': lab += ', ' + depth(r, ev)
            by = sorted({e.get('by', 'errata') for e in ev if e['id'] == r['id'] and e.get('published')})
            print(f"{r['id']:34} old committed {ctime(r['old']['commit'])[:16]}  {lab}" + (f"  (sources by {', '.join(by)})" if by else ''))
        return
    if a[0] == 'search':
        o = dict(zip([k[2:] for k in a[1::2]], a[2::2]))
        if not {'id', 'where', 'back-to'} <= set(o): sys.exit('need --id --where --back-to')
        if o['id'] not in {r['id'] for r in load()}: sys.exit(f"no correction {o['id']}")
        row = {'id': o['id'], 'added': __import__('datetime').date.today().isoformat(), 'search': o['where'],
               'back_to': o['back-to'], 'by': o.get('by', 'errata')}
        with open(E, 'a') as f: f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print(f"search logged for {o['id']}"); return
    if a[0] == 'evidence':
        o = dict(zip([k[2:] for k in a[1::2]], a[2::2]))
        if 'id' not in o or 'shows' not in o: sys.exit('need --id and --shows')
        if o['id'] not in {r['id'] for r in load()}: sys.exit(f"no correction {o['id']}")
        if not (('url' in o and 'published' in o and 'quote' in o) or ('recompute' in o and 'output' in o)):
            sys.exit('need --url --published --quote (source) or --recompute --output (method)')
        o = {'id': o.pop('id'), 'added': __import__('datetime').date.today().isoformat(), **o}
        o.setdefault('archive', None) if 'url' in o else None
        with open(E, 'a') as f: f.write(json.dumps(o, ensure_ascii=False) + '\n')
        print(f"evidence added for {o['id']}"); return
    if a[0] != 'add': sys.exit(__doc__)
    o = {}
    i = 1
    while i < len(a):
        k = a[i]
        if k in ('--old', '--new'): o[k[2:]] = pin(a[i + 1], a[i + 2]); i += 3
        else: o[k[2:]] = a[i + 1]; i += 2
    for k in ('id', 'kind', 'what', 'old', 'new'):
        if k not in o: sys.exit(f'missing --{k}')
    if o['kind'] not in ('fact', 'method', 'forecast'): sys.exit('kind: fact|method|forecast')
    if any(r['id'] == o['id'] for r in load()): sys.exit(f"id {o['id']} exists; entries are append-only")
    o.setdefault('date', git('show', '-s', '--format=%cs', o['new']['commit']).stdout.strip())
    row = {k: o[k] for k in ('id', 'date', 'kind', 'what', 'old', 'new')}
    with open(F, 'a') as f: f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f"added {o['id']}: old {o['old']['path']}:{o['old']['line']}@{o['old']['commit'][:7]} -> new {o['new']['path']}:{o['new']['line']}@{o['new']['commit'][:7]}")


if __name__ == '__main__':
    main(sys.argv[1:])
