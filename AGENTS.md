# AGENTS.md — NovelScrape

Project conventions for agents working in this repo. Supersedes nothing here except the
global `~/.pi/agent/AGENTS.md` (which still applies).

## What this project is

A Python scraper that downloads novel chapters from 12 novel-hosting websites via
`undetected_chromedriver` + Selenium, saves each chapter as a TXT file, and converts
them into combined TXT / EPUB via `combiner.py`. No web framework, no tests, no lint
config — plain scripts run from `venv/`.

## Architecture (read before changing anything)

```
scraper.py            # Main entry. UnifiedScraper class; quick mode via quick_config.json
quick_config.json     # Quick-mode settings for the scraper (website, novel, chapter range)
quick_combiner_config.json  # Quick-mode settings for the combiner
scraper_configs.json  # Per-website config: url_pattern, wait_type/wait_selector, delay,
                      #   timeout, headless, chrome_version, captcha_detection,
                      #   use_next_link, use_standard_chrome
combiner.py           # Combines chapter TXTs -> single TXT or EPUB (ebooklib), with cleaning
textutils.py          # Shared clean_text_content — ONLY copy, import it elsewhere
requirements.txt      # Dependencies (install: venv/Scripts/pip.exe install -r requirements.txt)
clean_epub_file.py    # Post-fix for EPUB text artifacts
clean_scraped_files.py# Batch text cleaning of downloaded chapters
backups/              # Dead per-site scrapers + legacy one-offs — historical reference ONLY, never import
.docs/archive/        # Old memory-bank + historical docs (partially stale, kept for reference)
downloads/            # Chapters: downloads/<novel_name>/N.txt (gitignored)
downloads/epub/        # Generated EPUB outputs (combiner default; gitignored)
```

Pipeline: `scraper.py` → `downloads/<novel>/chapter_N.txt` → `combiner.py` → TXT/EPUB.

Key mechanics in `scraper.py`:
- **Quick mode = `quick_config.json`** (website / novel_name / novel_slug /
  start_chapter / end_chapter). Present + run with no CLI args → used automatically;
  absent → interactive prompts. Do NOT re-add a QUICK_MODE block at the top of the file.
- URL is built from `url_pattern` in `scraper_configs.json` via `.format(novel_slug=, chapter_num=)`.
- Content extraction: full `page_source` → `trafilatura.extract()` → `unidecode`.
  If a site needs it, add `"content_selector": "<css>"` to its config to extract only
  that element first (fallback to full page). There is otherwise no per-site HTML parsing.
- Per-site differences live ONLY in `scraper_configs.json` (wait condition, delay,
  captcha detection, standard-vs-undetected Chrome, `use_next_link`).
- Captcha/rate-limit detection sets `stop_requested` and stops the whole range — never
  remove that break.

Shared helpers:
- `textutils.py` — the ONLY home of `clean_text_content`. Never copy it into another file;
  import it (see `combiner.py`, `clean_epub_file.py`).

## Environment

- Python venv: `venv/Scripts/python.exe` — always run scripts with it (see `run_scraper.bat`, `run_combiner.bat`).
- Deps: see `requirements.txt` (selenium, undetected-chromedriver, trafilatura, unidecode, ebooklib).
- Requires local Google Chrome; `undetected_chromedriver` auto-detects version via registry
  (registry-detection fallback lives in `initialize_driver`).
- Shell: Git Bash on Windows. Never `>nul` (use `/dev/null`). Never `&&` inside `powershell.exe` (PS 5.1).

## Project-specific rules

- **Adding a website = edit `scraper_configs.json` only, in the first instance** (plus
  optionally `quick_config.json` for testing). See `.docs/add-a-website.md` for the full
  recipe and debugging loop. Only touch `scraper.py` code if the site genuinely needs new behavior.
- Deps are pinned in `requirements.txt` — install with
  `venv/Scripts/pip.exe install -r requirements.txt`.
- Do **not** refactor `scraper.py`/`combiner.py` opportunistically; they work. Smallest change wins.
- `backups/` is frozen history. Never import from it, never "clean it up" unless asked.
- Old docs moved to `.docs/archive/` are partially stale (reference old filenames like
  `unified_scraper.py`); current truth is this file, `README.md`, and `.docs/`.
- Downloads, `chromeprofile/`, `venv/`, `backups/` are gitignored or untracked — never commit them.
- Git: owner commits manually. Leave changes uncommitted; summarize what changed.

## Checks

No test suite, lint, or typecheck exists. Verification = a real scrape of a small chapter
range (2–3 chapters) against the target site, plus `python -m py_compile scraper.py combiner.py`.
