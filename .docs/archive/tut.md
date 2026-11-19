# Development Tutorial & Quick Reference

## Python Environment Setup

### Virtual Environment Creation

```bash
# Using Python 3.8
py -3.8

# Using Python 3.12
py -3.12

# Create virtual environment with Python 3.12
py -3.12 -m venv venv

# Or with default Python
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

### Package Installation

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install undetected_chromedriver
pip install trafilatura
pip install unidecode
pip install ebooklib
pip install docopt
```

## Chrome Browser Configuration

### Remote Debugging Mode

```bash
# Open Chrome with remote debugging on port 9222
chrome.exe --remote-debugging-port=9222

# Open Chrome with remote debugging and custom profile
chrome.exe --remote-debugging-port=9222 --user-data-dir="path/to/chromeprofile"
```

### Chrome Version Compatibility

If you encounter Chrome driver version issues, specify the Chrome version explicitly:

```python
import undetected_chromedriver as uc

# Specify Chrome version (e.g., version 119)
driver = uc.Chrome(version_main=119)

# Or let undetected_chromedriver auto-detect
driver = uc.Chrome(use_subprocess=True)
```

## Useful Resources

- [SeleniumBase UC Mode Documentation](https://github.com/seleniumbase/SeleniumBase/blob/master/help_docs/uc_mode.md)
- [undetected-chromedriver GitHub](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

## Clean Installation

### Uninstall All Packages

If you need to start fresh with a clean Python environment:

```bash
# List all installed packages
pip freeze > requirements.txt

# Uninstall all packages
pip uninstall -r requirements.txt -y

# Delete requirements.txt
del requirements.txt
```

## Testing

### Quick Mode Testing

Test both `unified_combiner.py` and `unified_scraper.py` in quick mode:

**Test Case:**
- Novel: Nine Star Hegemon's Body Arts
- Website: empirenovel.com
- Novel slug: nine-star-hegemon-body-arts

**Steps:**
1. Run `unified_scraper.py` with empirenovel.com
2. Download a small chapter range (e.g., 1-5)
3. Run `unified_combiner.py` to combine chapters
4. Verify output files are created correctly

## Troubleshooting

### Common Issues

**Chrome Version Mismatch:**
- Check Chrome version: `chrome://version/`
- Update `version_main` parameter to match

**Import Errors:**
- Ensure virtual environment is activated
- Verify all packages are installed

**Permission Errors:**
- Run terminal as Administrator (Windows)
- Check file permissions on downloads directory

**Captcha Detection:**
- Wait and retry after some time
- Check if website has rate limiting

## Notes

- This project uses Selenium WebDriver with undetected_chromedriver for anti-bot detection
- Trafilatura is used for clean text extraction from HTML
- Unidecode converts Unicode characters to ASCII for compatibility
- Chrome profiles are stored locally for session persistence
- Always test with a small chapter range before bulk downloads
