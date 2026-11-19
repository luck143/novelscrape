# Testing a New Website — Strict Workflow

Owner directive: these rules apply to EVERY new website added to NovelScrape.

1. **Experimental scripts first.** Create `experimental/<site-slug>/` (or
   `experimental/scrape_<site>.py` + `experimental/<site>_config.json`), following the
   project's architecture and conventions (config-file driven, Selenium driver init,
   trafilatura + unidecode extraction, `downloads/<novel>/N.txt` layout).
2. **Main pipeline untouched.** Never edit `scraper.py`, `scraper_configs.json`,
   `quick_config.json`, `combiner.py`, or `textutils.py` during the experimental phase.
3. **Full pipeline test.** The experiment must cover: scraping chapters, merging in the
   correct order, cleaning/formatting, and EPUB generation (combiner is reused via
   `--epub --input ... --output ... --clean`).
4. **Validate.** Check extracted text quality (headings, no page furniture), natural
   sort order, and the EPUB structurally (zip integrity, nav.xhtml entries, per-chapter
   XHTML well-formedness and word counts) before reporting.
5. **Merge only on explicit approval.** Integrate into `scraper.py`/
   `scraper_configs.json` only when the owner explicitly asks.

## Reference implementation

- `experimental/bettertranslation9/scrape.py` — TOC-driven scraper for
  bettertranslation9.wordpress.com (irregular date-slug chapter URLs cannot use
  `url_pattern.format(chapter_num=)`; instead a `toc` command builds `toc.json`
  mapping chapter numbers to URLs/titles, and `scrape --start N --end M` downloads
  from that map). Site files live in `experimental/bettertranslation9/`:
  `scrape.py`, `config.json`, `combiner_config.json`, `toc.json`.
- Config: `experimental/bettertranslation9/config.json` (same shape as
  `scraper_configs.json` entries + `toc_link_pattern`, `trailing_markers`).
- Status: **INTEGRATED into the main scraper** (owner approval). Site entry
  `bettertranslation9.wordpress.com` in `scraper_configs.json` with `use_toc: true`;
  TOC-driven scraping + `trailing_markers` support added to `scraper.py`. End-to-end
  test via `scraper.py` produced byte-identical output to this experimental pipeline.
