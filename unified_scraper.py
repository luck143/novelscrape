#!/usr/bin/env python3
"""
Unified Novel Scraper - Centralized Controller for NovelScrape

This script provides a unified interface for scraping novels from multiple
novel hosting websites. It consolidates the functionality of all individual
scraper scripts into a single, user-friendly CLI tool.

Supported Websites:
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

Usage:
    python unified_scraper.py

Author: NovelScrape Project
Date: 2026-01-01
"""

# ============================================================================
# QUICK MODE CONFIGURATION
# Set these values to skip interactive prompts
# Set QUICK_MODE = False to use interactive mode
# ============================================================================

QUICK_MODE = True  # Set to False to use interactive mode

# Test URL for reference
TEST_URL = "https://www.empirenovel.com/novel/nine-star-hegemon-body-arts/"

# Website configuration (must match a key in scraper_configs.json)
# Examples: 'boxnovel.com', 'novelfull.com', 'wuxiaworld.com', etc.
website = 'empirenovel.com'  # Change this to your desired website

# Novel configuration
novel_name = 'nine-star-hegemon-body-arts'  # Name for saving files (will be used as directory name)
novel_slug = 'nine-star-hegemon-body-arts'  # Slug from URL (e.g., 'shadow-slave' from URL like boxnovel.com/novel/shadow-slave)

# Chapter range (optional - will be prompted if not provided in CLI mode)
start_chapter = 1  # Starting chapter number (e.g., 1)
end_chapter = 10  # Ending chapter number (e.g., 100)

# ============================================================================

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import trafilatura
from unidecode import unidecode
import os
import sys
import time
import json
import codecs
import argparse

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# ============================================================================
# WEBSITE CONFIGURATIONS
# ============================================================================

