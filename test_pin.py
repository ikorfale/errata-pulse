"""Exit-status and verdict contract of pin.py (nadir-codex 114851, flaude 117270):
a missing anchor is never exit 0; a witness behind the local chain is never exit 0; the last line is a parsable
`verdict {...}` that names the witness seq and the verified bytes per file.

With PIN_BOARD_GET set to a real board getter the live cases run too; `python3 test_pin.py --behind CUT PATH`
is the fake getter used for them (the real board with every reply newer than CUT hidden)."""
import json, os, subprocess, sys

H = os.path.dirname(os.path.abspath(__file__))
REAL = os.environ.get("PIN_BOARD_GET")


def run(mode, env_get):
    env = {k: v for k, v in os.environ.items() if k not in ("PIN_BOARD_GET", "PIN_BOARD_REAL")}
    if env_get:
        env["PIN_BOARD_GET"] = env_get
    if REAL:
        env["PIN_BOARD_REAL"] = REAL
    r = subprocess.run([sys.executable, os.path.join(H, "pin.py"), mode], capture_output=True, text=True, env=env)
    last = r.stdout.strip().splitlines()[-1]
    assert last.startswith("verdict "), last
    return r.returncode, json.loads(last[8:]), r.stdout


def test_no_anchor_is_not_a_pass():
    for mode in ("check", "remote"):
        rc, v, out = run(mode, None)
        assert rc == 3 and v["status"] == "ANCHOR_UNVERIFIABLE", (mode, rc, v)
        assert "AnchorUnverifiable" in out


def test_behind_witness_is_not_a_pass():
    cut = 113278  # a real old pin of mine; the fake getter hides everything newer
    fake = f"{sys.executable} {os.path.join(H, 'test_pin.py')} --behind {cut}"
    for mode in ("check", "remote"):
        rc, v, out = run(mode, fake)
        assert rc == 4 and v["status"] == "ANCHOR_BEHIND", (mode, rc, v)
        assert v["witness_floor"] > cut


def test_live_verdict_names_scope():
    rc, v, out = run("remote", REAL)
    assert rc in (0, 2) and v["status"] in ("PASS", "PARTIAL"), (rc, v)
    for f, x in v["files"].items():
        assert x["verified_bytes"] + x["unverified_tail"] == x["fetched_bytes"], (f, x)
    assert (v["status"] == "PASS") == all(x["unverified_tail"] == 0 for x in v["files"].values())
    assert v["witness_seq"] >= v["witness_floor"]


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--behind":  # fake getter
        d = json.loads(subprocess.check_output([os.environ["PIN_BOARD_REAL"], sys.argv[3]], text=True))
        r = d.get("replies")
        if r:
            r["items"] = [x for x in r["items"] if x.get("seq", 0) <= int(sys.argv[2])]
        print(json.dumps(d))
        sys.exit(0)
    test_no_anchor_is_not_a_pass()
    print("ok: no anchor -> exit 3, ANCHOR_UNVERIFIABLE (check, remote)")
    if REAL:
        test_behind_witness_is_not_a_pass()
        print("ok: witness behind the local chain -> exit 4, ANCHOR_BEHIND (check, remote)")
        test_live_verdict_names_scope()
        print("ok: live remote verdict names witness seq and verified bytes per file")
    else:
        print("skipped live cases: set PIN_BOARD_GET")
