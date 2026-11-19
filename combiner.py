#!/usr/bin/env python3
"""
Unified File Combiner for NovelScrape
Combines individual chapter TXT files into a single TXT file or creates EPUB directly.
Supports multiple chapter marker formats and provides a CLI interface.
"""

# ============================================================================
# QUICK MODE CONFIGURATION
# Moved out of source code: create quick_combiner_config.json in the project
# root and it is used automatically when combiner.py runs with no CLI args.
# Keys: operation ('combine'|'epub'), input_path, output_path (optional),
#   chapter_marker ('full'|'simple'|'none'), clean_text (bool),
#   start_chapter / end_chapter (optional), epub_title, epub_author, quiet (bool)
# Delete/rename the file to always get interactive prompts.
# ============================================================================

QUICK_CONFIG_FILE = 'quick_combiner_config.json'

# ============================================================================

import os
import sys
import glob
import time
import json
import re
import argparse

from textutils import clean_text_content as _clean_text_content
from ebooklib import epub


def extract_chapter_title(text_content, filename):
    """
    Extract chapter title from the first or second line of text content.
    
    Args:
        text_content: The full text content of the chapter
        filename: The filename (used as fallback)
        
    Returns:
        A tuple of (display_title, sort_title) where:
        - display_title: The title to show in EPUB (e.g., "Chapter 100: What Do You Mean By That?")
        - sort_title: The title used for sorting (e.g., "Chapter 100")
    """
    lines = text_content.strip().split('\n')
    
    # Check first line for chapter title
    if lines:
        first_line = lines[0].strip()
        # Check if first line looks like a chapter title
        # Patterns: "Chapter X", "Chapter X:", "Chapter X: Title", etc.
        if re.match(r'^Chapter\s+\d+', first_line, re.IGNORECASE):
            # Use the full first line as display title
            display_title = first_line
            # Extract just "Chapter X" for sort title
            match = re.match(r'^(Chapter\s+\d+)', first_line, re.IGNORECASE)
            sort_title = match.group(1) if match else first_line
            return display_title, sort_title
    
    # Check second line if first line didn't match
    if len(lines) > 1:
        second_line = lines[1].strip()
        if re.match(r'^Chapter\s+\d+', second_line, re.IGNORECASE):
            display_title = second_line
            match = re.match(r'^(Chapter\s+\d+)', second_line, re.IGNORECASE)
            sort_title = match.group(1) if match else second_line
            return display_title, sort_title
    
    # Fallback to filename without extension
    fallback = filename.replace('.txt', '')
    return fallback, fallback


def clean_text_content(content):
    """Deprecated wrapper kept for backward compatibility.
    Real implementation lives in textutils.py (single source of truth)."""
    return _clean_text_content(content)


def sort_naturally(files):
    """Sort files naturally, considering both numeric and non-numeric parts of the filename."""
    def try_int(value):
        try:
            return int(value)
        except ValueError:
            return value

    def alphanumeric_key(file_name):
        # Type-tag each part so int/str never compare directly
        # (mixed list comparison raises TypeError in Python 3)
        return [(0, int(c)) if c.isdigit() else (1, c) for c in re.split(r'(\d+)', file_name)]

    return sorted(files, key=alphanumeric_key)


def sort_by_mtime(files):
    """Sort files by modification time."""
    return sorted(files, key=lambda x: os.path.getmtime(x))


def get_txt_files(path, sort_method='mtime', start_chapter=None, end_chapter=None):
    """
    Get all TXT files from a directory, sort them, and optionally filter by chapter range.
    
    Args:
        path: Directory path containing TXT files
        sort_method: 'mtime' or 'natural' sorting method
        start_chapter: Starting chapter number (inclusive), None to start from first
        end_chapter: Ending chapter number (inclusive), None to end at last
    
    Returns:
        List of file paths matching the criteria
    """
    files = list(filter(os.path.isfile, glob.glob(os.path.join(path, "*.txt"))))
    
    if sort_method == 'natural':
        files = sort_naturally([os.path.basename(f) for f in files])
        files = [os.path.join(path, f) for f in files]
    else:  # default: mtime
        files = sort_by_mtime(files)
    
    # Filter by chapter range if specified
    if start_chapter is not None or end_chapter is not None:
        filtered_files = []
        for filepath in files:
            filename = os.path.basename(filepath)
            # Extract chapter number from filename (e.g., "1.txt" -> 1, "chapter-10.txt" -> 10)
            # Try to find the first number in the filename
            match = re.search(r'\d+', filename)
            if match:
                chapter_num = int(match.group())
                
                # Check if chapter is within range
                if start_chapter is not None and chapter_num < start_chapter:
                    continue
                if end_chapter is not None and chapter_num > end_chapter:
                    continue
                
                filtered_files.append(filepath)
        
        files = filtered_files
    
    return files


