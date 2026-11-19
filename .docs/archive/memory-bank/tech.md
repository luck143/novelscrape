# NovelScrape Technical Documentation

## Technologies Used

### Core Technologies

- **Python 3.x**: Primary programming language
- **Selenium WebDriver**: Browser automation for web scraping
- **undetected_chromedriver**: Chrome driver that bypasses bot detection
- **trafilatura**: HTML content extraction library
- **unidecode**: Unicode to ASCII conversion

### EPUB Processing

- **ebooklib**: EPUB file creation and manipulation
- **zipfile**: EPUB file handling (EPUBs are ZIP archives)

### Text Processing

- **re**: Regular expressions for text cleaning and pattern matching
- **os**: File system operations
- **glob**: File pattern matching
- **time**: Timing and delays

### Web Scraping

- **requests**: HTTP requests (imported but not heavily used)
- **json**: JSON data handling (imported but not heavily used)

## Development Setup

### Prerequisites

1. **Python 3.7+**: Required for modern Python features
2. **Google Chrome**: Browser for Selenium WebDriver
3. **ChromeDriver**: WebDriver executable (managed via undetected_chromedriver)

### Installation

```bash
# Install required packages
pip install selenium undetected-chromedriver trafilatura unidecode ebooklib

# Or install all at once
pip install selenium undetected-chromedriver trafilatura unidecode ebooklib webdriver-manager
```

### Project Structure Setup

```bash
# Create project directory
mkdir novelscrape
cd novelscrape

# Create downloads directory
mkdir downloads

# Create webdriver directory
mkdir webdriver

# Download ChromeDriver to webdriver/ directory
# (Optional - undetected_chromedriver can auto-download)
```

## Technical Constraints

### Browser Automation

- **Chrome Version Dependency**: undetected_chromedriver must match Chrome version
- **Manual Version Specification**: Sometimes requires `version_main` parameter
- **Headless Mode**: Can be enabled but may affect anti-bot detection
- **Memory Usage**: Each browser instance consumes significant RAM

### Website Constraints

- **Rate Limiting**: Many sites limit anonymous users (typically 10 chapters)
- **Captcha Challenges**: Advanced captchas require manual intervention
- **Structure Changes**: Scrapers break when websites update their HTML structure
- **Anti-Bot Measures**: Sites may implement new detection methods

### File System

- **Windows Path Handling**: Scripts use backslashes (Windows paths)
- **Encoding Issues**: Some files may require different encodings (utf-8, latin-1)
- **File Naming**: Novel names with special characters may cause issues

## Dependencies

### Required Python Packages

```
selenium>=4.0.0
undetected-chromedriver>=3.0.0
trafilatura>=1.0.0
unidecode>=1.0.0
ebooklib>=0.18
webdriver-manager>=3.0.0
```

### System Dependencies

- **Google Chrome**: Latest stable version recommended
- **ChromeDriver**: Compatible with Chrome version
- **Windows OS**: Scripts are Windows-specific (path handling)

## Tool Usage Patterns

### Chrome Driver Initialization

**Standard Pattern:**
```python
import undetected_chromedriver as uc
from selenium import webdriver

options = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True)
```

**With Version Specification:**
```python
driver = uc.Chrome(use_subprocess=True, version_main=127)
```

**With Headless Mode:**
```python
options = webdriver.ChromeOptions()
options.headless = True
driver = uc.Chrome(use_subprocess=True, options=options)
```

### Wait Conditions

**Wait for Element by Class:**
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "chapter-nav"))
)
```

**Wait for Element by ID:**
```python
wait = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.ID, "read-novel"))
)
```

**No Wait (Time-based):**
```python
import time
time.sleep(1)  # Simple delay
```

### Content Extraction

**Standard Trafilatura Extraction:**
```python
import trafilatura

content = driver.page_source
text = trafilatura.extract(content)
```

**With Unicode Normalization:**
```python
from unidecode import unidecode

text = trafilatura.extract(content)
normalized_text = unidecode(text)
```

### Captcha Detection

**Common Patterns:**
```python
if 'You need to enable JavaScript to run this app' in text:
    print("Captcha Found")
    time.sleep(30)
    sys.exit("Stopped")
