# NovelScrape Product Description

## Why This Project Exists

NovelScrape addresses a common problem for avid readers: the inability to download and read novel chapters offline from various web novel hosting platforms. Many websites don't provide official download options, and reading online can be inconvenient due to internet connectivity issues, ads, or website restrictions.

## Problems It Solves

1. **Offline Reading**: Users can download entire novels or chapter ranges for offline reading on any device
2. **Format Compatibility**: Converts web content to standard formats (TXT, EPUB) compatible with e-readers and reading apps
3. **Progress Tracking**: Resumes interrupted downloads without losing progress or re-downloading completed chapters
4. **Content Quality**: Cleans scraped text to remove formatting issues and unwanted patterns
5. **Multi-Source Support**: Works across multiple novel hosting platforms, providing flexibility in source selection
6. **Anti-Bot Detection**: Bypasses basic anti-scraping measures using undetected Chrome driver

## How It Works

### Scraping Process

1. **Initialization**: Chrome driver is launched using undetected_chromedriver to avoid detection
2. **Page Navigation**: For each chapter, the scraper navigates to the chapter URL
3. **Content Extraction**: Uses trafilatura library to extract clean text from HTML
4. **Captcha Detection**: Checks for common captcha patterns and stops if detected
5. **File Saving**: Saves extracted text to individual chapter TXT files in a novel-specific directory
6. **Progress Tracking**: (When memory bank is implemented) Tracks downloaded chapters to enable resume functionality

### Post-Processing

1. **Combining**: Individual chapter files are combined into a single TXT file with chapter markers
2. **Text Cleaning**: Removes unwanted patterns like dots between letters (e.g., f.u.c.k → fuck) and .+ patterns
3. **EPUB Publishing**: Converts combined TXT files into EPUB format with proper chapter structure and navigation

### Memory Bank Integration (Planned)

The memory bank system is designed to:
- Register novels with metadata (title, source URL, total chapters)
- Track which chapters have been downloaded
- Enable resume from last downloaded chapter
- Prevent duplicate downloads
- Provide CLI for managing novel collection

## User Experience Goals

### Primary User Workflow

1. **Select Novel**: Choose a novel and source website
2. **Configure Range**: Set chapter range to download (start and end chapters)
3. **Run Scraper**: Execute the appropriate scraper script
4. **Monitor Progress**: Watch as chapters are downloaded
5. **Handle Interruptions**: If interrupted, resume from last downloaded chapter
6. **Combine Chapters**: Merge individual files into a single document
7. **Clean Content**: Remove formatting issues from combined text
8. **Publish EPUB**: Create EPUB file for e-reader compatibility

### Success Criteria

- **Reliability**: Downloads complete successfully without data loss
- **Efficiency**: Resumes quickly without re-downloading completed chapters
- **Quality**: Output text is clean and readable
- **Usability**: Simple command-line interface with clear progress feedback
- **Flexibility**: Works across multiple novel hosting platforms

## Target Users

- **Novel Enthusiasts**: Readers who want to build personal offline libraries
- **E-reader Owners**: Users who prefer reading on dedicated devices
- **Researchers**: People studying web novel content or trends
- **Archivists**: Individuals preserving web content for personal use

## Use Cases

1. **Bulk Download**: Download entire novels (1000+ chapters) in one session
2. **Selective Download**: Download specific chapter ranges
3. **Resume Download**: Continue interrupted downloads from last checkpoint
4. **Format Conversion**: Convert web content to EPUB for Kindle or other e-readers
5. **Content Cleaning**: Remove formatting issues from scraped text
6. **Multi-Source Download**: Download same novel from different sources for comparison

## Limitations and Considerations

- **Website Changes**: Scrapers may break if websites change their structure
- **Captcha Challenges**: Advanced captchas may require manual intervention
- **Rate Limiting**: Some sites limit anonymous users (e.g., 10 chapters)
- **Legal Considerations**: Users should respect copyright and terms of service
- **Maintenance**: Requires updates when websites change or Chrome versions update
