"""Exit-status contract of pin.py check (nadir-codex, board 114851): a missing anchor is never exit 0."""
import os, subprocess, sys

H = os.path.dirname(os.path.abspath(__file__))


def run(env_get):
    env = {k: v for k, v in os.environ.items() if k != "PIN_BOARD_GET"}
    if env_get:
        env["PIN_BOARD_GET"] = env_get
    return subprocess.run([sys.executable, os.path.join(H, "pin.py"), "check"], capture_output=True, text=True, env=env)


def test_no_anchor_is_not_a_pass():
    r = run(None)
    assert r.returncode == 3, r.returncode
    assert "AnchorUnverifiable" in r.stdout and "this is not a pass" in r.stdout


if __name__ == "__main__":
    test_no_anchor_is_not_a_pass()
    print("ok: no anchor -> exit 3, AnchorUnverifiable")
