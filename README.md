# NovelScrape

A Python-based web scraping system for downloading novel chapters from multiple novel hosting websites and converting them to readable formats (TXT and EPUB).

## Features

- **Multi-Website Support**: Scrape from 12 different novel hosting platforms
- **Anti-Bot Detection**: Bypasses basic anti-scraping measures using undetected_chromedriver
- **Progress Tracking**: Resume interrupted downloads without losing progress
- **Format Conversion**: Convert scraped content to TXT or EPUB formats
- **Text Cleaning**: Remove unwanted patterns and formatting issues from scraped text
- **Unified Interface**: Single scraper script for all supported websites
- **Web Dashboard**: Local web UI (`webapp.py`) for scraping, combining, and downloading — control it with `venv\Scripts\python.exe serverctl.py start|stop|restart|status|logs` (works in any shell, never spawns a duplicate); see `.docs/web-dashboard.md`

## Supported Websites

NovelScrape currently supports the following websites:

1. **empirenovel.com** - EmpireNovel ⭐ (Most recently tested with nine-star-hegemon-body-arts)
2. **boxnovel.com** - BoxNovel
3. **novelfull.com** - NovelFull
4. **lightnovelworld.co** - LightNovelWorld
5. **novelbin.com** - NovelBin
6. **novelontop.com** - NovelOnTop
7. **novlove.com** - NovLove
8. **readlightnovel.meme** - ReadLightNovel
9. **wuxiaworld.com** - WuxiaWorld
10. **wuxiaz.com** - WuxiaZ
11. **novelhi.com** - NovelHi
12. **freewebnovel.com** - FreeWebNovel

> **Note:** Website domains may change over time. EmpireNovel has been most recently tested and verified working with the example novel "nine-star-hegemon-body-arts".

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (managed by undetected-chromedriver)

### Setup

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
# or individually:
pip install selenium undetected-chromedriver trafilatura unidecode ebooklib
```

3. (Optional) Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

## Usage

### Quick Start

The project provides two main tools:

#### 1. Unified Scraper (`scraper.py`)

Download novel chapters from any supported website.

**Interactive Mode:**
```bash
python scraper.py
```

**Quick Mode:**
Create `quick_config.json` in the project root:
```json
{
  "website": "empirenovel.com",
  "novel_name": "nine-star-hegemon-body-arts",
  "novel_slug": "nine-star-hegemon-body-arts",
  "start_chapter": 1,
  "end_chapter": 10
}
```

Then run:
```bash
python scraper.py
```

**CLI Mode:**
```bash
python scraper.py --website empirenovel.com --novel-name nine-star-hegemon-body-arts --novel-slug nine-star-hegemon-body-arts --start 1 --end 10
```

#### 2. Unified Combiner (`combiner.py`)

Combine downloaded chapters into a single TXT file or create an EPUB.

**Interactive Mode:**
```bash
python combiner.py
```

**Quick Mode:**
Create `quick_combiner_config.json` in the project root:
```json
{
  "operation": "epub",
  "input_path": "downloads/nine-star-hegemon-body-arts",
  "output_path": "downloads/epub/nine-star-hegemon-body-arts.epub",
  "clean_text": true
}
```

Then run:
```bash
python combiner.py
```

**CLI Examples:**
```bash
# Combine TXT files
python combiner.py --combine --input downloads/novelname --output combined.txt

# Create EPUB
python combiner.py --epub --input downloads/novelname --title "My Novel" --author "Author"

