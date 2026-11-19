# Scraping a New Novel from an Already-Supported Website

The website is already configured in `scraper_configs.json` — you only need to point
`quick_config.json` at the new novel. No code or config changes to the scraper itself.

## Step-by-step

1. **Open the novel's index page** in your browser (the page listing all chapters) and
   copy its URL, e.g. `https://bettertranslation9.wordpress.com/some-other-novel-name/`

2. **Find the novel's slug** — the last part of that URL: `some-other-novel-name`

3. **Edit `quick_config.json`** in the project root:
   ```json
   {
     "website": "bettertranslation9.wordpress.com",
     "novel_name": "some-other-novel-name",
     "novel_slug": "some-other-novel-name",
     "start_chapter": 1,
     "end_chapter": 5
   }
   ```
   - `novel_slug` — the URL part from step 2 (for TOC sites like
     bettertranslation9.wordpress.com, this is the index page's URL slug)
   - `novel_name` — download folder name under `downloads/` (keep it the same as the
     slug; the EPUB name follows it too)

4. **Test with a small range first** (chapters 1–3): run `run_scraper.bat`, then check
   `downloads/<novel_name>/1.txt` — it should start with `Chapter 1: ...` and contain
   real story text.

5. **Download everything** — set `end_chapter` to the last chapter number on the index
   page (a bigger number is safe: missing chapters just report "not found") and run
   `run_scraper.bat` again. Already-downloaded chapters are skipped automatically, so
   you can stop and resume anytime.

6. **Generate the EPUB**:
   ```bash
   venv\Scripts\python.exe combiner.py --epub --input downloads/some-other-novel-name ^
     --output downloads/epub/some-other-novel-name.epub --clean ^
     --title "Novel Title" --author "BetterTranslation"
   ```

## Notes & caveats

- **TOC-based sites** (config has `"use_toc": true`, e.g.
  bettertranslation9.wordpress.com): chapters are found by matching `Chapter <N>` in the
  index page's link text. If a novel names its chapter links differently (e.g. "Part 5"
  or a different site section per novel), the TOC will come back empty — that needs a
  tweak to `toc_link_pattern` in `scraper_configs.json` (or a new code path if the
  structure differs entirely; follow `.docs/test-new-website-workflow.md`).
- **URL-pattern sites** (all other sites): `novel_slug` is whatever appears in the
  chapter URL where the site's `url_pattern` says `{novel_slug}` — check an existing
  chapter URL in the browser to confirm.
- Only ONE novel can be scraped per run (one `quick_config.json`); change the file
  between runs.
