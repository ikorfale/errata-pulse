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
Entries are append-only: a wrong entry gets a new entry, never an edit."""
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, 'data', 'corrections.jsonl')


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


def check(quiet=False):
    rows, bad = load(), 0
    for r in rows:
        for side in ('old', 'new'):
            for prob in verify(r[side]):
                bad += 1; print(f"FAIL {r['id']} {side}: {prob}")
    if not quiet: print(f'{len(rows)} corrections, {2 * len(rows)} pins, {bad} failures')
    return bad


def main(a):
    if not a or a[0] == 'check': sys.exit(1 if check() else 0)
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
