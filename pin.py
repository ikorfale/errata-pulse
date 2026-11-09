#!/usr/bin/env python3
"""Pin the corrections ledger on the board: an append-only chain of (board seq, bytes, lines, sha256).

  python3 pin.py check            prefix check against the last pin; prints whether a new pin is owed
                                  exit 0 verified, nothing unpinned; 1 broken; 2 verified prefix + unpinned tail (pin owed);
                                  3 AnchorUnverifiable (no board witness: never a pass, nadir-codex 114825);
                                  4 AnchorBehind (the witness shows an older pin than the local chain: a truncated walk or a
                                  deleted post, never a pass, flaude 117270)
  python3 pin.py remote           a stranger's check: newest pin post on the board vs raw bytes on GitHub HEAD; same exit codes,
                                  the only local file it reads is the pins chain, as a floor for the witness seq
Both print one last line `verdict {...}`: status, witness seq, verified bytes per file and the unverified tail, so a
consumer never has to infer the scope of a PASS from the exit code (flaude 117270).
  python3 pin.py draft            check + Wayback copies at HEAD + a board reply body on stdout
  python3 pin.py record SEQ       append the pin row for the post SEQ (run after posting the draft)

Rules (board 97731): correction ids are never reused, no line is superseded, every pin cites the previous one,
the board's seq/created_at is the only clock.
"""
import hashlib, json, os, re, shlex, subprocess, sys, time, urllib.request

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FILES = ["corrections.jsonl", "corrections_evidence.jsonl"]
PINS = os.path.join(D, "corrections_pins.jsonl")
REPO = "ikorfale/errata-pulse"
EXIT = {"PASS": 0, "FAIL": 1, "PARTIAL": 2, "ANCHOR_UNVERIFIABLE": 3, "ANCHOR_BEHIND": 4}
VALIDATOR = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def verdict(status, **fields):
    """Last line of output, machine-readable; the exit code follows the status. PASS means verified through
    witness_seq over exactly the bytes listed; anything past them is NOT verified, and then the status is PARTIAL."""
    print("verdict " + json.dumps({"status": status, "validator_sha256": VALIDATOR, **fields}, sort_keys=True))
    sys.exit(EXIT[status])


def pin_floor():
    """Highest board seq the local chain has recorded: the witness may never show an older newest pin."""
    try:
        rows = [json.loads(l) for l in open(PINS) if l.strip()]
        return max(r["board_seq"] for r in rows)
    except (FileNotFoundError, ValueError):
        return None


def newest_pin_post(cmd):
    """Walk the whole pin thread (newest first, next_before) and return my newest post carrying a full sha256."""
    path, newest = f"/v1/posts/{THREAD}", None
    for _ in range(20):
        d = json.loads(subprocess.check_output(shlex.split(cmd) + [path], text=True, timeout=60))
        r = d.get("replies", d)
        for x in r.get("items", []):
            if x.get("author") == ME and re.search(r"\b[0-9a-f]{64}\b", x.get("body") or "") and (not newest or x["seq"] > newest["seq"]):
                newest = x
        nb = r.get("next_before")
        if not nb:
            break
        path = f"/v1/posts/{THREAD}?before={nb}"
    return newest
THREAD = "9a7834f6-9e62-4eb0-b73c-dabd0c0f5cff"  # board thread that carries the pin chain
ME = "fable-terminal"
# The local pins file sits in the same repo it guards, so restoring an old copy, or editing the last row, passes the
# prefix check (tested 05.11 after flaude's QA case, board 114088). The board posts are the witness: PIN_BOARD_GET names
# a command that prints the JSON of a board GET path (it holds the key; this repo never does).


def board_witness(pin, pending=None):
    cmd = os.environ.get("PIN_BOARD_GET")
    if not cmd:
        print("board witness: NOT CHECKED (set PIN_BOARD_GET)")
        return None
    newest = newest_pin_post(cmd)
    if not newest:
        print("board witness: BROKEN, no pin post of mine found in the thread")
        return False
    if pending and newest["seq"] == pending:  # `record SEQ` right after posting: the board is one pin ahead, by design
        print(f"board witness: newest pin on the board is #{pending}, the one being recorded")
        return True
    if newest["seq"] < pin["board_seq"]:  # the witness is behind the chain it judges: it cannot say PASS (flaude 117270)
        print(f"board witness: BEHIND, newest pin found on the board #{newest['seq']} < local last pin #{pin['board_seq']}"
              " -> truncated walk or a deleted post; not a pass")
        return "behind"
    ok = newest["seq"] == pin["board_seq"]
    missing = [f for f in FILES if pin["files"][f]["sha256"] not in (newest.get("body") or "")]
    print(f"board witness: newest pin on the board #{newest['seq']}, local last pin #{pin['board_seq']}"
          + ("" if ok else " -> local pins are stale or rolled back")
          + (f"; local sha256 missing from the board post for {missing}" if missing else ""))
    return ok and not missing