def load_configs(config_file='scraper_configs.json'):
    """
    Load website configurations from JSON file
    
    Args:
        config_file: Path to the JSON configuration file
        
    Returns:
        Dictionary of website configurations
        
    Raises:
        SystemExit: If configuration file is missing or invalid
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        
        # Check if configs is a dictionary
        if not isinstance(configs, dict):
            print(f"[X] Invalid configuration format: expected JSON object, got {type(configs).__name__}")
            sys.exit(1)
        
        return configs['websites']
    except FileNotFoundError:
        print(f"[X] Configuration file not found: {config_file}")
        print("[X] Please ensure scraper_configs.json exists in the project directory")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[X] Error parsing configuration file: {e}")
        sys.exit(1)
    except KeyError:
        print(f"[X] Invalid configuration format: 'websites' key not found")
        sys.exit(1)


# Load website configurations from JSON file
WEBSITE_CONFIGS = load_configs()


# ============================================================================
# SCRAPER CLASS
# ============================================================================

class UnifiedScraper:
    """Unified scraper for multiple novel websites"""
    
    def __init__(self, website, novel_name, novel_slug, start_chapter, end_chapter):
        """
        Initialize the scraper
        
        Args:
            website: Website domain (e.g., 'boxnovel.com')
            novel_name: Name for saving files
            novel_slug: Slug for URL construction
            start_chapter: Starting chapter number
            end_chapter: Ending chapter number
        """
        if website not in WEBSITE_CONFIGS:
            raise ValueError(f"Unsupported website: {website}")
        
        self.website = website
        self.config = WEBSITE_CONFIGS[website]
        self.novel_name = novel_name
        self.novel_slug = novel_slug
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.driver = None
        
        # Create download directory
        self.download_dir = f'downloads/{novel_name}'
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Statistics
        self.success_count = 0
        self.failed_count = 0
        self.failed_chapters = []
        self.successful_chapters = []
    
    def initialize_driver(self):
        """Initialize Chrome driver with appropriate configuration"""
        try:
            options = webdriver.ChromeOptions()
            
            # Check if website uses standard Chrome (lightnovelworld.co)
            if self.config.get('use_standard_chrome', False):
                # Special options for lightnovelworld.co
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--remote-debugging-port=9222')
                
                # Use custom profile directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                profile_dir = os.path.join(script_dir, 'chromeprofile')
                os.makedirs(profile_dir, exist_ok=True)
                options.add_argument(f'user-data-dir={profile_dir}')
                
                try:
                    self.driver = webdriver.Chrome(options=options)
                except Exception as e:
                    print(f"✗ Error initializing standard Chrome driver: {e}")
                    return False
            else:
                # Use undetected_chromedriver for most websites
                if self.config.get('headless', False):
                    options.headless = True
                
                if self.config.get('chrome_version'):
                    self.driver = uc.Chrome(
                        use_subprocess=True,
                        options=options,
                        version_main=self.config['chrome_version']
                    )
                else:
                    self.driver = uc.Chrome(use_subprocess=True, options=options)
            
            print(f"✓ Chrome driver initialized for {self.config['name']}")
            return True
            
        except Exception as e:
            print(f"✗ Error initializing Chrome driver: {e}")
            return False
    
    def build_url(self, chapter_num):
        """
        Build URL for a specific chapter
        
        Args:
            chapter_num: Chapter number
            
        Returns:
            Full URL for the chapter
        """
        return self.config['url_pattern'].format(
            novel_slug=self.novel_slug,
            chapter_num=chapter_num
        )
    
    def wait_for_page_load(self):
        """Wait for page to load based on website configuration"""
        wait_type = self.config['wait_type']
        
        if wait_type == 'none':
            # No wait condition, just use delay
            time.sleep(self.config['delay'])
        else:
            # Wait for specific element
            try:
                by_type = getattr(By, wait_type)
                selector = self.config['wait_selector']
                timeout = self.config['timeout']
            except AttributeError:
                print(f"  Warning: Invalid wait_type '{wait_type}', using delay instead")
                time.sleep(self.config['delay'])
                return
            
            try:
                wait = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by_type, selector))
                )
                time.sleep(self.config['delay'])
            except Exception as e:
                print(f"  Warning: Wait condition failed: {e}")
                # Continue anyway, might still work
    
    def extract_content(self):
        """
        Extract content from current page
        
        Returns:
            Extracted text content
        """
        content = self.driver.page_source
        text = trafilatura.extract(content)
        return unidecode(text) if text else ""
    
    def check_captcha(self, text):
        """
        Check for captcha or rate limiting
        
        Args:
            text: Extracted text content
            
        Returns:
            True if captcha detected, False otherwise
        """
        if not self.config.get('captcha_detection', True):
            return False
        
        captcha_patterns = [
            'You need to enable JavaScript to run this app',
            'Anonymous users can read up to 10 chapters'
        ]
        
        for pattern in captcha_patterns:
            if pattern in text:
                if 'JavaScript' in pattern:
                    print(f"✗ Captcha detected!")
                else:
                    print(f"✗ Rate limit reached!")
                return True
        
        return False
    
    def save_chapter(self, chapter_num, text):
        """
        Save chapter content to file
        
        Args:
            chapter_num: Chapter number
            text: Chapter text content
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            filename = f"{chapter_num}.txt"
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(text)
            
            return True
        except Exception as e:
            print(f"  ✗ Error saving chapter {chapter_num}: {e}")
            return False
    
    def scrape_chapter(self, chapter_num, max_retries=2):
        """
        Scrape a single chapter
        
        Args:
            chapter_num: Chapter number to scrape
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        # Check if chapter already exists (resume functionality)
        filepath = os.path.join(self.download_dir, f"{chapter_num}.txt")
        if os.path.exists(filepath):
            print(f"  ✓ Chapter {chapter_num} already exists, skipping")
            return True
        
        url = self.build_url(chapter_num)
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                print(f"  Retry {attempt}/{max_retries} for chapter {chapter_num}")
            
            try:
                # Navigate to URL
                self.driver.get(url)
                
                # Wait for page load
                self.wait_for_page_load()
                
                # Extract content
                text = self.extract_content()
                
                # Check for captcha
                if self.check_captcha(text):
                    print(f"  ✗ Stopping due to captcha/rate limit")
                    return False
                
                # Check if content was extracted
                if not text or len(text) < 100:
                    print(f"  ✗ No content extracted or content too short")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    return False
                
                # Check for next link if use_next_link is enabled
                if self.config.get('use_next_link', False):
                    try:
                        selector = self.config['wait_selector']
                        next_element = self.driver.find_element(By.ID, selector)
                        if not next_element or not next_element.get_attribute('href'):
                            print(f"  ✗ Next link not found (possible captcha)")
                            if attempt < max_retries:
                                time.sleep(2)
                                continue
                            return False
                    except Exception as e:
                        print(f"  ✗ Error checking next link: {e}")
                        if attempt < max_retries:
                            time.sleep(2)
                            continue
                        return False
                
                # Save chapter
                if self.save_chapter(chapter_num, text):
                    print(f"  ✓ Chapter {chapter_num} downloaded successfully")
                    return True
                else:
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    return False
                    
            except Exception as e:
                print(f"  ✗ Error scraping chapter {chapter_num}: {e}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                return False
        
        return False
    
    def scrape_range(self):
        """
        Scrape a range of chapters
        
        Returns:
            Dictionary with success and failed chapter lists
        """
        print(f"\n{'='*60}")
        print(f"Starting scrape for: {self.novel_name}")
        print(f"Website: {self.config['name']} ({self.website})")
        print(f"Chapter range: {self.start_chapter} to {self.end_chapter}")
        print(f"Download directory: {self.download_dir}")
        print(f"{'='*60}\n")
        
        # Initialize driver
        if not self.initialize_driver():
            return {'success': [], 'failed': list(range(self.start_chapter, self.end_chapter + 1))}
        
        try:
            # Scrape each chapter
            total_chapters = self.end_chapter - self.start_chapter + 1
            for idx, chapter_num in enumerate(range(self.start_chapter, self.end_chapter + 1), 1):
                # Display progress
                progress = (idx / total_chapters) * 100
                print(f"[{progress:5.1f}%] Scraping chapter {chapter_num}/{self.end_chapter}")
                
                if self.scrape_chapter(chapter_num):
                    self.success_count += 1
                    self.successful_chapters.append(chapter_num)
                else:
                    self.failed_count += 1
                    self.failed_chapters.append(chapter_num)
                
                # Small delay between chapters
                time.sleep(0.5)
            
        except KeyboardInterrupt:
            print(f"\n\n✗ Scraping interrupted by user")
        except Exception as e:
            print(f"\n\n✗ Unexpected error: {e}")
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
                print("\n✓ Chrome driver closed")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Scraping Summary")
        print(f"{'='*60}")
        print(f"Total chapters: {self.end_chapter - self.start_chapter + 1}")
        print(f"Successfully downloaded: {self.success_count}")
        print(f"Failed: {self.failed_count}")
        
        if self.failed_chapters:
            print(f"\nFailed chapters: {', '.join(map(str, self.failed_chapters))}")
        
        print(f"{'='*60}\n")
        
        return {
            'success': self.successful_chapters,
            'failed': self.failed_chapters
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def display_welcome():
    """Display welcome message"""
    print("\n" + "="*60)
    print(" " * 15 + "UNIFIED NOVEL SCRAPER")
    print(" " * 12 + "NovelScrape Project")
    print("="*60 + "\n")


def display_websites():
    """Display list of supported websites"""
    print("Supported Websites:")
    print("-" * 60)
    
    websites = list(WEBSITE_CONFIGS.keys())
    for i, website in enumerate(websites, 1):
        config = WEBSITE_CONFIGS[website]
        print(f"  {i:2d}. {website:25s} - {config['name']}")
    
    print("-" * 60 + "\n")


def get_website_choice():
    """
    Get website choice from user
    
    Returns:
        Selected website domain
    """
    websites = list(WEBSITE_CONFIGS.keys())
    
    while True:
        try:
            choice = input(f"Select website (1-{len(websites)}) or enter website name: ").strip()
            
            # Check if user entered a number
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(websites):
                    return websites[choice_num - 1]
                else:
                    print(f"✗ Please enter a number between 1 and {len(websites)}")
            # Check if user entered a website name
            elif choice in websites:
                return choice
            else:
                print(f"✗ Invalid choice. Please enter a number or website name.")
                
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Error: {e}")


def get_novel_name():
    """
    Get novel name from user
    
    Returns:
        Novel name for file saving
    """
    while True:
        try:
            novel_name = input("Enter novel name (for saving files): ").strip()
            
            if not novel_name:
                print("✗ Novel name cannot be empty")
                continue
            
            # Sanitize novel name
            novel_name = novel_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            
            return novel_name
            
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user")
            sys.exit(0)


def get_novel_slug():
    """
    Get novel slug from user
    
    Returns:
        Novel slug for URL construction
    """
    while True:
        try:
            novel_slug = input("Enter novel slug (from URL, e.g., 'shadow-slave'): ").strip()
            
            if not novel_slug:
                print("✗ Novel slug cannot be empty")
                continue
            
            # Sanitize slug
            novel_slug = novel_slug.replace(' ', '-').lower()
            
            return novel_slug
            
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user")
            sys.exit(0)


def get_chapter_range():
    """
    Get chapter range from user
    
    Returns:
        Tuple of (start_chapter, end_chapter)
    """
    while True:
        try:
            start = input("Enter start chapter number: ").strip()
            end = input("Enter end chapter number: ").strip()
            
            if not start.isdigit() or not end.isdigit():
                print("✗ Please enter valid numbers")
                continue
            
            start_chapter = int(start)
            end_chapter = int(end)
            
            if start_chapter <= 0 or end_chapter <= 0:
                print("✗ Chapter numbers must be positive")
                continue
            
            if start_chapter > end_chapter:
                print("✗ Start chapter must be less than or equal to end chapter")
                continue
            
            return start_chapter, end_chapter
            
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user")
            sys.exit(0)


def confirm_scraping(website, novel_name, novel_slug, start_chapter, end_chapter):
    """
    Confirm scraping parameters with user
    
    Returns:
        True if user confirms, False otherwise
    """
    print("\n" + "="*60)
    print("Scraping Configuration:")
    print("-" * 60)
    print(f"  Website:        {WEBSITE_CONFIGS[website]['name']} ({website})")
    print(f"  Novel Name:     {novel_name}")
    print(f"  Novel Slug:     {novel_slug}")
    print(f"  Start Chapter:  {start_chapter}")
    print(f"  End Chapter:    {end_chapter}")
    print(f"  Total Chapters: {end_chapter - start_chapter + 1}")
    print("-" * 60)
    
    while True:
        try:
            choice = input("\nProceed with scraping? (y/n): ").strip().lower()
            
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("✗ Please enter 'y' or 'n'")
                
        except KeyboardInterrupt:
            print("\n\n✗ Operation cancelled by user")
            sys.exit(0)


def parse_cli_args():
    """
    Parse CLI arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Unified Novel Scraper - Download novels from multiple websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (no arguments)
  python unified_scraper.py
  
  # Quick mode (set QUICK_MODE = True at top of file)
  python unified_scraper.py
  
  # CLI mode with all parameters
  python unified_scraper.py --website empirenovel.com --novel-name "nine-star-hegemon" --novel-slug "nine-star-hegemon-body-arts" --start 1 --end 100
  
  # CLI mode with start chapter only (will prompt for end)
  python unified_scraper.py --website empirenovel.com --novel-name "nine-star-hegemon" --novel-slug "nine-star-hegemon-body-arts" --start 1
  
  # CLI mode with end chapter only (will prompt for start)
  python unified_scraper.py --website empirenovel.com --novel-name "nine-star-hegemon" --novel-slug "nine-star-hegemon-body-arts" --end 100
        """
    )
    
    parser.add_argument(
        '--website',
        type=str,
        help='Website domain (e.g., empirenovel.com, boxnovel.com)'
    )
    
    parser.add_argument(
        '--novel-name',
        type=str,
        help='Novel name for saving files (will be used as directory name)'
    )
    
    parser.add_argument(
        '--novel-slug',
        type=str,
        help='Novel slug from URL (e.g., shadow-slave)'
    )
    
    parser.add_argument(
        '--start',
        type=int,
        default=None,
        help='Starting chapter number (optional, will prompt if not provided)'
    )
    
    parser.add_argument(
        '--end',
        type=int,
        default=None,
        help='Ending chapter number (optional, will prompt if not provided)'
    )
    
    return parser.parse_args()


def main():
    """Main function"""
    # Access module-level configuration variables
    global website, novel_name, novel_slug, start_chapter, end_chapter
    
    try:
        # Check if we should use QUICK_MODE (no CLI arguments and QUICK_MODE is True)
        if len(sys.argv) == 1 and QUICK_MODE:
            # Use configuration from top of file
            print("\n" + "="*60)
            print(" " * 15 + "UNIFIED NOVEL SCRAPER")
            print(" " * 12 + "NovelScrape Project")
            print(" " * 20 + "Quick Mode")
            print("="*60 + "\n")
            
            print("Using configuration from file:")
            print(f"  Website:        {WEBSITE_CONFIGS[website]['name']} ({website})")
            print(f"  Novel Name:     {novel_name}")
            print(f"  Novel Slug:     {novel_slug}")
            print(f"  Start Chapter:  {start_chapter}")
            print(f"  End Chapter:    {end_chapter}")
            print(f"  Total Chapters: {end_chapter - start_chapter + 1}")
            print("="*60 + "\n")
            
            # Create scraper and start scraping directly
            scraper = UnifiedScraper(website, novel_name, novel_slug, start_chapter, end_chapter)
            results = scraper.scrape_range()
            
            # Final message
            if results['failed']:
                print(f"\n⚠ Scraping completed with {len(results['failed'])} failures")
                print(f"  You can retry the failed chapters later")
            else:
                print(f"\n✓ All chapters downloaded successfully!")
                print(f"  Files saved to: {scraper.download_dir}")
        else:
            # Display welcome message
            display_welcome()
            
            # Display supported websites
            display_websites()
            
            # Get user input
            website = get_website_choice()
            novel_name = get_novel_name()
            novel_slug = get_novel_slug()
            start_chapter, end_chapter = get_chapter_range()
            
            # Confirm scraping
            if not confirm_scraping(website, novel_name, novel_slug, start_chapter, end_chapter):
                print("\n✗ Scraping cancelled by user")
                return
            
            # Create scraper and start scraping
            scraper = UnifiedScraper(website, novel_name, novel_slug, start_chapter, end_chapter)
            results = scraper.scrape_range()
            
            # Final message
            if results['failed']:
                print(f"\n⚠ Scraping completed with {len(results['failed'])} failures")
                print(f"  You can retry the failed chapters later")
            else:
                print(f"\n✓ All chapters downloaded successfully!")
                print(f"  Files saved to: {scraper.download_dir}")
        
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
