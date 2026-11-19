# Web Dashboard (`webapp.py`)

A local web interface wrapping the existing CLI pipeline. **Nothing in
`scraper.py` or `combiner.py` is modified** — the dashboard imports and runs
their existing functions in background threads.

## Run it — one CLI (`serverctl.py`)

Single entry point, plain Python — works identically in Git Bash, PowerShell,
cmd, and herdr tabs. **No `.bat` files, no shell scripts, no popups.**

```bash
venv/Scripts/python.exe serverctl.py status      # RUNNING <pid> + url / STOPPED
venv/Scripts/python.exe serverctl.py start       # start; no-op if already running
venv/Scripts/python.exe serverctl.py stop
venv/Scripts/python.exe serverctl.py restart
venv/Scripts/python.exe serverctl.py logs [N]    # tail server log (default 40)
venv/Scripts/python.exe serverctl.py serve       # foreground (Ctrl-C stops)
```

Pipeline pass-throughs (run in the foreground with the venv python):

```bash
venv/Scripts/python.exe serverctl.py scrape      # -> scraper.py
venv/Scripts/python.exe serverctl.py combine     # -> combiner.py
venv/Scripts/python.exe serverctl.py clean       # -> clean_scraped_files.py
```

In Git Bash with the venv activated, `python serverctl.py status` also works.

Open <http://127.0.0.1:5000>. Runs on localhost only (host `127.0.0.1`) — it is
not exposed to the network. Runs on localhost only (host `127.0.0.1`) — it is
not exposed to the network.

## What it gives you

| Panel | Function |
|---|---|
| **Scrape chapters** | Website dropdown (auto-populated from `scraper_configs.json`), novel name/slug, chapter range → starts the scraper. |
| **Job console** | Live stream (SSE) of the scraper/combiner console output. |
| **Combine → TXT/EPUB** | Pick a downloaded novel, output format, chapter marker (`full`/`simple`/`none`), text cleaning, EPUB title/author, optional chapter sub-range. |
| **Library** | `downloads/<novel>/` folders with chapter counts + existing EPUB/TXT outputs, each with a download link. |

One background job runs at a time; a second request gets HTTP 409.

## API (for scripting)

- `GET  /api/websites` — list from `scraper_configs.json`
- `GET  /api/library` — novels, epubs, combined txt files
- `GET  /api/job` / `GET /api/job/stream` — current job status / SSE log
- `POST /api/scrape` — `{website, novel_name, novel_slug, start_chapter, end_chapter}`
- `POST /api/combine` — `{novel, operation: "epub"|"txt", chapter_marker, clean_text, epub_title, epub_author, start_chapter?, end_chapter?, output_path?}`
- `GET  /api/download?file=<name>` — download from `downloads/` or `downloads/epub/`
  (name-validated; relative output paths resolve against the project dir)

## Implementation notes

- Server lifecycle: `serverctl.py` probes `GET /api/job` to detect a running
  instance, looks up the listening PID via `netstat -ano` (the venv
  `python.exe` is a launcher, so the spawned PID may differ from the
  interpreter's), and keeps `.artifacts/webapp-server.pid` in sync. `start`
  is a no-op when the probe succeeds — never two servers. `serverctl.py` is
  the ONLY entry point (no .bat / shell scripts — they trigger Windows file
  associations and popups).
- Progress capture: the scraper/combiner `print()` to stdout, which is
  redirected into the job log via `contextlib.redirect_stdout` (console output
  is preserved too).
- The single-page UI is `templates/index.html` (vanilla JS, no build step).
- `flask` was added to `requirements.txt`.
- Do NOT enable Flask's debug reloader — it double-spawns the Chrome-driving
  threads.
- Captcha/rate-limit behavior is unchanged: the scraper still stops the whole
  range; you'll see `⚠ Stopping early` in the job console.
