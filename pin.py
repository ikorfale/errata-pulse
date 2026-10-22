#!/usr/bin/env python3
"""Pin the corrections ledger on the board: an append-only chain of (board seq, bytes, lines, sha256).

  python3 pin.py check            prefix check against the last pin; prints whether a new pin is owed
  python3 pin.py draft            check + Wayback copies at HEAD + a board reply body on stdout
  python3 pin.py record SEQ       append the pin row for the post SEQ (run after posting the draft)

Rules (board 97731): correction ids are never reused, no line is superseded, every pin cites the previous one,
the board's seq/created_at is the only clock.
"""
import hashlib, json, os, subprocess, sys, time, urllib.request

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FILES = ["corrections.jsonl", "corrections_evidence.jsonl"]
PINS = os.path.join(D, "corrections_pins.jsonl")
REPO = "ikorfale/errata-pulse"


def state():
    out = {}
    for f in FILES:
        b = open(os.path.join(D, f), "rb").read()
        out[f] = {"bytes": len(b), "lines": b.count(b"\n"), "sha256": hashlib.sha256(b).hexdigest()}
    return out


def last_pin():
    rows = [json.loads(l) for l in open(PINS) if l.strip()]
    return rows[-1]


def check():
    pin, now, ok, owed = last_pin(), state(), True, False
    for f in FILES:
        b = open(os.path.join(D, f), "rb").read()
        old = pin["files"][f]
        n = old["bytes"]
        good = hashlib.sha256(b[:n]).hexdigest() == old["sha256"] and b[n - 1:n] == b"\n"
        ok &= good
        owed |= now[f]["sha256"] != old["sha256"]
        print(f"{f}: pinned {n} B in {pin['board_seq']}, now {now[f]['bytes']} B; prefix {'OK' if good else 'BROKEN'}")
    ids = [json.loads(l)["id"] for l in open(os.path.join(D, FILES[0])) if l.strip()]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        ok = False
        print("reused correction ids:", dup)
    print("new pin owed" if owed else "no new pin owed")
    return ok, owed, pin, now


def wayback(url):
    req = urllib.request.Request("https://web.archive.org/save/" + url, method="HEAD")
    opener = urllib.request.build_opener(type("NoRedir", (urllib.request.HTTPRedirectHandler,),
                                              {"redirect_request": lambda *a, **k: None}))
    try:
        r = opener.open(req, timeout=120)
        return r.headers.get("location")
    except urllib.error.HTTPError as e:
        return e.headers.get("location")
    except Exception:
        return None


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    ok, owed, pin, now = check()
    if cmd == "check":
        sys.exit(0 if ok else 1)
    if not ok:
        sys.exit("prefix broken or ids reused: say so in public before any new pin")
    commit = subprocess.check_output(["git", "-C", os.path.dirname(D), "rev-parse", "HEAD"], text=True).strip()
    pushed = subprocess.run(["git", "-C", os.path.dirname(D), "branch", "-r", "--contains", commit],
                            capture_output=True, text=True).stdout.strip()
    if cmd == "draft":
        if not owed:
            return
        if not pushed:
            sys.exit("push first: the pin names a commit strangers must be able to fetch")
        L = [f"Corrections ledger pin, after #{pin['board_seq']}. Prefix check against it [ran]:", "",
             f"| file | then (#{pin['board_seq']}) | now |", "|---|---|---|"]
        for f in FILES:
            o, n = pin["files"][f], now[f]
            url = f"https://raw.githubusercontent.com/{REPO}/{commit}/data/{f}"
            now[f]["archive"] = wayback(url)
            time.sleep(3)
            L.append(f"| {f} | {o['bytes']} B, {o['lines']} lines, `{o['sha256'][:8]}…` | {n['bytes']} B, {n['lines']} lines, `{n['sha256']}` |")
        L += ["", f"Old sizes end on a newline; correction ids unique. Commit {commit}. Wayback copies (gzip-encoded, unzip then hash):"]
        L += [f"- {now[f]['archive']}" for f in FILES]
        L += ["", f"Chain: #{pin['board_seq']} -> this post. Ledger: pulse.errata.page/corrections/"]
        print("\n".join(L))
        json.dump({"commit": commit, "files": now}, open("/tmp/pin_draft.json", "w"))
    elif cmd == "record":
        seq = int(sys.argv[2])
        draft = json.load(open("/tmp/pin_draft.json"))
        row = {"board_seq": seq, "prev_seq": pin["board_seq"], "commit": draft["commit"], "files": draft["files"]}
        with open(PINS, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print("recorded", seq)


if __name__ == "__main__":
    main()
