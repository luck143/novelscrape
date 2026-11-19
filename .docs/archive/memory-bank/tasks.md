# NovelScrape Repetitive Tasks

This document contains workflows for common repetitive tasks in the NovelScrape project.

## Add Support for New Novel Website

**Last performed:** 2026-01-01 (during memory bank initialization)

**Files to modify:**
- Add configuration to [`scraper_configs.json`](scraper_configs.json)
- `unified_scraper.py` - Verify it works with new website configuration
- `combine.py` - Verify combine script works with new format
- `2_publish_epub.py` - Test EPUB publishing

**Steps:**
1. Add website configuration to [`scraper_configs.json`](scraper_configs.json) with all required fields
2. Test unified_scraper.py with the new website configuration
3. Verify trafilatura text extraction works correctly
4. Test with a few chapters before using for bulk downloads
5. Update this documentation to add the new website to the supported list

**Important notes:**
- Follow existing naming conventions for consistency
- Ensure proper error handling and timeout management
- Test with a few chapters before running full download
- Add chapter limit detection if applicable
- Update README_MEMORY_BANK.md with new scraper info

**Example implementation:**
```python
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import trafilatura
from unidecode import unidecode
import time
import sys

options = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True)

def scrape_data(novelname, chapter_num, url):
    driver.get(url)
    wait = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "element-class"))
    )
    time.sleep(1)
    content = driver.page_source
    text = trafilatura.extract(content)
    
    if 'You need to enable JavaScript to run this app' in text:
        print("Captcha Found")
        sys.exit("Stopped")
    
    filename = f"{chapter_num}.txt"
    with open(f'downloads/{novelname}/{filename}', 'w') as file:
        file.write(unidecode(text))

for x in range(start_chapter, end_chapter):
    url = f"https://example.com/novel/{novelname}/chapter-{x}"
    scrape_data(novelname, x, url)

driver.quit()
```

## Download and Process a Novel

**Last performed:** Ongoing

**Files to use:**
- [`unified_scraper.py`](unified_scraper.py) - Unified scraper for all websites
- [`unified_combiner.py`](unified_combiner.py) - Combine chapters or create EPUB (with optional cleaning)
- `clean_epub_file.py` - Clean EPUB files (optional)

**Steps:**
1. Run [`unified_scraper.py`](unified_scraper.py) and select the appropriate website
2. Enter novel name, novel slug, and chapter range when prompted
3. Wait for download to complete or resume if interrupted
4. Run [`unified_combiner.py`](unified_combiner.py) to merge chapters or create EPUB
   - Use `--clean` flag to remove formatting artifacts during combining
5. (Optional) Run clean_epub_file.py if EPUB needs cleaning

**Important notes:**
- Always test with a small chapter range first
- Check for captcha/limit messages during download
- Downloads are saved to `downloads/{novelname}/` directory
- Combined files are timestamped to avoid overwriting
- EPUB files are created in downloads/ directory by default
- Use `--epub` flag with unified_combiner.py to create EPUB directly from individual chapter files
- Use `--clean` flag with unified_combiner.py to clean text during combining (replaces clean_text_file.py)

## Combine Chapters into Single File

**Last performed:** Ongoing

**Files to use:**
- [`unified_combiner.py`](unified_combiner.py) - Unified combiner (recommended)

**Steps:**
1. Run [`unified_combiner.py`](unified_combiner.py) in interactive mode or with CLI arguments
2. Select "Combine TXT files" option
3. Enter novel name or path to chapter files
4. Choose chapter marker format (full, simple, or none)
5. Choose whether to clean text content (removes dots between letters, .+ patterns)
6. Enter output filename (optional, auto-generated if not provided)
7. Verify the combined file is created correctly

**CLI Examples:**
```bash
# Interactive mode
python unified_combiner.py

# Combine with full chapter markers
python unified_combiner.py --combine --input downloads/novelname --output combined.txt --marker full

# Combine with simple markers
python unified_combiner.py --combine --input downloads/novelname --marker simple

# Combine with no markers
python unified_combiner.py --combine --input downloads/novelname --marker none

# Combine with cleaning
python unified_combiner.py --combine --input downloads/novelname --clean
```

**Important notes:**
- Files are sorted by modification time to maintain order
- Chapter marker formats: full (`#Chapter 1 : 1`), simple (`#`), or none
- Output file is timestamped to avoid overwriting if not specified
- Legacy scripts (combine.py, 1_combine2.py, combine_epub.py, wanderinginn/combine.py) have been deleted

## Clean Text Files

**Last performed:** Ongoing

**Files to use:**
- [`unified_combiner.py`](unified_combiner.py) - Integrated cleaning with --clean flag (recommended)
- `clean_text_file.py` - Standalone cleaning script (deprecated)

**Steps (using unified_combiner.py):**
1. Run unified_combiner.py with --clean flag during combine or EPUB creation
2. Cleaning is applied automatically to each chapter
3. Output file contains cleaned content

