# Extending NovelScrape to a new website

The scraper was designed so most sites need **zero code changes** — only a new entry in
`scraper_configs.json`. Content extraction is generic (trafilatura over the whole page),
so a site works if: (a) its chapter URLs follow a predictable pattern, and (b) the
chapter text is the main readable content of the page.

## 1. Recon (5 minutes, no code)

Open 2–3 chapter pages of the target novel in your browser and note:

1. **URL pattern** — e.g. `https://site.com/novel/<slug>/chapter-<N>/`. Find the slug and
   whether chapter numbers appear as `chapter-123`, `/123`, `_123.html`, etc.
2. **Does the text load without JavaScript?** View-source and check the chapter text is
   in the HTML. If it's injected by JS, this scraper still works (it uses a real browser),
   but you'll need a proper `wait_selector`.
3. **A reliable element that appears only when the page is loaded** — an element `id`
   (best), a `class`, or nothing (fall back to a plain delay).
4. **Anti-bot behavior** — does a plain browser get through? Is there a Cloudflare
   check / captcha? Does it rate-limit fast clicks?

## 2. Add the config entry

Append to `scraper_configs.json` under `"websites"`:

```json
"newsite.com": {
  "name": "NewSite",
  "url_pattern": "https://newsite.com/novel/{novel_slug}/chapter-{chapter_num}/",
  "wait_type": "ID",
  "wait_selector": "chapter-content",
  "timeout": 20,
  "delay": 2,
  "headless": false,
  "chrome_version": null,
  "captcha_detection": true,
  "use_next_link": false,
  "use_standard_chrome": false
}
```

Field meanings (and what existing sites use them for):

| Field | Meaning |
|---|---|
| `url_pattern` | Python `.format()` template with `{novel_slug}` and `{chapter_num}` |
| `wait_type` | `ID`, `CLASS_NAME`, `TAG_NAME`, `CSS_SELECTOR`, or `none` (just sleep `delay`) |
| `wait_selector` | The locator value; ignored when `wait_type` is `none` |
| `timeout` | Seconds for the explicit wait (0 when `wait_type` is `none`) |
| `delay` | Extra sleep after load — politeness/rendering buffer; raise for slow or rate-limiting sites (wuxiaworld uses 10) |
| `headless` | `true` only for sites with no bot protection (novelontop); headless is more detectable |
| `chrome_version` | Pin major Chrome version for `uc.Chrome(version_main=…)` only when auto-detect fails; `null` = auto-detect via registry |
| `captcha_detection` | Scan extracted text for captcha signatures and abort (stops the whole run) |
| `use_next_link` | `true` = fetch the first chapter via the URL pattern, then follow the page's next-chapter link (`wait_selector` used as its element ID) for subsequent chapters (novelbin/novlove — for sites where chapter numbers aren't URL-predictable) |
| `use_standard_chrome` | `true` = plain Selenium + persistent `chromeprofile/` dir instead of undetected_chromedriver (lightnovelworld.co — needed when UC's patching itself trips the site) |
| `content_selector` | Optional CSS selector for the chapter-text container. Set it when trafilatura on the full page picks up menus/ads instead of the chapter. Falls back to the full page if the element is missing |

## 3. Test loop

1. Set `quick_config.json` in the project root (website / novel_name / novel_slug /
   start_chapter / end_chapter), e.g. `"website": "newsite.com"`, real slug, 1→3.
2. Run: `./run_scraper.bat` (or `venv/Scripts/python.exe scraper.py`).
3. Open `downloads/<novel_name>/chapter_1.txt` — check the text is the actual chapter,
   not navigation menus, ads, or "please enable JavaScript".
4. If extraction is noisy/wrong → this site needs a code change (see §4). If it's good →
   scrape a slightly wider range (e.g. 10 chapters) to check rate limiting, then done.

## 4. When config isn't enough (code changes)

All extraction lives in `UnifiedScraper` in `scraper.py`. In increasing order of effort:

- **Trafilatura picks the wrong block** (menus/ads instead of chapter): add a per-site
  `"content_selector": "<css>"` to the config — `extract_content()` will pull that
  element's HTML (falling back to the full page) before calling trafilatura. This is
  config-only; no code change needed.
- **Chapter numbers not in the URL**: `use_next_link: true` already handles this — check
  `scrape_chapter()` follows the `next_chap`/next link element; you may need to add the
  site's next-link selector there.
- **Captcha/challenge page**: keep `captcha_detection: true`; if the site is behind
  Cloudflare's managed challenge, run non-headless with `use_standard_chrome: true` and a
  warm profile (solve once manually, then the profile keeps cookies).
- **Different chapter-numbering scheme** (e.g. `chapter_0012.html` zero-padded, or
  offset numbering): add a `url_builder` variant or a `chapter_num_offset`/
  `zero_pad` config field handled in `build_url()`.

## 5. Housekeeping after adding a site

- Add the domain to the Supported Websites list in `README.md`.
- Note in the config comment / README which novel + date you verified it with (existing
  entries record "most recently tested" sites this way).
- If the site's `url_pattern` duplicates another site's (see novlove.com → novelbin.com
  pattern), keep `name` distinct so interactive mode stays clear.
