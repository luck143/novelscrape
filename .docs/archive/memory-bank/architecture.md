# NovelScrape Architecture

## System Architecture

NovelScrape follows a modular architecture with three main layers:

1. **Scraping Layer**: Individual scraper scripts for each novel hosting website
2. **Processing Layer**: Combine, clean, and publish utilities
3. **Tracking Layer**: Memory bank system for progress tracking (partially implemented)

## Source Code Organization

### Root Directory Structure

```
novelscrape/
├── unified_scraper.py             # Unified CLI scraper for all websites
├── unified_combiner.py            # Unified CLI combiner for TXT and EPUB creation with text cleaning
├── scraper_configs.json            # Website configurations
├── 2_publish_epub.py              # EPUB publishing (version 1)
├── 2_publish_epub2.py             # EPUB publishing (version 2)
├── clean_epub_file.py             # EPUB cleaning utility
├── ninestar_scraper_with_memory.py # Memory bank integration example
├── README_MEMORY_BANK.md          # Memory bank documentation
├── README_UNIFIED_COMBINER.md     # Unified combiner documentation
├── downloads/                    # Downloaded chapters (gitignored)
├── webdriver/                     # Chrome driver executables
└── wanderinginn/                  # Specialized scripts for Wandering Inn
```

### Scraper Scripts Pattern

Each scraper follows a consistent pattern:

**Common Imports:**
```python
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import trafilatura
from unidecode import unidecode
```

**Common Components:**
1. Chrome driver initialization with undetected_chromedriver
2. `scrape_data()` function to download individual chapters
3. Captcha detection and handling
4. File saving to `downloads/{novelname}/` directory
5. Loop through chapter range with URL construction

**Website-Specific Variations:**
- Different wait conditions (By.CLASS_NAME, By.ID)
- Different URL patterns
- Some use next-link navigation (novelbin.py, novelfull2.py, novlove.py)
- Some have retry logic (wuxiascrape2.py)

### Supported Websites

The [`unified_scraper.py`](unified_scraper.py) provides a unified CLI interface for all supported websites using [`scraper_configs.json`](scraper_configs.json) for configuration.

**Supported Websites (12 total):**
- boxnovel.com
- novelfull.com
- empirenovel.com
- lightnovelworld.co
- novelbin.com
- novelontop.com
- novlove.com
- readlightnovel.meme
- wuxiaworld.com
- wuxiaz.com
- novelhi.com
- freewebnovel.com

**Note**: Individual scraper scripts have been removed in favor of the unified scraper. All website configurations are now managed in [`scraper_configs.json`](scraper_configs.json).

## Key Technical Decisions

### Anti-Bot Detection

- **undetected_chromedriver**: Primary tool for bypassing basic bot detection
- **Chrome Options**: Various options to avoid detection flags
- **Version Management**: Manual version specification when needed (version_main parameter)

### Content Extraction

- **trafilatura**: Used for clean text extraction from HTML
- **unidecode**: Converts Unicode characters to ASCII for compatibility

### Captcha Detection

Common patterns checked:
- "You need to enable JavaScript to run this app"
- "Anonymous users can read up to 10 chapters"

### File Organization

- **Individual Chapters**: `downloads/{novelname}/{chapter_num}.txt`
- **Combined Files**: `downloads/{novelname}_{timestamp}.txt`
- **Cleaned Files**: `downloads/{filename}_cleaned.txt`
- **EPUB Files**: `{novelname}.epub`

## Design Patterns

### Scraper Pattern

All scrapers follow a consistent pattern:
1. Initialize Chrome driver
2. Define `scrape_data()` function
3. Loop through chapter range
4. Navigate to URL, wait for page load
5. Extract content with trafilatura
6. Check for captcha/limits
7. Save to file
8. Close driver

### Memory Bank Pattern (Planned)

The memory bank integration follows this pattern:
1. Register novel with metadata
2. Check if chapter already downloaded
3. Mark chapter as downloaded after success
4. Track novel status (downloading, paused, completed, error)
5. Resume from last downloaded chapter