def combine_to_txt(input_path, output_path, chapter_marker='full', clean=False, verbose=True, start_chapter=None, end_chapter=None):
    """
    Combine TXT files into a single TXT file.
    
    Args:
        input_path: Path to directory containing chapter files
        output_path: Path for output combined file
        chapter_marker: Type of chapter marker ('full', 'simple', 'none')
                        - 'full': "#Chapter {name} : {name}"
                        - 'simple': "#"
                        - 'none': No marker
        clean: Whether to clean the text content (remove dots between letters, .+ patterns)
        verbose: Print progress information
        start_chapter: Starting chapter number (inclusive), None to start from first
        end_chapter: Ending chapter number (inclusive), None to end at last
    """
    if verbose:
        print(f"Reading files from: {input_path}")
        if start_chapter is not None or end_chapter is not None:
            range_str = f" (chapters {start_chapter if start_chapter else 'start'} to {end_chapter if end_chapter else 'end'})"
            print(f"Filtering by chapter range{range_str}")
    
    files = get_txt_files(input_path, sort_method='natural', start_chapter=start_chapter, end_chapter=end_chapter)
    
    if not files:
        print("No TXT files found in the specified directory!")
        return False
    
    if verbose:
        print(f"Found {len(files)} files to combine")
        print(f"Output file: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for fname in files:
            filename = os.path.basename(fname)
            name = filename.rsplit('.', 1)[0]
            
            if verbose:
                print(f"Processing: {filename}")
            
            with open(fname, 'r', encoding='utf-8') as readfile:
                content = readfile.read()
                
                # Clean content if requested
                if clean:
                    content = clean_text_content(content)
                
                # Add chapter marker based on format
                if chapter_marker == 'full':
                    outfile.write(f"#Chapter {name} : {name}\n")
                elif chapter_marker == 'simple':
                    outfile.write("#")
                
                outfile.write(content + "\n\n")
    
    if verbose:
        print(f"\nSuccessfully combined {len(files)} files into {output_path}")
    
    return True


def txt_to_epub(folder_path, epub_file, title="Untitled", author="Unknown", clean=False, verbose=True, start_chapter=None, end_chapter=None):
    """
    Convert TXT files in a folder to an EPUB file.
    
    Args:
        folder_path: Path to directory containing chapter TXT files
        epub_file: Path for output EPUB file
        title: Title of the EPUB
        author: Author of the EPUB
        clean: Whether to clean the text content (remove dots between letters, .+ patterns)
        verbose: Print progress information
        start_chapter: Starting chapter number (inclusive), None to start from first
        end_chapter: Ending chapter number (inclusive), None to end at last
    """
    if verbose:
        print(f"Creating EPUB from: {folder_path}")
        print(f"Output EPUB: {epub_file}")
        if start_chapter is not None or end_chapter is not None:
            range_str = f" (chapters {start_chapter if start_chapter else 'start'} to {end_chapter if end_chapter else 'end'})"
            print(f"Filtering by chapter range{range_str}")
    
    # Create a new eBook object
    book = epub.EpubBook()
    
    # Add metadata for the eBook
    book.add_metadata('DC', 'title', title)
    book.add_metadata('DC', 'creator', author)
    
    # List all txt files — same helper as combine_to_txt so TXT and EPUB
    # always see chapters in the same order (natural sort).
    txt_files = [
        os.path.basename(f)
        for f in get_txt_files(folder_path, sort_method='natural',
                               start_chapter=start_chapter, end_chapter=end_chapter)
    ]
    
    if not txt_files:
        print("No TXT files found in the specified directory!")
        return False
    
    if verbose:
        print(f"Found {len(txt_files)} chapters")
    
    # List to store chapter items
    chapter_items = []
    
    for idx, txt_file in enumerate(txt_files, start=1):
        # Construct the full path to the txt file
        file_path = os.path.join(folder_path, txt_file)
        
        if verbose:
            print(f"Processing chapter {idx}/{len(txt_files)}: {txt_file}")
        
        # Read the chapter content from the file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try reading with a different encoding
            if verbose:
                print(f"UTF-8 decoding failed. Trying 'windows-1252' encoding for {txt_file}...")
            with open(file_path, 'r', encoding='windows-1252') as file:
                text_content = file.read()
        
        # Clean content if requested
        if clean:
            text_content = clean_text_content(text_content)
        
        # Extract chapter title from the text content (first or second line)
        display_title, sort_title = extract_chapter_title(text_content, txt_file)
        
        # Create a new chapter with the extracted title
        chapter_html = epub.EpubHtml(
            title=display_title,
            file_name=f"chapter{idx}.xhtml",
            lang="en"
        )
        
        # Wrap the content in HTML structure
        html_content = """
        <html>
        <head>
            <meta charset="utf-8"/>
            <title>{}</title>
        </head>
        <body>
            <h1>{}</h1>
            <p>{}</p>
        </body>
        </html>
        """.format(display_title, display_title, text_content.replace('\n', '<br/>'))
        
        # Set the content of the chapter
        chapter_html.content = html_content
        
        # Add chapter to the book
        book.add_item(chapter_html)
        chapter_items.append(chapter_html)
    
    # Define the table of contents (TOC)
    book.toc = tuple([epub.Link(chapter.file_name, chapter.title, chapter.title) for chapter in chapter_items])
    
    # Add necessary eBook items
    book.add_item(epub.EpubNav())
    
    # Write the eBook to a file
    epub.write_epub(epub_file, book)
    
    if verbose:
        print(f"\nSuccessfully created EPUB file: {epub_file}")
    
    return True


def interactive_mode():
    """Run the combiner in interactive CLI mode."""
    print("=" * 60)
    print("Unified File Combiner - NovelScrape")
    print("=" * 60)
    
    # Get operation type
    print("\nSelect operation:")
    print("1. Combine TXT files")
    print("2. Create EPUB from TXT files")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '3':
        print("Exiting...")
        sys.exit(0)
    
    if choice not in ['1', '2']:
        print("Invalid choice!")
        sys.exit(1)
    
    # Get novel name/path
    novel_name = input("\nEnter novel name (or full path to chapter files): ").strip()
    
    # Determine input path
    if os.path.isabs(novel_name):
        input_path = novel_name
    else:
        input_path = os.path.join(os.getcwd(), 'downloads', novel_name)
    
    if not os.path.exists(input_path):
        print(f"Error: Directory not found: {input_path}")
        sys.exit(1)
    
    # Ask for chapter range (optional)
    print("\nChapter range (leave blank to include all chapters):")
    start_input = input("  Start chapter number (press Enter to start from first): ").strip()
    start_chapter = int(start_input) if start_input else None
    
    end_input = input("  End chapter number (press Enter to end at last): ").strip()
    end_chapter = int(end_input) if end_input else None
    
    if start_chapter is not None and end_chapter is not None and start_chapter > end_chapter:
        print("Error: Start chapter cannot be greater than end chapter!")
        sys.exit(1)
    
    if choice == '1':
        # TXT combining options
        print("\nChapter marker format:")
        print("1. Full: #Chapter {name} : {name}")
        print("2. Simple: #")
        print("3. None")
        
        marker_choice = input("\nEnter choice (1-3): ").strip()
        
        marker_map = {
            '1': 'full',
            '2': 'simple',
            '3': 'none'
        }
        
        chapter_marker = marker_map.get(marker_choice, 'full')
        
        # Ask about cleaning
        clean_choice = input("\nClean text content? (removes dots between letters, .+ patterns) [y/N]: ").strip().lower()
        clean = clean_choice == 'y' or clean_choice == 'yes'
        
        # Generate output filename
        timestamp = str(int(time.time()))
        output_name = input("\nEnter output filename (press Enter for auto-generated): ").strip()
        
        if not output_name:
            output_name = f"{novel_name}_{timestamp}.txt"
        
        if not output_name.endswith('.txt'):
            output_name += '.txt'
        
        output_path = os.path.join(os.getcwd(), 'downloads', output_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Combine files
        success = combine_to_txt(input_path, output_path, chapter_marker=chapter_marker, clean=clean, start_chapter=start_chapter, end_chapter=end_chapter)
        
        if success:
            print(f"\n✓ Combined files saved to: {output_path}")
        else:
            print("\n✗ Failed to combine files")
            sys.exit(1)
    
    elif choice == '2':
        # EPUB creation options
        title = input("\nEnter EPUB title (press Enter to use novel name): ").strip()
        if not title:
            title = novel_name.replace('-', ' ').replace('_', ' ').title()
        
        author = input("Enter author name (press Enter for 'Unknown'): ").strip()
        if not author:
            author = "Unknown"
        
        # Ask about cleaning
        clean_choice = input("\nClean text content? (removes dots between letters, .+ patterns) [y/N]: ").strip().lower()
        clean = clean_choice == 'y' or clean_choice == 'yes'
        
        # Generate output filename
        output_name = input("\nEnter output EPUB filename (press Enter for auto-generated): ").strip()
        
        if not output_name:
            output_name = f"{novel_name}.epub"
        
        if not output_name.endswith('.epub'):
            output_name += '.epub'
        
        # EPUBs go to downloads/epub/ to keep generated outputs
        # separate from raw chapter directories
        output_path = os.path.join(os.getcwd(), 'downloads', 'epub', output_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create EPUB
        success = txt_to_epub(input_path, output_path, title=title, author=author, clean=clean, start_chapter=start_chapter, end_chapter=end_chapter)
        
        if success:
            print(f"\n✓ EPUB created: {output_path}")
        else:
            print("\n✗ Failed to create EPUB")
            sys.exit(1)


def load_quick_config():
    """Load quick-mode settings from quick_combiner_config.json, or None if absent."""
    if not os.path.exists(QUICK_CONFIG_FILE):
        return None
    try:
        with open(QUICK_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid {QUICK_CONFIG_FILE}: {e}")
        sys.exit(1)


def main():
    """Main entry point for the unified combiner."""
    parser = argparse.ArgumentParser(
        description='Unified File Combiner for NovelScrape - Combine TXT files or create EPUB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (no arguments, no quick_combiner_config.json)
  python combiner.py
  
  # Quick mode (uses quick_combiner_config.json in the project root)
  python combiner.py
  
  # Combine TXT files with full chapter markers
  python combiner.py --combine --input downloads/novelname --output downloads/combined.txt --marker full
  
  # Create EPUB from TXT files (auto-saved to downloads/epub/)
  python combiner.py --epub --input downloads/novelname --title "My Novel" --author "Author Name"
  
  # Combine with simple markers
  python combiner.py --combine --input downloads/novelname --marker simple
  
  # Combine only chapters 1-100
  python combiner.py --combine --input downloads/novelname --start 1 --end 100
  
  # Create EPUB from chapters 50-150
  python combiner.py --epub --input downloads/novelname --start 50 --end 150
  
  # Combine from chapter 100 to end
  python combiner.py --combine --input downloads/novelname --start 100
        """
    )
    
    parser.add_argument(
        '--combine',
        action='store_true',
        help='Combine TXT files into a single TXT file'
    )
    
    parser.add_argument(
        '--epub',
        action='store_true',
        help='Create EPUB from TXT files'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Input directory containing chapter TXT files'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (TXT or EPUB)'
    )
    
    parser.add_argument(
        '--marker',
        type=str,
        choices=['full', 'simple', 'none'],
        default='full',
        help='Chapter marker format for TXT combining (default: full)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean text content (removes dots between letters, .+ patterns)'
    )
    
    parser.add_argument(
        '--title',
        type=str,
        default='Untitled',
        help='EPUB title (default: Untitled)'
    )
    
    parser.add_argument(
        '--author',
        type=str,
        default='Unknown',
        help='EPUB author (default: Unknown)'
    )
    
    parser.add_argument(
        '--start',
        type=int,
        default=None,
        help='Starting chapter number (inclusive)'
    )
    
    parser.add_argument(
        '--end',
        type=int,
        default=None,
        help='Ending chapter number (inclusive)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Check if we should use quick config (no CLI arguments and JSON present)
    quick_cfg = load_quick_config() if len(sys.argv) == 1 else None
    if quick_cfg:
        # Use configuration from quick_combiner_config.json
        operation = quick_cfg.get('operation', 'combine')
        input_path = quick_cfg.get('input_path', '')
        output_path = quick_cfg.get('output_path') or None
        chapter_marker = quick_cfg.get('chapter_marker', 'full')
        clean_text = bool(quick_cfg.get('clean_text', False))
        start_chapter = quick_cfg.get('start_chapter')
        end_chapter = quick_cfg.get('end_chapter')
        epub_title = quick_cfg.get('epub_title', 'Untitled')
        epub_author = quick_cfg.get('epub_author', 'Unknown')
        quiet = bool(quick_cfg.get('quiet', False))

        if not input_path:
            print(f"Error: {QUICK_CONFIG_FILE} must set 'input_path'")
            sys.exit(1)

        print("=" * 60)
        print("Unified File Combiner - Quick Mode")
        print("=" * 60)
        print(f"Using configuration from {QUICK_CONFIG_FILE}:")
        print(f"  Operation: {operation}")
        print(f"  Input: {input_path}")
        print(f"  Output: {output_path if output_path else 'Auto-generated'}")
        print(f"  Marker: {chapter_marker}")
        print(f"  Clean: {clean_text}")
        if start_chapter is not None or end_chapter is not None:
            print(f"  Chapter range: {start_chapter if start_chapter else 'start'} to {end_chapter if end_chapter else 'end'}")
        print("=" * 60 + "\n")
        
        # Set args from configuration
        args.combine = (operation == 'combine')
        args.epub = (operation == 'epub')
        args.input = input_path
        args.output = output_path
        args.marker = chapter_marker
        args.clean = clean_text
        args.start = start_chapter
        args.end = end_chapter
        args.title = epub_title
        args.author = epub_author
        args.quiet = quiet
    elif len(sys.argv) == 1:
        # No arguments and no quick config, run interactive mode
        interactive_mode()
        return
    
    # Validate arguments
    if not args.combine and not args.epub:
        print("Error: Must specify --combine or --epub")
        parser.print_help()
        sys.exit(1)
    
    if args.combine and args.epub:
        print("Error: Cannot use --combine and --epub together")
        sys.exit(1)
    
    if not args.input:
        print("Error: --input is required")
        sys.exit(1)
    
    # Check input directory exists
    if not os.path.exists(args.input):
        print(f"Error: Input directory not found: {args.input}")
        sys.exit(1)
    
    verbose = not args.quiet
    
    # Execute requested operation
    if args.combine:
        # Generate output filename if not provided
        if not args.output:
            timestamp = str(int(time.time()))
            novel_name = os.path.basename(os.path.normpath(args.input))
            args.output = os.path.join(
                os.getcwd(),
                'downloads',
                f"{novel_name}_{timestamp}.txt"
            )
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        
        # Validate chapter range
        if args.start is not None and args.end is not None and args.start > args.end:
            print("Error: Start chapter cannot be greater than end chapter!")
            sys.exit(1)
        
        success = combine_to_txt(
            args.input,
            args.output,
            chapter_marker=args.marker,
            clean=args.clean,
            verbose=verbose,
            start_chapter=args.start,
            end_chapter=args.end
        )
        
        if not success:
            sys.exit(1)
    
    elif args.epub:
        # Generate output filename if not provided;
        # EPUBs go to downloads/epub/ (kept separate from raw chapters)
        if not args.output:
            novel_name = os.path.basename(os.path.normpath(args.input))
            args.output = os.path.join(
                os.getcwd(),
                'downloads', 'epub',
                f"{novel_name}.epub"
            )
        elif not os.path.dirname(args.output):
            # Bare filename given → route into downloads/epub/
            args.output = os.path.join('downloads', 'epub', args.output)
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        
        # Validate chapter range
        if args.start is not None and args.end is not None and args.start > args.end:
            print("Error: Start chapter cannot be greater than end chapter!")
            sys.exit(1)
        
        success = txt_to_epub(
            args.input,
            args.output,
            title=args.title,
            author=args.author,
            clean=args.clean,
            verbose=verbose,
            start_chapter=args.start,
            end_chapter=args.end
        )
        
        if not success:
            sys.exit(1)


if __name__ == '__main__':
    main()
