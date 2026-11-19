"""
serverctl.py — start / stop / restart / status for the NovelScrape web dashboard.

Guarantees at most ONE server instance:
  * `start` probes the server first and refuses to spawn a second one.
  * `stop` kills whatever process is listening on the port (netstat lookup,
    works even for servers started manually).
  * a PID file (.artifacts/webapp-server.pid) records who was started by this
    tool; netstat remains the source of truth.

Usage (works in any shell — Git Bash, PowerShell, cmd):
    venv\\Scripts\\python.exe serverctl.py status
    venv\\Scripts\\python.exe serverctl.py start
    venv\\Scripts\\python.exe serverctl.py stop
    venv\\Scripts\\python.exe serverctl.py restart
    venv\\Scripts\\python.exe serverctl.py logs [N]     # tail server log
    venv\\Scripts\\python.exe serverctl.py serve       # foreground (Ctrl-C stops)
    venv\\Scripts\\python.exe serverctl.py scrape [...]   # -> scraper.py
    venv\\Scripts\\python.exe serverctl.py combine [...]  # -> combiner.py
    venv\\Scripts\\python.exe serverctl.py clean [...]    # -> clean_scraped_files.py
"""

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 5000
BASE_URL = f"http://{HOST}:{PORT}"
ARTIFACTS = BASE_DIR / ".artifacts"
PID_FILE = ARTIFACTS / "webapp-server.pid"
LOG_FILE = ARTIFACTS / "webapp-server.log"

DETACHED = 0x00000008 | 0x00000200          # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP


def probe(timeout=1.5):
    """True if a NovelScrape dashboard answers on the port."""
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/job", timeout=timeout) as r:
            return r.status == 200
    except Exception:                               # noqa: BLE001
        return False


def pid_by_port():
    """PID of the process listening on PORT via netstat, or None."""
    try:
        out = subprocess.run(["netstat", "-ano", "-p", "tcp"],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:                               # noqa: BLE001
        return None
    for line in out.splitlines():
        parts = line.split()
        # LISTENING line: proto, local addr, foreign addr, state, pid
        if len(parts) >= 5 and parts[3] == "LISTENING" and \
                parts[1].upper().endswith(f":{PORT}"):
            return int(parts[4])
    return None


def read_pid_file():
    try:
        return int(PID_FILE.read_text().strip())
    except Exception:                               # noqa: BLE001
        return None


def clear_pid_file():
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


def taskkill(pid):
    subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                   capture_output=True, timeout=15)


def stop(wait_secs=10):
    """Stop the server (pid file first, netstat fallback). Returns True if stopped."""
    if not probe():
        clear_pid_file()
        print("Server is not running.")
        return True
    pid = pid_by_port()
    if pid is None:
        print("[X] Server responds but no PID found on port — kill it manually.")
        return False
    taskkill(pid)
    deadline = time.time() + wait_secs
    while probe(timeout=0.5) and time.time() < deadline:
        time.sleep(0.5)
    if probe(timeout=0.5):
        print(f"[X] PID {pid} still alive after {wait_secs}s — kill it manually.")
        return False
    clear_pid_file()
    print(f"Server stopped (PID {pid}).")
    return True


def start():
    if probe():
        pid = pid_by_port()
        print(f"Server already running (PID {pid}) at {BASE_URL} — not starting a second one.")
        return 0
    ARTIFACTS.mkdir(exist_ok=True)
    python = sys.executable
    with open(LOG_FILE, "ab") as log:
        proc = subprocess.Popen(
            [python, str(BASE_DIR / "webapp.py")],
            cwd=str(BASE_DIR), stdout=log, stderr=log,
            creationflags=DETACHED, stdin=subprocess.DEVNULL,
        )
    # wait until it answers
    deadline = time.time() + 20
    while not probe() and time.time() < deadline:
        time.sleep(0.5)
    if not probe():
        print(f"[X] Server did not come up within 20s — see {LOG_FILE}")
        return 1
    # proc.pid may be the venv launcher, not the actual interpreter — record
    # the PID that is really listening on the port.
    pid = pid_by_port() or proc.pid
    PID_FILE.write_text(str(pid))
    print(f"Server started (PID {pid}) at {BASE_URL} — log: {LOG_FILE}")
    return 0


def status():
    up = probe()
    pid = pid_by_port() if up else None
    recorded = read_pid_file()
    if up:
        stale = recorded not in (None, pid)
        print(f"RUNNING  PID {pid}  url {BASE_URL}"
              + (f"  (pid-file corrected from {recorded})" if stale else ""))
        if stale:
            PID_FILE.write_text(str(pid))
    else:
        clear_pid_file()
        print("STOPPED")
    return 0


def tail_logs(n=40):
    if not LOG_FILE.is_file():
        print("No server log yet.")
        return 0
    lines = LOG_FILE.read_text(errors="replace").splitlines()
    print("\n".join(lines[-int(n):]))
    return 0


def passthrough(script, args):
    """Run a pipeline script in the foreground with the same interpreter."""
    proc = subprocess.run([sys.executable, str(BASE_DIR / script)] + list(args),
                          cwd=str(BASE_DIR))
    return proc.returncode


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start":
        return start()
    if cmd == "stop":
        return 0 if stop() else 1
    if cmd == "restart":
        if not stop():
            return 1
        time.sleep(1)
        return start()
    if cmd == "status":
        return status()
    if cmd == "logs":
        return tail_logs(sys.argv[2] if len(sys.argv) > 2 else 40)
    if cmd == "serve":
        return passthrough("webapp.py", [])
    if cmd in ("scrape", "combine", "clean"):
        script = {"scrape": "scraper.py", "combine": "combiner.py",
                  "clean": "clean_scraped_files.py"}[cmd]
        return passthrough(script, sys.argv[2:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
