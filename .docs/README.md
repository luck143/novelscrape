# .docs — NovelScrape

Current documentation. (`.docs/archive/` holds older/historical docs; partially stale.)

- `add-a-website.md` — **How to extend scraping to a new website**: the recipe, the
  debugging loop, and when code changes (vs config-only) are needed.
- `usage.md` — combiner usage examples and workflows (paths updated for the current layout).
- `../AGENTS.md` — project conventions and architecture map for agents (read first).
- `../README.md` — user-facing overview, install, config reference (kept current).
- `archive/` — old docs kept for reference: memory-bank notes, old file-structure docs,
  `tut.md`, `tut.txt`, `usage.txt`. Referenced old filenames (`unified_scraper.py`,
  `docs/`, `webdriver/`) no longer exist — do not follow them.

## How the system works (30-second version)

1. `scraper.py` loads `scraper_configs.json` → `UnifiedScraper`.
2. For each chapter N in range: build URL from the site's `url_pattern`, open it in
   (undetected) Chrome, wait per `wait_type`/`wait_selector` + `delay` seconds, extract
   text with **trafilatura** (site-agnostic), check for captcha/404, retry up to 2×,
   save `downloads/<novel_name>/chapter_N.txt`.
3. `combiner.py` sorts the chapter files (natural sort), optionally cleans text (via
   `textutils.py`), writes one combined TXT (downloads/) and/or builds an EPUB with
   ebooklib (downloads/epub/ — generated outputs kept separate from raw chapters).
