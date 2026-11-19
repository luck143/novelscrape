# Quick Mode Usage Guide

## Overview

Both `scraper.py` and `combiner.py` now support **Quick Mode**, which allows you to configure all parameters directly in the files instead of entering them interactively each time.

## How to Use Quick Mode

### Step 1: Enable Quick Mode

Open either file and set `QUICK_MODE = True` at the top of the file (it's already enabled by default).

### Step 2: Configure Parameters

Edit the configuration variables at the top of the file with your desired values.

---

## scraper.py Configuration

```python
QUICK_MODE = True  # Set to False to use interactive mode

# Website configuration
website = 'boxnovel.com'  # Must match a key in scraper_configs.json

# Novel configuration
novel_name = 'my_novel'  # Name for saving files (directory name)
novel_slug = 'my-novel-slug'  # Slug from URL

# Chapter range
start_chapter = 1  # Starting chapter number
end_chapter = 10  # Ending chapter number
```

### Example Configuration

```python
QUICK_MODE = True
website = 'boxnovel.com'
novel_name = 'shadow_slave'
novel_slug = 'shadow-slave'
start_chapter = 1
end_chapter = 100
```

### How to Find the Novel Slug

1. Navigate to the novel's page on the website
2. Look at the URL structure
3. Extract the slug (the part after the domain)

Example:
- URL: `https://boxnovel.com/novel/shadow-slave/chapter-1/`
- Novel slug: `shadow-slave`

---

## combiner.py Configuration

```python
QUICK_MODE = True  # Set to False to use interactive mode

# Operation type
operation = 'combine'  # Options: 'combine' or 'epub'

# Input path
input_path = 'downloads/novelname'  # Path to chapter files

# Output path (optional)
output_path = ''  # Leave empty for auto-generated filename

# Chapter marker (for TXT combining)
chapter_marker = 'full'  # Options: 'full', 'simple', 'none'

# Clean text
clean_text = False  # Set to True to remove formatting artifacts

# EPUB metadata (for EPUB creation)
epub_title = 'My Novel'
epub_author = 'Author Name'

# Suppress output
quiet = False  # Set to True to suppress progress messages
```

### Example Configuration (Combine to TXT)

```python
QUICK_MODE = True
operation = 'combine'
input_path = 'downloads/shadow_slave'
output_path = 'downloads/shadow_slave_combined.txt'
chapter_marker = 'full'
clean_text = True
```

### Example Configuration (Create EPUB)

```python
QUICK_MODE = True
operation = 'epub'
input_path = 'downloads/shadow_slave'
output_path = 'downloads/shadow_slave.epub'
epub_title = 'Shadow Slave'
epub_author = 'GuiltyThree'
clean_text = True
```

---

## Running the Scripts

### Quick Mode (No Arguments)

```bash
# Run scraper with configured values
python scraper.py

# Run combiner with configured values
python combiner.py
```

### Interactive Mode (No Configuration)

```bash
# Run scraper in interactive mode (set QUICK_MODE = False)
python scraper.py

# Run combiner in interactive mode (set QUICK_MODE = False)
python combiner.py
```

### CLI Mode (Override Configuration)

You can still use CLI arguments to override the configuration:

```bash
# Override scraper configuration
python scraper.py --website novelfull.com --novel "my_novel" --slug "my-novel" --start 1 --end 50

# Override combiner configuration
python combiner.py --combine --input downloads/novelname --output combined.txt --marker full
```

---

## Supported Websites (for unified_scraper.py)

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

---

## Tips

1. **Test First**: Always test with a small chapter range (e.g., 1-5) before running a large download
2. **Save Configurations**: Keep multiple copies of the files with different configurations for different novels
3. **Check Output**: Verify the output files are created correctly before deleting source files
4. **Resume Support**: The scraper automatically skips already downloaded chapters, so you can resume interrupted downloads

---

## Troubleshooting

### Issue: "Unsupported website" error
**Solution**: Make sure the `website` value matches exactly with a key in `scraper_configs.json`

### Issue: "Directory not found" error
**Solution**: Check that `input_path` in unified_combiner.py points to an existing directory

### Issue: Chapters not downloading
**Solution**: 
- Verify the novel slug is correct
- Check if the website structure has changed
- Try with a smaller chapter range first

### Issue: Want to use interactive mode temporarily
**Solution**: Set `QUICK_MODE = False` at the top of the file, or simply provide any CLI argument

---

## Example Workflow

### Download and Combine a Novel

1. **Configure the scraper**:
   ```python
   # In scraper.py
   QUICK_MODE = True
   website = 'boxnovel.com'
   novel_name = 'shadow_slave'
   novel_slug = 'shadow-slave'
   start_chapter = 1
   end_chapter = 100
   ```

2. **Run the scraper**:
   ```bash
   python scraper.py
   ```

3. **Configure the combiner**:
   ```python
   # In combiner.py
   QUICK_MODE = True
   operation = 'combine'
   input_path = 'downloads/shadow_slave'
   output_path = 'downloads/shadow_slave_combined.txt'
   clean_text = True
   ```

4. **Run the combiner**:
   ```bash
   python combiner.py
   ```

5. **Done!** Your combined file is ready at `downloads/shadow_slave_combined.txt`
