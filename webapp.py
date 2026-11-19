"""
webapp.py — Local web dashboard for the NovelScrape project.

Wraps the existing scraper.py and combiner.py in a small Flask app:

  * Scrape form (website / novel / chapter range) -> runs the scraper in a
    background thread, streams its console output live to the browser (SSE).
  * Library view of downloads/<novel>/ folders (chapter counts + EPUBs).
  * Combine -> TXT or EPUB button per novel, with the combiner's options.
  * Download link for generated TXT/EPUB files (restricted to downloads/).

Run:  venv/Scripts/python.exe webapp.py   (or webapp.bat)
Then open http://127.0.0.1:5000

Nothing in scraper.py or combiner.py is modified by this file.
"""

import json
import re
import sys
import threading
import time
from contextlib import redirect_stdout
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request, send_file

BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
EPUB_DIR = DOWNLOADS_DIR / "epub"

sys.path.insert(0, str(BASE_DIR))

import scraper as scraper_mod           # noqa: E402
import combiner as combiner_mod         # noqa: E402

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Job manager — one background job at a time (scrape or combine), with a
# log buffer that the SSE stream drains.
# ---------------------------------------------------------------------------

class Job:
    def __init__(self, kind, title):
        self.kind = kind
        self.title = title
        self.state = "running"      # running | done | error
        self.started = time.time()
        self.finished = None
        self.result = None
        self.lines = []
        self.log_version = 0        # bumped on every appended line
        self.lock = threading.Lock()

    def log(self, text):
        with self.lock:
            for line in text.splitlines() or [""]:
                self.lines.append(line)
                self.log_version += 1

    def snapshot(self):
        with self.lock:
            return {
                "kind": self.kind,
                "title": self.title,
                "state": self.state,
                "started": self.started,
                "finished": self.finished,
                "result": self.result,
                "log_version": self.log_version,
                "log": self.lines[-400:],
            }


class _JobWriter:
    """stdout replacement that forwards printed text into the current job log."""

    def __init__(self, job, original):
        self.job = job
        self.original = original

    def write(self, text):
        self.original.write(text)          # keep console output as before
        self.job.log(text)

    def flush(self):
        self.original.flush()


_job_lock = threading.Lock()
_current_job = None


def get_job():
    with _job_lock:
        return _current_job


def start_job(kind, title, target, payload):
    """Run target(payload, job) in a daemon thread. Returns None if busy."""
    global _current_job
    with _job_lock:
        if _current_job and _current_job.state == "running":
            return None
        job = Job(kind, title)
        _current_job = job

    def runner():
        original = sys.stdout
        try:
            with redirect_stdout(_JobWriter(job, original)):
                job.result = target(payload, job)
            job.state = "done"
        except Exception as exc:                        # noqa: BLE001
            job.log(f"[X] Unexpected error: {exc}")
            job.state = "error"
        finally:
            job.finished = time.time()

    threading.Thread(target=runner, daemon=True).start()
    return job


# ---------------------------------------------------------------------------
# Background targets
# ---------------------------------------------------------------------------

def run_scrape(payload, job):
    website = payload["website"]
    if website not in scraper_mod.WEBSITE_CONFIGS:
        raise ValueError(f"Unsupported website: {website}")
    s = scraper_mod.UnifiedScraper(
        website,
        payload["novel_name"],
        payload["novel_slug"],
        int(payload["start_chapter"]),
        int(payload["end_chapter"]),
    )
    return s.scrape_range()


def run_combine(payload, job):
    folder = payload["input_path"]
    if not Path(folder).is_dir():
        raise ValueError(f"Input folder not found: {folder}")
    start = payload.get("start_chapter")
    end = payload.get("end_chapter")
    clean = bool(payload.get("clean_text", True))
    if payload.get("operation") == "epub":
        title = payload.get("epub_title") or Path(folder).name
        author = payload.get("epub_author") or "Unknown"
        marker = payload.get("chapter_marker", "full")
        out = payload.get("output_path") or str(EPUB_DIR / f"{Path(folder).name}.epub")
        combiner_mod.txt_to_epub(folder, str(_resolve(out)), title=title, author=author,
                                 clean=clean, verbose=True,
                                 start_chapter=start, end_chapter=end)
        return {"output": str(_resolve(out))}
    marker = payload.get("chapter_marker", "full")
    out = payload.get("output_path") or str(DOWNLOADS_DIR / f"{Path(folder).name}.txt")
    combiner_mod.combine_to_txt(folder, str(_resolve(out)), chapter_marker=marker,
                                clean=clean, verbose=True,
                                start_chapter=start, end_chapter=end)
    return {"output": str(_resolve(out))}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_name(name):
    if not name or re.search(r'[<>:"/\\|?*]', name) or name in (".", ".."):
        raise ValueError(f"Invalid name: {name!r}")
    return name


