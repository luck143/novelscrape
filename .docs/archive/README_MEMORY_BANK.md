# Novel Scraping Memory Bank

This document explains the Memory Bank system for the novel scraping project. The Memory Bank tracks and manages scraped novel data, progress, and metadata, providing functionality to resume interrupted scraping and avoid duplicates.

## Overview

The Memory Bank system consists of three main components:

1. **backups/memory_bank.py** - Core module with the MemoryBank class
2. **backups/memory_bank_cli.py** - Command-line interface for managing the memory bank
3. **Integration scripts** - Modified scraping scripts that use the memory bank (e.g., `ninestar_scraper_with_memory.py`)

## Features

- Track novel metadata and download progress
- Resume interrupted scraping from the last downloaded chapter
- Prevent duplicate downloads
- Command-line interface for easy management
- Export/import functionality for backup and sharing

## Quick Start

### 1. Initialize the Memory Bank

The memory bank is automatically initialized when you first use it. A `memory_bank.json` file will be created in your project directory.

### 2. Register a Novel

```bash
python backups/memory_bank_cli.py register ninestar --url "https://www.empirenovel.com/novel/nine-star-hegemon-body-arts/" --total-chapters 5156
```

### 3. Use the Enhanced Scraper

```bash
python ninestar_scraper_with_memory.py
```

The scraper will automatically:
- Register the novel if not already registered
- Check for already downloaded chapters
- Resume from the last downloaded chapter
- Mark each chapter as downloaded in the memory bank

### 4. Combine Files with Memory Bank Integration

```bash
python backups/combine_with_memory.py ninestar
```

This will combine all chapter files and register the combined file in the memory bank.

## Command Line Interface

The `backups/memory_bank_cli.py` provides various commands to manage your novel collection:

### List All Novels

```bash
python backups/memory_bank_cli.py list
```

### Show Novel Information

```bash
python backups/memory_bank_cli.py info ninestar
python backups/memory_bank_cli.py info ninestar --chapters  # Show chapter list
```

### Get Next Chapter to Download

```bash
python backups/memory_bank_cli.py next ninestar
```

### Check if a Chapter is Downloaded

```bash
python backups/memory_bank_cli.py check ninestar 5001
```

### Mark a Chapter as Downloaded

```bash
python backups/memory_bank_cli.py mark ninestar 5001 "downloads/ninestar/5001.txt" --title "Chapter Title"
```

### Set Novel Status

```bash
python backups/memory_bank_cli.py status ninestar completed
```

### Delete a Novel

```bash
python backups/memory_bank_cli.py delete ninestar --force
```

### Export/Import Memory Bank

```bash
# Export
python backups/memory_bank_cli.py export backup.json

# Import (merge with existing data)
python backups/memory_bank_cli.py import backup.json

# Import (replace existing data)
python backups/memory_bank_cli.py import backup.json --replace
```

## Integration with Existing Scripts

### ninestar_scraper_with_memory.py

This is a modified version of your scraper that integrates with the memory bank:

- Automatically registers the novel if not already registered
- Checks for already downloaded chapters to avoid duplicates
- Resumes from the last downloaded chapter if interrupted
- Updates the memory bank with each downloaded chapter

Usage:
```bash
# Use default range
python ninestar_scraper_with_memory.py

# Use custom range
python ninestar_scraper_with_memory.py 5000 5100
```

### backups/combine_with_memory.py

This is a modified version of your combine script that integrates with the memory bank:

- Combines chapter files into a single file
- Registers the combined file in the memory bank metadata
- Can auto-detect the most recently modified novel directory

Usage:
```bash
# Auto-detect most recent novel
python backups/combine_with_memory.py

# Specify novel name
python backups/combine_with_memory.py ninestar
```

## Memory Bank Data Structure

The memory bank stores data in `memory_bank.json` with the following structure:

```json
{
  "novels": {
    "novel_name": {
      "name": "novel_name",
      "source_url": "https://...",
      "total_chapters": 5156,
      "downloaded_chapters": {
        "5000": {
          "chapter_number": 5000,
          "file_path": "downloads/novel_name/5000.txt",
          "title": "Chapter Title",
          "downloaded_at": "2023-01-01T12:00:00"
        }
      },
      "last_chapter_downloaded": 5000,
      "status": "downloading",
      "created_at": "2023-01-01T10:00:00",
      "metadata": {
        "title": "Novel Title",
        "author": "Author Name",
        "combined_files": [
          {
            "file_path": "downloads/novel_name_combined_1234567890.txt",
            "created_at": "2023-01-01 15:00:00",
            "chapters_count": 100
          }
        ]
      }
    }
  },
  "last_updated": "2023-01-01T12:00:00",
  "version": "1.0"
}
```

## Novel Status Values

- `registered` - Novel has been registered but no chapters downloaded
- `downloading` - Currently downloading chapters
- `paused` - Downloading was paused or interrupted
- `completed` - All chapters have been downloaded
- `error` - An error occurred during downloading

## Best Practices

1. **Always use the enhanced scrapers** when possible to maintain accurate memory bank data
2. **Check the memory bank status** before starting a new scraping session
3. **Export your memory bank regularly** for backup purposes
4. **Use the CLI** (`backups/memory_bank_cli.py`) to manage your novel collection and check progress
5. **Combine files after completing downloads** to create final versions

## Troubleshooting

### Memory Bank File Not Found

If `memory_bank.json` is missing, it will be automatically created when you first use the memory bank.

### Inconsistent Data

If the memory bank data becomes inconsistent, you can:
1. Export the current data as a backup
2. Delete the `memory_bank.json` file
3. Re-register your novels
4. Import your backup data if needed

### Scraper Not Resuming

If the scraper doesn't resume from the expected chapter:
1. Check the novel status with `python memory_bank_cli.py info novel_name`
2. Verify the last chapter downloaded
3. Make sure the file paths in the memory bank match the actual files

## Integration with Existing Workflow

The memory bank is designed to integrate seamlessly with your existing workflow:

1. Use the enhanced scrapers for new downloads
2. Continue using your existing combine and publish scripts
3. Use the CLI to track progress and manage your collection
4. Export the memory bank for backup or sharing

The memory bank doesn't interfere with your existing files or scripts - it just adds a tracking layer on top.