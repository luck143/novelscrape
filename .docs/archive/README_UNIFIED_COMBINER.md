# Unified File Combiner

A unified tool for combining individual chapter TXT files into a single TXT file or creating EPUB files directly. This tool replaces the multiple combiner scripts with a single, flexible solution.

**Note**: The unified combiner is [`combiner.py`](../combiner.py).

## Features

- **Combine TXT files**: Merge individual chapter files into a single TXT document
- **Create EPUB files**: Convert chapter TXT files directly into EPUB format
- **Text cleaning**: Remove formatting artifacts like dots between letters and .+ patterns
- **Multiple chapter marker formats**: Choose between full markers, simple markers, or no markers
- **Interactive and CLI modes**: Use interactively or via command-line arguments
- **Natural file sorting**: Properly sorts files numerically (e.g., chapter1, chapter2, chapter10)
- **Encoding support**: Handles UTF-8 and fallback to windows-1252 encoding

## Installation

No additional installation required. The unified combiner uses the same dependencies as the rest of NovelScrape:

```bash
pip install ebooklib
```

## Usage

### Interactive Mode

Run the script without any arguments to enter interactive mode:

```bash
python combiner.py
```

You'll be prompted to:
1. Choose operation (Combine TXT or Create EPUB)
2. Enter novel name or path to chapter files
3. Select chapter marker format (for TXT combining)
4. Choose whether to clean text content (removes dots between letters, .+ patterns)
5. Enter output filename (optional, auto-generated if not provided)
6. Enter EPUB title and author (for EPUB creation)

### Command-Line Mode

#### Combine TXT Files

Basic usage:
```bash
python combiner.py --combine --input downloads/novelname
```

With custom output:
```bash
python combiner.py --combine --input downloads/novelname --output downloads/combined.txt
```

With different chapter marker formats:
```bash
# Full markers: #Chapter 1 : 1
python combiner.py --combine --input downloads/novelname --marker full

# Simple markers: #
python combiner.py --combine --input downloads/novelname --marker simple

# No markers
python combiner.py --combine --input downloads/novelname --marker none
```

With text cleaning (removes dots between letters, .+ patterns):
```bash
python combiner.py --combine --input downloads/novelname --clean
```

Quiet mode (suppress progress output):
```bash
python combiner.py --combine --input downloads/novelname --quiet
```

#### Create EPUB Files

Basic usage:
```bash
python combiner.py --epub --input downloads/novelname
```

With custom metadata:
```bash
python combiner.py --epub --input downloads/novelname --output novel.epub --title "My Novel" --author "Author Name"
```

With text cleaning (removes dots between letters, .+ patterns):
```bash
python combiner.py --epub --input downloads/novelname --clean
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--combine` | Combine TXT files into a single TXT file |
| `--epub` | Create EPUB from TXT files |
| `--input INPUT` | Input directory containing chapter TXT files |
| `--output OUTPUT` | Output file path (TXT or EPUB) |
| `--marker {full,simple,none}` | Chapter marker format for TXT combining (default: full) |
| `--title TITLE` | EPUB title (default: Untitled) |
| `--author AUTHOR` | EPUB author (default: Unknown) |
| `--clean` | Clean text content (removes dots between letters, .+ patterns) |
| `--quiet` | Suppress progress output |

## Chapter Marker Formats

### Full Format
```
#Chapter 1 : 1
[chapter content]

#Chapter 2 : 2
[chapter content]
```

### Simple Format
```
#[chapter content]

#[chapter content]
```

### No Markers
```
[chapter content]

[chapter content]
```

## File Sorting

The unified combiner uses two sorting methods:

1. **Modification Time (default for TXT combining)**: Sorts files by when they were created/modified
2. **Natural Sort (used for EPUB creation)**: Sorts files numerically and alphabetically (e.g., `1.txt`, `2.txt`, `10.txt` instead of `1.txt`, `10.txt`, `2.txt`)

## Migration from Old Scripts

### From `combine.py` or `1_combine2.py`

**Old way:**
```bash
# Edit the script to set path and output filename
python combine.py
```

**New way:**
```bash
python combiner.py --combine --input downloads/novelname --marker full
# or for simple markers (like combine.py)
python combiner.py --combine --input downloads/novelname --marker simple
```

### From `combine_epub.py`

**Old way:**
```bash
# Edit the script to set folder_path, epub_file, title, and author
python combine_epub.py
```

**New way:**
```bash
python combiner.py --epub --input downloads/novelname --output novel.epub --title "Title" --author "Author"
```

### From `wanderinginn/combine.py`

**Old way:**
```bash
# Edit the script to set path
cd wanderinginn
python combine.py
```

**New way:**
```bash
python combiner.py --combine --input downloads/wandering_inn --marker full
```