def _resolve(path):
    """Resolve a possibly-relative output path against the project dir."""
    p = Path(path)
    return p if p.is_absolute() else (BASE_DIR / p)


def library_data():
    novels = []
    if DOWNLOADS_DIR.is_dir():
        for d in sorted(DOWNLOADS_DIR.iterdir()):
            if d.is_dir():
                txts = list(d.glob("*.txt"))
                if txts:
                    novels.append({
                        "name": d.name,
                        "chapters": len(txts),
                        "first": min(int(p.stem) for p in txts if p.stem.isdigit()) if any(p.stem.isdigit() for p in txts) else None,
                        "last": max(int(p.stem) for p in txts if p.stem.isdigit()) if any(p.stem.isdigit() for p in txts) else None,
                    })
    epubs = sorted(EPUB_DIR.glob("*.epub")) if EPUB_DIR.is_dir() else []
    combined = sorted(DOWNLOADS_DIR.glob("*.txt"))
    return {
        "novels": novels,
        "epubs": [{"name": p.name, "size": p.stat().st_size} for p in epubs],
        "txt_files": [{"name": p.name, "size": p.stat().st_size} for p in combined],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/websites")
def api_websites():
    try:
        sites = scraper_mod.load_configs()
        return jsonify([
            {"id": k, "name": v.get("name", k)} for k, v in sorted(sites.items())
        ])
    except Exception as exc:                            # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.route("/api/library")
def api_library():
    return jsonify(library_data())


@app.route("/api/job")
def api_job():
    job = get_job()
    return jsonify(job.snapshot() if job else {"kind": None, "state": "idle"})


@app.route("/api/job/stream")
def api_job_stream():
    def generate():
        last_version = -1
        idle_sent = False
        while True:
            job = get_job()
            if job is None:
                if not idle_sent:
                    yield "data: {\"state\": \"idle\"}\n\n"
                    idle_sent = True
                time.sleep(1)
                continue
            idle_sent = False
            snap = job.snapshot()
            if snap["log_version"] != last_version or snap["state"] != "running":
                last_version = snap["log_version"]
                yield "data: " + json.dumps(snap) + "\n\n"
            if job.state != "running" and time.time() - job.finished > 5:
                break                                    # stop streaming shortly after finish
            time.sleep(0.5)
    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache"})


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    data = request.get_json(force=True)
    try:
        novel_name = safe_name(data["novel_name"])
        novel_slug = safe_name(data["novel_slug"])
        start, end = int(data["start_chapter"]), int(data["end_chapter"])
        if start > end or start < 1:
            raise ValueError("Chapter range invalid")
        if data["website"] not in scraper_mod.WEBSITE_CONFIGS:
            raise ValueError(f"Unsupported website: {data['website']}")
    except (KeyError, ValueError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400
    job = start_job("scrape", f"{novel_name}: ch {start}-{end}",
                    run_scrape, {"website": data["website"], "novel_name": novel_name,
                                 "novel_slug": novel_slug,
                                 "start_chapter": start, "end_chapter": end})
    if job is None:
        return jsonify({"error": "Another job is already running"}), 409
    return jsonify({"started": True})


@app.route("/api/combine", methods=["POST"])
def api_combine():
    data = request.get_json(force=True)
    try:
        folder = str((DOWNLOADS_DIR / safe_name(data["novel"])).resolve())
        op = data.get("operation", "epub")
        if op not in ("epub", "txt"):
            raise ValueError("operation must be epub or txt")
    except (KeyError, ValueError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400
    payload = {
        "input_path": folder,
        "operation": op,
        "clean_text": bool(data.get("clean_text", True)),
        "chapter_marker": data.get("chapter_marker", "full"),
        "epub_title": data.get("epub_title") or data["novel"],
        "epub_author": data.get("epub_author") or "Unknown",
        "output_path": data.get("output_path"),
        "start_chapter": data.get("start_chapter"),
        "end_chapter": data.get("end_chapter"),
    }
    job = start_job("combine", f"{data['novel']} -> {op}", run_combine, payload)
    if job is None:
        return jsonify({"error": "Another job is already running"}), 409
    return jsonify({"started": True})


@app.route("/api/download")
def api_download():
    name = request.args.get("file", "")
    try:
        safe_name(name)
    except ValueError:
        return jsonify({"error": "Invalid file name"}), 400
    for candidate in (EPUB_DIR / name, DOWNLOADS_DIR / name):
        if candidate.is_file():
            return send_file(candidate, as_attachment=True)
    return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    # debug=False: the reloader would double-spawn Chrome-driving threads.
    app.run(host="127.0.0.1", port=5000, debug=False)