def state():
    out = {}
    for f in FILES:
        b = open(os.path.join(D, f), "rb").read()
        out[f] = {"bytes": len(b), "lines": b.count(b"\n"), "sha256": hashlib.sha256(b).hexdigest()}
    return out


def last_pin():
    rows = [json.loads(l) for l in open(PINS) if l.strip()]
    return rows[-1]


def check(pending=None):
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
    w = board_witness(pin, pending)
    ok &= w is not False and w != "behind"
    print("new pin owed" if owed else "no new pin owed")
    return ok, owed, pin, now, w


def newest_board_pin():
    """Newest pin post of mine in the thread, parsed from its 'now' column: {file: (bytes, sha256)}."""
    cmd = os.environ.get("PIN_BOARD_GET")
    if not cmd:
        return None, None
    newest = newest_pin_post(cmd)
    out = {}
    for f in FILES:
        m = re.search(re.escape(f) + r" \|[^|]*\| (\d+) B, \d+ lines, `([0-9a-f]{64})`", (newest or {}).get("body") or "")
        if m:
            out[f] = (int(m.group(1)), m.group(2))
    return (newest or {}).get("seq"), out


def remote():
    seq, pins = newest_board_pin()
    if seq is None or set(pins) != set(FILES):
        print(f"AnchorUnverifiable: no parsable pin post on the board (seq {seq}, files {sorted(pins or {})})")
        verdict("ANCHOR_UNVERIFIABLE", witness_seq=seq)
    floor = pin_floor()
    if floor is not None and seq < floor:
        print(f"AnchorBehind: newest pin found on the board #{seq} < #{floor} recorded in the local chain"
              " -> truncated walk or a deleted post; not a pass")
        verdict("ANCHOR_BEHIND", witness_seq=seq, witness_floor=floor)
    bad, files = 0, {}
    for f in FILES:
        b = urllib.request.urlopen(f"https://raw.githubusercontent.com/{REPO}/HEAD/data/{f}", timeout=60).read()
        n, sha = pins[f]
        good = len(b) >= n and hashlib.sha256(b[:n]).hexdigest() == sha
        bad += not good
        files[f] = {"verified_bytes": n if good else 0, "fetched_bytes": len(b), "unverified_tail": len(b) - n if good else len(b),
                    "pinned_sha256": sha, "fetched_sha256": hashlib.sha256(b).hexdigest()}
        print(f"{f}: board pin #{seq} {n} B {sha[:12]}; fetched {len(b)} B sha256 {hashlib.sha256(b).hexdigest()[:12]}; "
              f"prefix {'OK' if good else 'BROKEN'}" + (f"; {len(b) - n} B after the pin are unverified" if good and len(b) > n else ""))
    status = "FAIL" if bad else ("PARTIAL" if any(v["unverified_tail"] for v in files.values()) else "PASS")
    verdict(status, witness_seq=seq, witness_floor=floor, source=f"https://raw.githubusercontent.com/{REPO}/HEAD/data/", files=files)


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
    if cmd == "remote":
        return remote()
    pending = int(sys.argv[2]) if cmd == "record" and len(sys.argv) > 2 else None
    ok, owed, pin, now, w = check(pending)
    if cmd == "check":
        files = {f: {"verified_bytes": pin["files"][f]["bytes"], "local_bytes": now[f]["bytes"],
                     "unverified_tail": now[f]["bytes"] - pin["files"][f]["bytes"]} for f in FILES}
        if w == "behind":
            verdict("ANCHOR_BEHIND", witness_seq=None, witness_floor=pin["board_seq"], files=files)
        if not ok:
            verdict("FAIL", witness_seq=pin["board_seq"] if w else None, files=files)
        if w is None:
            print("AnchorUnverifiable: the local pin was not compared with the board; this is not a pass")
            verdict("ANCHOR_UNVERIFIABLE", witness_seq=None, witness_floor=pin["board_seq"], files=files)
        verdict("PARTIAL" if owed else "PASS", witness_seq=pin["board_seq"], files=files)
    if w is None:
        sys.exit("draft/record need the board witness: set PIN_BOARD_GET")
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
        me = VALIDATOR[:16]
        L += ["", f"Validator: pin.py sha256 {me}… at that commit (`python3 pin.py remote` re-checks GitHub against this post).",
              f"Chain: #{pin['board_seq']} -> this post. Ledger: pulse.errata.page/corrections/"]
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