## Component Relationships

```
Scraper Scripts
    ↓
Downloads (individual chapter files)
    ↓
Combine Scripts
    ↓
Combined TXT Files
    ↓
Clean Scripts (optional)
    ↓
EPUB Publishing Scripts
    ↓
EPUB Files
```

## Critical Implementation Paths

### Scraping Flow

1. **Driver Initialization**: `uc.Chrome(use_subprocess=True)` or `uc.Chrome(version_main=X)`
2. **Page Navigation**: `driver.get(url)`
3. **Wait Condition**: `WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.*, selector)))`
4. **Content Extraction**: `trafilatura.extract(driver.page_source)`
5. **Captcha Check**: Check for known captcha patterns in extracted text
6. **File Save**: Write to `downloads/{novelname}/{chapter_num}.txt`

### Combining Flow

**Using unified_combiner.py:**
1. **File Collection**: Use `glob.glob()` to find all TXT files in novel directory
2. **Sorting**: Sort by modification time (TXT) or natural sort (EPUB) to maintain order
3. **Merging**: Read each file and append to output with configurable chapter markers
4. **Cleaning**: Optionally clean text content (remove dots between letters, .+ patterns)
5. **Output**: Create timestamped combined file or EPUB

### EPUB Publishing Flow

**Option 1: From individual TXT files (unified_combiner.py)**
1. **File Collection**: Use `glob.glob()` to find all TXT files in novel directory
2. **Natural Sorting**: Sort files numerically (1.txt, 2.txt, 10.txt)
3. **EPUB Creation**: Create EpubBook instance
4. **Chapter Creation**: Create EpubHtml for each TXT file
5. **TOC Generation**: Generate table of contents
6. **File Writing**: Write EPUB file with epub.write_epub()

**Option 2: From combined TXT file (2_publish_epub.py, 2_publish_epub2.py)**
1. **Text Reading**: Read combined TXT file
2. **Chapter Splitting**: Use regex to split on chapter markers
3. **EPUB Creation**: Create EpubBook instance
4. **Chapter Creation**: Create EpubHtml for each chapter
5. **TOC Generation**: Generate table of contents
6. **File Writing**: Write EPUB file with epub.write_epub()

## Data Flow

```
Website URL
    → Selenium WebDriver
    → trafilatura extraction
    → Unidecode normalization
    → Individual TXT files
    → Combine script
    → Combined TXT file
    → Clean script (optional)
    → EPUB publisher
    → EPUB file
```

## Extension Points

### Adding New Website Support

1. Create new scraper file following existing pattern
2. Determine URL pattern for the website
3. Find appropriate wait condition (element to wait for)
4. Test with a few chapters before bulk download
5. Add to supported websites list

### Memory Bank Integration

1. Import memory_bank module
2. Register novel before scraping
3. Check `memory_bank.is_chapter_downloaded()` before download
4. Call `memory_bank.mark_chapter_downloaded()` after success
5. Update novel status appropriately
6. Handle resume logic in main loop

## Performance Considerations

- **Single-threaded**: Most scrapers use sequential downloads
- **Rate Limiting**: Some sites have limits (e.g., 10 chapters for anonymous users)
- **Timeout Management**: Wait conditions prevent indefinite hangs
- **Retry Logic**: Some scrapers implement retry on failure (wuxiascrape2.py)
- **Memory Usage**: Trafilatura processes HTML in memory

## Error Handling

- **TimeoutException**: Page load timeout handling
- **Captcha Detection**: Stop scraping when detected
- **Rate Limiting**: Detect and stop when limit reached
- **File I/O**: Basic error handling for file operations
- **Driver Cleanup**: Always call `driver.quit()` in finally block

## Security Considerations

- **Anti-Bot Measures**: undetected_chromedriver helps bypass detection
- **Rate Limiting**: Respect website limits to avoid IP blocking
- **User Data**: Chrome profiles stored locally (chromeprofile/)
- **Legal**: Users must respect copyright and terms of service