**New way (with cleaning):**
```bash
python combiner.py --combine --input downloads/novelname --clean
# or for EPUB
python combiner.py --epub --input downloads/novelname --clean
```

**Note**: For additional text cleaning (e.g., removing 'Comments' sections), use `clean_scraped_files.py`.

## Examples

### Example 1: Combine a novel with full chapter markers
```bash
python combiner.py --combine --input downloads/i-became-the-pope-now-what --output downloads/pope_combined.txt --marker full
```

### Example 2: Create EPUB with custom metadata
```bash
python combiner.py --epub --input downloads/ninestar --output downloads/ninestar.epub --title "Nine Star Hegemon" --author "Mad Snail"
```

### Example 3: Clean text while combining
```bash
# Combine with cleaning
python combiner.py --combine --input downloads/novelname --clean

# Create EPUB with cleaning
python combiner.py --epub --input downloads/novelname --clean
```

### Example 4: Quick combine with auto-generated filename
```bash
python combiner.py --combine --input downloads/novelname
# Output: downloads/novelname_1234567890.txt
```

### Example 5: Quiet mode for scripts
```bash
python combiner.py --combine --input downloads/novelname --quiet
```

## Text Cleaning

The `--clean` option removes common formatting artifacts from scraped text:

**What it removes:**
- Dots between letters (e.g., `f.u.c.k` → `fuck`, `T.h.e. y.o.u.n.g.` → `The young.`)
- Multiple dots between letters (e.g., `a..b` → `ab`, `a...b` → `ab`)
- `.+` patterns that may appear in scraped content

**What it preserves:**
- Legitimate punctuation (periods at sentence endings, etc.)
- Normal spacing and formatting
- All other text content

**When to use:**
- When scraped content contains anti-bot obfuscation patterns
- When text has dots inserted between letters to evade detection
- When `.+` patterns appear in the content

**Example:**
```bash
# Without cleaning: "The. y.o.u.n.g. hero.+. fought bravely."
# With cleaning: "The. young. hero fought bravely."
```

## Output Locations

- **Combined TXT files**: Saved to `downloads/` directory by default
- **EPUB files**: Saved to `downloads/` directory by default
- **Timestamps**: Auto-generated filenames include Unix timestamp for uniqueness

## Error Handling

The unified combiner handles:
- Missing input directories
- No TXT files found
- Encoding issues (UTF-8 fallback to windows-1252)
- Invalid command-line arguments

## Notes

- The unified combiner preserves the original chapter content exactly as it appears in the source files (unless `--clean` is used)
- UTF-8 encoding is used by default with automatic fallback for files that don't support it
- EPUB files include proper table of contents and navigation
- Chapter titles in EPUB are derived from the TXT filenames
- Text cleaning is applied to each chapter individually before combining or EPUB creation

## Comparison with Old Scripts

The old scripts have been deleted. All functionality is now in [`combiner.py`](../combiner.py):

| Feature | Old Scripts | Unified Combiner |
|---------|-------------|------------------|
| TXT combining | 3 separate scripts (deleted) | Single script (`combiner.py`) |
| EPUB creation | 1 separate script (deleted) | Integrated |
| Text cleaning | Separate script (deleted) | Integrated with --clean flag |
| CLI interface | None (hardcoded paths) | Full CLI support |
| Interactive mode | None | Yes |
| Chapter markers | Fixed per script | Configurable |
| File sorting | MTime only | MTime + Natural |
| Encoding handling | Basic | UTF-8 + fallback |
| Auto-generated filenames | Timestamp only | Timestamp + configurable |

## Troubleshooting

### "No TXT files found"
- Check that the input path is correct
- Ensure the directory contains `.txt` files
- Verify you have read permissions for the directory

### "UTF-8 decoding failed"
- The script automatically tries windows-1252 encoding
- This is normal for some scraped content
- The conversion will continue successfully

### Files in wrong order
- For TXT combining: Files are sorted by modification time (when they were downloaded)
- For EPUB creation: Files are sorted naturally (numerically)
- Use `--marker full` to verify chapter numbers in the output

## Integration with NovelScrape Workflow

The unified combiner fits seamlessly into the NovelScrape workflow:

1. **Scrape**: Use [`scraper.py`](../scraper.py) to download chapters
2. **Combine & Clean**: Use [`combiner.py`](../combiner.py) to merge chapters with optional cleaning
3. **Additional Cleaning**: Use [`clean_scraped_files.py`](../clean_scraped_files.py) to remove 'Comments' sections
4. **Publish**: Use [`combiner.py`](../combiner.py) with `--epub` flag

## Future Enhancements

Potential improvements for the unified combiner:
- Support for combining from multiple directories
- Batch processing multiple novels
- Progress bar for large operations
- Custom chapter title extraction patterns
- Support for additional output formats (PDF, DOCX)