elif 'Anonymous users can read up to 10 chapters' in text:
    print("Limit Reached")
    sys.exit("Stopped")
```

### File Operations

**Save Chapter to File:**
```python
import os

novelname = 'ninestar'
chapter_num = 5000
os.makedirs(f'downloads/{novelname}', exist_ok=True)

filename = f"{chapter_num}.txt"
file_path = f'downloads/{novelname}/{filename}'

with open(file_path, 'w', encoding='utf-8') as file:
    file.write(text)
```

**Combine Multiple Files:**
```python
import glob
import os

path = os.getcwd() + '\\downloads\\ninestar\\'
files = list(filter(os.path.isfile, glob.glob(path + "*.txt")))
files.sort(key=lambda x: os.path.getmtime(x))

with open('output.txt', 'w') as outfile:
    for fname in files:
        with open(fname, 'r') as readfile:
            outfile.write(readfile.read() + "\n\n")
```

### Text Cleaning

**Remove Dots Between Letters:**
```python
import re

pattern = r'([a-zA-Z])\.([a-zA-Z])'
cleaned = re.sub(pattern, r'\1\2', text)

# Handle multiple dots
pattern_multiple = r'([a-zA-Z])\.+([a-zA-Z])'
cleaned = re.sub(pattern_multiple, r'\1\2', cleaned)
```

**Remove .+ Patterns:**
```python
pattern_dot_plus = r'\.\+'
cleaned = re.sub(pattern_dot_plus, '', text)
```

### EPUB Creation

**Basic EPUB Creation:**
```python
from ebooklib import epub

book = epub.EpubBook()
book.set_title("Novel Title")

# Create chapter
chapter = epub.EpubHtml(title="Chapter 1", file_name='chap_1.xhtml', lang='en')
chapter.content = '<html><body><h1>Chapter 1</h1><p>Content</p></body></html>'

book.add_item(chapter)
book.toc = (chapter,)
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
book.spine = ['nav', chapter]

epub.write_epub('output.epub', book, {})
```

## Configuration Patterns

### Scraper Configuration

Each scraper typically has:
- Novel name (hardcoded)
- Chapter range (start, end)
- Base URL pattern
- Wait condition selector
- Chrome driver options

### Environment Variables

Currently not used, but could be implemented for:
- Novel names
- Chapter ranges
- Download paths
- Chrome version

## Debugging Techniques

### Common Issues

**Chrome Version Mismatch:**
```python
# Solution: Specify version explicitly
driver = uc.Chrome(use_subprocess=True, version_main=127)
```

**Timeout Errors:**
```python
# Solution: Increase timeout or check wait condition
wait = WebDriverWait(driver, 60).until(...)
```

**Empty Content:**
```python
# Solution: Check if trafilatura extracted anything
text = trafilatura.extract(content)
if not text:
    print("No content extracted")
    # Handle error
```

**File Encoding Issues:**
```python
# Solution: Try different encodings
try:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
except UnicodeDecodeError:
    with open(file, 'r', encoding='latin-1') as f:
        content = f.read()
```

## Performance Optimization

### Scraping Optimization

- **Reduce Delays**: Minimize `time.sleep()` calls
- **Optimize Waits**: Use precise wait conditions instead of long delays
- **Batch Processing**: Process chapters in batches (not currently implemented)
- **Parallel Downloads**: Could use threading (NUM_THREADS defined but not used)

### File I/O Optimization

- **Buffer Writing**: Write larger chunks to disk
- **Compression**: Compress large files (not currently implemented)
- **Incremental Processing**: Process files as they're downloaded

## Error Handling Patterns

### Try-Except Blocks

```python
try:
    # Scraping operation
    driver.get(url)
    text = trafilatura.extract(driver.page_source)
except Exception as e:
    print(f"Error: {e}")
    # Handle error
finally:
    driver.quit()
```

### Retry Logic

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        # Operation
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        time.sleep(5)
```

## Security Best Practices

### Rate Limiting

- Add delays between requests
- Respect website terms of service
- Don't overwhelm servers

### Data Privacy

- Don't store user credentials
- Use environment variables for sensitive data
- Clean up temporary files

### Legal Compliance

- Respect copyright and terms of service
- Use scraped content for personal use only
- Don't redistribute scraped content without permission
