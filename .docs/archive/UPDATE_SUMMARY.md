# Documentation Update Summary

This document summarizes the changes made to align documentation with the current codebase.

## Date: 2025-08-14

## Changes Made

### 1. File Name Corrections

| Old Reference | New Reference | Files Updated |
|---------------|---------------|---------------|
| `unified_scraper.py` | `scraper.py` | README.md, QUICK_MODE_USAGE.md, usage.md, README_UNIFIED_COMBINER.md |
| `unified_combiner.py` | `combiner.py` | README.md, QUICK_MODE_USAGE.md, usage.md, README_UNIFIED_COMBINER.md |

### 2. Batch Files Fixed

- **run_scraper.bat**: Changed from `unified_scraper.py` → `scraper.py`
- **run_combiner.bat**: Changed from `unified_combiner.py` → `combiner.py`

### 3. Memory Bank Documentation Updated

Updated `docs/README_MEMORY_BANK.md` to reflect that memory bank modules are in `backups/`:
- `memory_bank.py` → `backups/memory_bank.py`
- `memory_bank_cli.py` → `backups/memory_bank_cli.py`
- `combine_with_memory.py` → `backups/combine_with_memory.py`

### 4. New Documentation Created

- **docs/FILE_STRUCTURE.md**: Complete guide to file organization, naming, and relationships

### 5. Updated README.md

- Corrected all script references
- Added project structure including all actual files
- Added reference to FILE_STRUCTURE.md
- Clarified combiner.py is actually a scraper

### 6. Updated docs/QUICK_MODE_USAGE.md

- Changed all `unified_scraper.py` references to `scraper.py`
- Changed all `unified_combiner.py` references to `combiner.py`

### 7. Updated docs/README_UNIFIED_COMBINER.md

- Changed all `unified_combiner.py` references to `combiner.py`
- Updated integration workflow to use `scraper.py`
- Added note about `clean_scraped_files.py`

### 8. Rewrote usage.md

- Completely rewrote with correct script names
- All command examples now use `combiner.py`

## Current Script Names Summary

| Purpose | Actual File |
|---------|-------------|
| Main scraper | `scraper.py` |
| Unified combiner | `combiner.py` |
| Legacy scraper | `combiner.py` (confusingly named) |
| Memory scraper | `ninestar_scraper_with_memory.py` |
| Comments cleaner | `clean_scraped_files.py` |
| EPUB cleaner | `clean_epub_file.py` |

## Memory Bank Files Location

All memory bank related files are in the `backups/` directory:
- `memory_bank.py`
- `memory_bank_cli.py`
- `combine_with_memory.py`
- `ninestar_scraper_with_memory.py` (also in root)

## Files Not Modified (Already Correct)

- `docs/memory-bank/` directory (design docs)
- `docs/rules/` directory
- `tut.md`
- `.gitignore`

## Verification

To verify the documentation is now accurate:

1. Run scraper: `python scraper.py` or `run_scraper.bat`
2. Run combiner: `python combiner.py` or `run_combiner.bat`
3. Clean comments: `python clean_scraped_files.py` (edit directory first)
4. Memory bank CLI: `python backups/memory_bank_cli.py list`

## Notes

- The documentation discrepancy occurred because the intended names (`unified_scraper.py`, `unified_combiner.py`) were not used when the files were created
- `combiner.py` is actually a scraper, not a combiner - this is a historical naming issue
- The memory bank functionality is primarily in the backups folder, with `ninestar_scraper_with_memory.py` in the root as an active example