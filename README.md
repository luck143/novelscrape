# NovelScrape

A Python-based web scraping system for downloading novel chapters from multiple novel hosting websites and converting them to readable formats (TXT and EPUB).

## Features

- **Multi-Website Support**: Scrape from 12 different novel hosting platforms
- **Anti-Bot Detection**: Bypasses basic anti-scraping measures using undetected_chromedriver
- **Progress Tracking**: Resume interrupted downloads without losing progress
- **Format Conversion**: Convert scraped content to TXT or EPUB formats
- **Text Cleaning**: Remove unwanted patterns and formatting issues from scraped text
- **Unified Interface**: Single scraper script for all supported websites

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

#### 1. Unified Scraper (`unified_scraper.py`)

Download novel chapters from any supported website.

**Interactive Mode:**
```bash
python unified_scraper.py
```

**Quick Mode:**
Edit the configuration at the top of `unified_scraper.py`:
```python
QUICK_MODE = True
website = 'empirenovel.com'
novel_name = 'nine-star-hegemon-body-arts'
novel_slug = 'nine-star-hegemon-body-arts'
start_chapter = 1
end_chapter = 10
```

Then run:
```bash
python unified_scraper.py
```

#### 2. Unified Combiner (`unified_combiner.py`)

Combine downloaded chapters into a single TXT file or create an EPUB.

**Interactive Mode:**
```bash
python unified_combiner.py
```

**Quick Mode:**
Edit the configuration at the top of `unified_combiner.py`:
```python
QUICK_MODE = True
operation = 'epub'  # or 'combine'
input_path = 'downloads/nine-star-hegemon-body-arts'
output_path = 'downloads/nine-star-hegemon-body-arts.epub'
clean_text = False
```

Then run:
```bash
python unified_combiner.py
```

**CLI Examples:**
```bash
# Combine TXT files
python unified_combiner.py --combine --input downloads/novelname --output combined.txt

# Create EPUB
python unified_combiner.py --epub --input downloads/novelname --output novel.epub --title "My Novel" --author "Author"

# Combine with text cleaning
python unified_combiner.py --combine --input downloads/novelname --clean
```

### Common Workflow

1. **Download Chapters:**
   ```bash
   python unified_scraper.py
   # Select website, enter novel name, slug, and chapter range
   ```

2. **Create EPUB:**
   ```bash
   python unified_combiner.py --epub --input downloads/novelname --clean
   ```

3. **Enjoy Reading:**
   - Open the EPUB file in your favorite e-reader
   - Or read the combined TXT file

### Text Cleaning

Some websites use anti-bot measures that add dots between letters. Use the `--clean` flag to remove these:

```bash
python unified_combiner.py --epub --input downloads/novelname --clean
```

This removes patterns like:
- `T.h.e. y.o.u.n.g.` → `The young.`
- `f.u.c.` → `fuc`
- `.+` patterns

## Project Structure

```
novelscrape/
├── unified_scraper.py          # Main scraper for all websites
├── unified_combiner.py         # Combine chapters or create EPUB
├── scraper_configs.json         # Website configurations
├── clean_epub_file.py         # EPUB cleaning utility
├── downloads/                 # Downloaded chapters (gitignored)
├── webdriver/                 # Chrome driver executables
├── .kilocode/               # Project documentation and rules
│   ├── docs/                 # Documentation files
│   ├── rules/                # Project rules
│   └── artifacts/            # Reports, logs, plans
└── README.md                 # This file
```

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
- `captcha_detection`: Enable captcha detection
- `use_next_link`: Check for next chapter link
- `use_standard_chrome`: Use standard Chrome (for some websites)

### Quick Mode Configuration

Both `unified_scraper.py` and `unified_combiner.py` support quick mode:

1. Set `QUICK_MODE = True` at the top of the file
2. Edit the configuration variables
3. Run the script without arguments

## Troubleshooting

### Chrome Version Mismatch

If you get a Chrome driver error:

```python
# In unified_scraper.py or specific scraper:
driver = uc.Chrome(version_main=127)  # Set to your Chrome version
```

Check your Chrome version at `chrome://version/`

### Captcha Detection

The scraper automatically detects common captchas and stops:
- "You need to enable JavaScript to run this app"
- "Anonymous users can read up to 10 chapters"

If detected, wait or use a different approach.

### Files in Wrong Order

- **TXT combining**: Files sorted by modification time
- **EPUB creation**: Files sorted naturally (1, 2, 10, etc.)

## Advanced Usage

For detailed usage examples and advanced features, see:
- [`usage.md`](usage.md) - Comprehensive usage guide
- [`.kilocode/docs/README_UNIFIED_COMBINER.md`](.kilocode/docs/README_UNIFIED_COMBINER.md) - Unified combiner documentation
- [`.kilocode/docs/QUICK_MODE_USAGE.md`](.kilocode/docs/QUICK_MODE_USAGE.md) - Quick mode guide

## Specialized Scripts

The project includes specialized scripts for specific websites:

- **wanderinginn/** - Scripts for wanderinginn.com (not supported by unified scraper)
  - `dummy.py` - Custom scraper
  - `toepub.py` - Custom EPUB creator

## Memory Bank (Planned Feature)

A memory bank system is planned to enable:
- Progress tracking across sessions
- Resume from last downloaded chapter
- Prevent duplicate downloads
- Status management (downloading, paused, completed, error)

Reference implementation: [`ninestar_scraper_with_memory.py`](ninestar_scraper_with_memory.py)

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
- Check documentation in `.kilocode/docs/`
- Review `usage.md` for detailed examples
- Test with small chapter ranges first

---

**Happy Reading! 📚**
