# NovelScrape File Structure Guide

This document explains the actual file organization and naming in the NovelScrape project.

## Main Scripts

| File | Purpose | Notes |
|------|---------|-------|
| `scraper.py` | **Unified scraper** for all 12 supported websites | Replaces all individual website scrapers |
| `combiner.py` | **Unified combiner** - merges chapters or creates EPUB | Replaces `combine.py`, `combine_epub.py`, etc. |
| `clean_scraped_files.py` | Removes 'Comments' sections from scraped files | Additional cleanup utility |
| `clean_epub_file.py` | EPUB cleaning utility | For EPUB-specific cleanup |
| `scraper_bkp.py` | Backup copy of scraper | Historical backup |

> **Important**: The documentation may refer to `unified_scraper.py` and `unified_combiner.py`. These are the **actual file names** in the codebase: `scraper.py` and `combiner.py`.

## Batch Files (Windows)

| File | Runs | Purpose |
|------|------|---------|
| `run_scraper.bat` | `scraper.py` | Quick way to run the scraper with venv |
| `run_combiner.bat` | `combiner.py` | Quick way to run the combiner with venv |

## Configuration Files

| File | Purpose |
|------|---------|
| `scraper_configs.json` | Website configurations (URL patterns, timeouts, etc.) |

## Memory Bank (Backups)

The memory bank modules are located in the `backups/` directory:

| File | Purpose |
|------|---------|
| `backups/memory_bank.py` | Core MemoryBank class |
| `backups/memory_bank_cli.py` | CLI for managing the memory bank |
| `backups/combine_with_memory.py` | Combiner with memory bank integration |
| `backups/ninestar_scraper_with_memory.py` | Backup of memory-enabled scraper |

> Note: `ninestar_scraper_with_memory.py` exists in the root directory and is the active memory-enabled scraper for Nine Star Hegemon Body Arts.

## Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `usage.md` | Detailed usage examples for combiner |
| `tut.md` | Tutorial/guide |
| `docs/QUICK_MODE_USAGE.md` | Quick mode configuration guide |
| `docs/README_UNIFIED_COMBINER.md` | Unified combiner documentation |
| `docs/README_MEMORY_BANK.md` | Memory bank system documentation |
| `docs/memory-bank/` | Memory bank design documents |
| `docs/rules/` | Project rules and organization standards |

## Directories

| Directory | Purpose |
|-----------|---------|
| `downloads/` | Downloaded chapter files (gitignored) |
| `backups/` | Backup scripts and memory bank modules |
| `webdriver/` | Chrome driver executables |
| `docs/` | Documentation files |
| `venv/` | Python virtual environment (gitignored) |
| `chromeprofile/` | Chrome profile for anti-bot detection (gitignored) |

## Common Confusions

### Q: Why are the files named differently than in documentation?

**A:** The documentation was written with intended names (`unified_scraper.py`, `unified_combiner.py`) but the actual files are `scraper.py` and `combiner.py`.

### Q: Which scraper should I use?

**A:** Use `scraper.py` - it's the main unified scraper with support for all 12 websites.

### Q: Which combiner should I use?

**A:** Use `combiner.py` - it's the unified combiner for TXT and EPUB creation.

## Quick Reference

### Scrape a novel:
```bash
# Edit scraper.py to configure QUICK_MODE
python scraper.py
# or use run_scraper.bat
```

### Combine chapters:
```bash
# Edit combiner.py to configure QUICK_MODE
python combiner.py
# or use run_combiner.bat
```

### Clean scraped files (remove Comments):
```bash
# Edit clean_scraped_files.py to set the directory
python clean_scraped_files.py
```

### Use memory bank:
```bash
# List novels
python backups/memory_bank_cli.py list

# Run memory-enabled scraper
python ninestar_scraper_with_memory.py
```

## Script Relationship Diagram

```
scraper.py ───────────────────────┐
   │                               │
   ├── downloads/                ├──> scraper_configs.json
   │                               │
combiner.py ────────────────────┘
   │
   ├── downloads/
   │
   ├── clean_scraped_files.py (for Comments removal)
   └── clean_epub_file.py (for EPUB cleanup)

Memory Bank (backups/):
├── memory_bank.py ──┐
├── memory_bank_cli.py ──┤
├── combine_with_memory.py ──┼──> memory_bank.json
└── ninestar_scraper_with_memory.py ──┘
```