**Example:**
```bash
# Combine with cleaning
python unified_combiner.py --combine --input downloads/novelname --clean

# Create EPUB with cleaning
python unified_combiner.py --epub --input downloads/novelname --clean
```

**Steps (using clean_text_file.py - deprecated):**
1. Run script with input file as argument
2. Script automatically creates output file with `_cleaned` suffix
3. Verify cleaned output

**Important notes:**
- Cleaning removes dots between letters (f.u.c.k → fuck)
- Removes .+ patterns
- Preserves legitimate punctuation
- Handles multiple encodings (utf-8, latin-1)
- unified_combiner.py integrates cleaning directly, avoiding extra step

## Create EPUB from Chapter Files

**Last performed:** Ongoing

**Files to use:**
- [`unified_combiner.py`](unified_combiner.py) - Create EPUB from individual TXT files (recommended)
- `2_publish_epub.py` or `2_publish_epub2.py` - Create EPUB from combined TXT file

**Steps (using unified_combiner.py):**
1. Run [`unified_combiner.py`](unified_combiner.py) in interactive mode or with CLI arguments
2. Select "Create EPUB from TXT files" option
3. Enter novel name or path to chapter files
4. Choose whether to clean text content (removes dots between letters, .+ patterns)
5. Enter EPUB title and author (optional)
6. Enter output EPUB filename (optional, auto-generated if not provided)
7. Verify EPUB file is created and readable

**CLI Examples:**
```bash
# Interactive mode
python unified_combiner.py

# Create EPUB with custom metadata
python unified_combiner.py --epub --input downloads/novelname --output novel.epub --title "My Novel" --author "Author Name"

# Create EPUB with auto-generated filename
python unified_combiner.py --epub --input downloads/novelname

# Create EPUB with cleaning
python unified_combiner.py --epub --input downloads/novelname --clean
```

**Steps (using 2_publish_epub.py or 2_publish_epub2.py):**
1. Edit the path variable to point to combined TXT file
2. Edit the output EPUB filename and title
3. Run the script
4. Verify EPUB file is created and readable

**Important notes:**
- unified_combiner.py creates EPUB directly from individual TXT files (no need to combine first)
- 2_publish_epub.py uses different chapter title extraction
- 2_publish_epub2.py handles "#Chapter 301 : 301" format better
- All scripts create proper EPUB structure with TOC
- Test EPUB in an e-reader before distribution

## Handle Chrome Driver Version Mismatch

**Last performed:** As needed

**Files to modify:**
- Any scraper script that fails with Chrome driver error

**Steps:**
1. Check Chrome version: chrome://version/
2. Find the version_main parameter in scraper
3. Update version_main to match Chrome version
4. Or remove version_main to let undetected_chromedriver auto-detect

**Example:**
```python
# Before (Chrome 127)
driver = uc.Chrome(use_subprocess=True, version_main=127)

# After (Chrome 128)
driver = uc.Chrome(use_subprocess=True, version_main=128)

# Or auto-detect
driver = uc.Chrome(use_subprocess=True)
```

**Important notes:**
- undetected_chromedriver usually auto-detects correctly
- Manual specification may be needed for newer Chrome versions
- ChromeDriver executable is in `webdriver/` directory
- Can also use webdriver-manager for automatic updates

## Debug Scraper Issues

**Last performed:** As needed

**Files to check:**
- [`unified_scraper.py`](unified_scraper.py) - The unified scraper
- [`scraper_configs.json`](scraper_configs.json) - Website configuration
- Website HTML structure (using browser dev tools)

**Steps:**
1. Check error message in terminal output
2. Verify URL pattern in scraper_configs.json is correct for the website
3. Check wait condition selector still exists on page
4. Test with a small chapter range first
5. Check for captcha or rate limit messages
6. Verify trafilatura is extracting content
7. Check file permissions for downloads directory

**Common issues:**
- Website structure changed → Update wait_selector in scraper_configs.json
- Chrome version mismatch → Update chrome_version in scraper_configs.json or remove to auto-detect
- Captcha detected → Wait or use different approach
- Rate limit reached → Wait before continuing
- Empty content → Check trafilatura extraction
- File not saving → Check directory permissions

## Memory Bank Integration (When Implemented)

**Last performed:** Not yet implemented

**Files to modify:**
- Create `memory_bank.py` module
- Update scraper scripts to use memory bank
- Create `memory_bank_cli.py` for CLI interface

**Steps:**
1. Implement memory_bank.py with MemoryBank class
2. Add methods: register_novel, mark_chapter_downloaded, is_chapter_downloaded, etc.
3. Update scraper to check memory bank before downloading
4. Update scraper to mark chapters as downloaded after success
5. Implement resume logic in main loop
6. Create CLI for managing memory bank
7. Test with a small novel first

**Important notes:**
- See ninestar_scraper_with_memory.py for integration example
- Memory bank data stored in memory_bank.json
- Tracks novel status: downloading, paused, completed, error
- Enables resume from last downloaded chapter
- Prevents duplicate downloads