# Combine with text cleaning
python combiner.py --combine --input downloads/novelname --clean
```

### Common Workflow

1. **Download Chapters:**
   ```bash
   python scraper.py
   # Select website, enter novel name, slug, and chapter range
   ```

2. **Create EPUB:**
   ```bash
   python combiner.py --epub --input downloads/novelname --clean
   ```

3. **Enjoy Reading:**
   - Open the EPUB file in your favorite e-reader
   - Or read the combined TXT file

### Text Cleaning

Some websites use anti-bot measures that add dots between letters. Use the `--clean` flag to remove these patterns (via `textutils.py` — normal punctuation like `e.g` and sentence periods is preserved):

```bash
python combiner.py --epub --input downloads/novelname --clean
```

This removes patterns like:
- `T.h.e. y.o.u.n.g.` → `The young.`
- `f.u.c.` → `fuc`
- `.+` patterns

## Project Structure

```
novelscrape/
├── scraper.py                  # Main scraper for all websites
├── combiner.py                 # Combine chapters or create EPUB (EPUBs → downloads/epub/)
├── textutils.py                # Shared text-cleaning helpers
├── scraper_configs.json        # Website configurations
├── quick_config.json           # Quick-mode settings for scraper.py
├── quick_combiner_config.json  # Quick-mode settings for combiner.py
├── requirements.txt            # Dependencies
├── clean_epub_file.py          # EPUB cleaning utility
├── clean_scraped_files.py      # Remove 'Comments' sections from files
├── run_scraper.bat             # Quick run scraper (Windows)
├── run_combiner.bat            # Quick run combiner (Windows)
├── AGENTS.md                   # Conventions for coding agents
├── .docs/                      # Documentation (usage.md, add-a-website.md, archive/)
├── backups/                    # Frozen historical scripts — never import
├── chromeprofile/              # Persistent Chrome profile (gitignored)
├── downloads/                  # Raw chapters: downloads/<novel>/N.txt (gitignored)
│   └── epub/                   # Generated EPUB outputs (gitignored)
└── venv/                       # Python virtual environment (gitignored)
```

> **Note**: Old documentation lives in `.docs/archive/`. Current docs: this README,
> `AGENTS.md`, `.docs/README.md`, `.docs/add-a-website.md`, `.docs/usage.md`,
> `.docs/scrape-new-novel.md`.

## Configuration

### Website Configuration

Website configurations are stored in `scraper_configs.json`. Each website includes:

- `url_pattern`: URL pattern for chapter pages
- `wait_type`: Element wait type (CLASS_NAME, ID, none)
- `wait_selector`: CSS selector to wait for
- `timeout`: Page load timeout in seconds
- `delay`: Additional delay after page load
- `headless`: Run Chrome in headless mode
- `chrome_version`: Specific Chrome version (if needed)
- `captcha_detection`: Enable captcha detection (stops the whole run when triggered)
- `use_next_link`: Follow the page's next-chapter link instead of building URLs
- `use_standard_chrome`: Use standard Chrome (for some websites)
- `content_selector`: Optional CSS selector for the chapter text container (used when
  full-page extraction picks up menus/ads)

### Quick Mode Configuration

Both `scraper.py` and `combiner.py` support quick mode via JSON files in the project root:

1. `scraper.py` → `quick_config.json`
2. `combiner.py` → `quick_combiner_config.json`
3. Run the script without arguments and the JSON is used automatically
4. Without the JSON file (or with CLI arguments), you get interactive/CLI mode

## Troubleshooting

### Chrome Version Mismatch

If you get a Chrome driver error:

```python
# In scraper.py or specific scraper:
driver = uc.Chrome(version_main=127)  # Set to your Chrome version
```

Check your Chrome version at `chrome://version/`

### Captcha Detection

The scraper automatically detects common captchas and stops:
- "You need to enable JavaScript to run this app"
- "Anonymous users can read up to 10 chapters"

If detected, wait or use a different approach.

### Files in Wrong Order

- Both TXT combining and EPUB creation sort files **naturally** (1, 2, 10, etc.) in the
  same order — see `get_txt_files()` in `combiner.py`.

## Advanced Usage

For detailed usage examples and advanced features, see:
- [`.docs/usage.md`](.docs/usage.md) - Comprehensive usage guide
- [`.docs/scrape-new-novel.md`](.docs/scrape-new-novel.md) - How to scrape another novel from an already-supported website
- [`.docs/add-a-website.md`](.docs/add-a-website.md) - How to add a new website

## Memory Bank (Not Implemented)

A memory bank system was explored but never completed; the scraper's built-in resume
(skip existing chapter files) covers the practical need. Historical reference code lives
in `backups/` (`ninestar_scraper_with_memory.py`, `memory_bank.py`, `memory_bank_cli.py`).

## Legal Notice

This tool is for personal use only. Please respect:
- Website terms of service
- Copyright and intellectual property
- Rate limiting and anti-bot measures

## Contributing

Contributions are welcome! Areas for improvement:
- Support for additional websites
- Memory bank implementation
- Automatic Chrome driver updates
- Better error handling and retry logic

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or suggestions:
- Review [`.docs/usage.md`](.docs/usage.md) for detailed examples
- Test with small chapter ranges first

---

**Happy Reading! 📚**
