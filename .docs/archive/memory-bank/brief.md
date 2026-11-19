# NovelScrape Project Brief

## Project Purpose

NovelScrape is a Python-based web scraping system designed to download novel chapters from various novel hosting websites and convert them into readable formats (TXT and EPUB).

## Core Goals

1. **Scrape Novel Chapters**: Download chapters from multiple novel websites with anti-bot detection bypass
2. **Track Progress**: Maintain download progress to resume interrupted downloads
3. **Publish to EPUB**: Convert scraped chapters into EPUB format for e-reader compatibility
4. **Clean Content**: Remove unwanted patterns and formatting issues from scraped text
5. **Support Multiple Sources**: Work with various novel hosting platforms

## Project Scope

- **Websites Supported**: boxnovel.com, novelfull.com, empirenovel.com, lightnovelworld.co, novelbin.com, novelontop.com, novlove.com, readlightnovel.meme, wuxiaworld.com, wuxiaz.com, novelhi.com, freewebnovel.com
- **Output Formats**: Individual chapter TXT files, combined TXT files, EPUB files
- **Key Features**: Memory bank for progress tracking, captcha detection, text cleaning, chapter combining

## Current State

The project has a unified scraper script ([`unified_scraper.py`](unified_scraper.py)) that supports 12 different novel websites, combine scripts to merge chapters, EPUB publishing utilities, and text cleaning tools. A memory bank system is partially implemented (referenced but the core module is missing).

**Note**: Individual scraper scripts have been removed in favor of the unified scraper. All website configurations are now managed in [`scraper_configs.json`](scraper_configs.json).

## Known Limitations

- Memory bank module (memory_bank.py) is referenced but not present in the codebase
- Each scraper is a standalone script with hardcoded novel names and chapter ranges
- No unified interface for managing multiple scrapers
- Chrome driver management requires manual updates
