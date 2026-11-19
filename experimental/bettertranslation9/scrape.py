#!/usr/bin/env python3
"""
EXPERIMENTAL — bettertranslation9.wordpress.com scraper (do NOT integrate yet).

Experimental scraper for WordPress.com-hosted novel sites (bettertranslation9).
Follows the scraper.py architecture (config file -> Chrome driver -> trafilatura
extraction -> downloads/<novel_name>/N.txt) but uses TOC-driven URL discovery,
because chapter URLs on this site are irregular date-based slugs and cannot be
built from a url_pattern with .format(chapter_num=).

Pipeline (run from project root with venv/Scripts/python.exe):
  1. python experimental/bettertranslation9/scrape.py toc
       -> fetches the novel index page, saves experimental/bettertranslation9/toc.json
          mapping {"<chapter_num>": {"url": ..., "title": ...}}
  2. python experimental/bettertranslation9/scrape.py scrape --start 1 --end 3
       -> downloads chapters N..M into downloads/<novel_name>/N.txt

Main scraper.py, scraper_configs.json and combiner.py are NOT modified by this
experiment (owner rule: merge only after explicit approval).
"""

import argparse
import json
import os
import re
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import trafilatura
from unidecode import unidecode

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'config.json')


def load_config(config_file=DEFAULT_CONFIG):
    """Load the experimental per-site config (mirrors scraper.py load_configs)."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


class WordPressTocScraper:
    """TOC-driven scraper for bettertranslation9.wordpress.com.

    Mirrors UnifiedScraper's structure and conventions: initialize_driver /
    wait_for_page_load / extract_content / save_chapter / scrape_range,
    with skip-existing, retry, and stop-on-failure semantics.
    """

    def __init__(self, config, start_chapter=None, end_chapter=None):
        self.config = config
        self.novel_name = config['novel_name']
        self.start_chapter = start_chapter
        self.end_chapter = end_chapter
        self.driver = None
        self.toc = {}

        self.download_dir = os.path.join('downloads', self.novel_name)
        os.makedirs(self.download_dir, exist_ok=True)

        self.success_count = 0
        self.failed_count = 0
        self.failed_chapters = []
        self.successful_chapters = []
        self.stop_requested = False

    # ------------------------------------------------------------------ #
    # Driver                                                              #
    # ------------------------------------------------------------------ #

    def initialize_driver(self):
        """Standard Chrome (no undetected evasion needed on WordPress.com)."""
        try:
            options = webdriver.ChromeOptions()
            options.page_load_timeout = self.config.get('timeout', 30)
            options.set_capability('pageLoadStrategy', 'normal')
            if self.config.get('headless', False):
                options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1400,1000')

            self.driver = webdriver.Chrome(options=options)
            print(f"✓ Chrome driver initialized for {self.config['name']}")
            return True
        except Exception as e:
            print(f"✗ Error initializing Chrome driver: {e}")
            return False

    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    # ------------------------------------------------------------------ #
    # Page helpers                                                        #
    # ------------------------------------------------------------------ #

    def wait_for_page_load(self):
        """Wait for the configured element (mirrors scraper.py wait_for_page_load)."""
        wait_type = self.config.get('wait_type', 'none')
        if wait_type == 'none':
            time.sleep(self.config.get('delay', 2))
            return
        try:
            by = getattr(By, wait_type)
            WebDriverWait(self.driver, self.config.get('timeout', 30)).until(
                EC.visibility_of_element_located((by, self.config['wait_selector']))
            )
            time.sleep(self.config.get('delay', 2))
        except Exception as e:
            print(f"  Warning: Wait condition failed: {e}")

    def get_entry_content_html(self):
        """Return the chapter container HTML (content_selector), or full page."""
        selector = self.config.get('content_selector')
        if selector:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, selector)
                return el.get_attribute('innerHTML')
            except Exception:
                pass
        return self.driver.page_source

    def get_entry_title(self):
        """Return the post title (h1.entry-title) for chapter heading."""
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, 'h1.entry-title')
            return el.text.strip()
        except Exception:
            return ''

    # ------------------------------------------------------------------ #
    # TOC                                                                 #
    # ------------------------------------------------------------------ #

    def build_toc(self):
        """Fetch the novel index page and extract chapter_num -> url/title."""
        print(f"Fetching TOC: {self.config['index_url']}")
        self.driver.get(self.config['index_url'])
        self.wait_for_page_load()

        pattern = re.compile(self.config.get('toc_link_pattern', r'Chapter\s+(\d+)'),
                             re.IGNORECASE)
        links = self.driver.find_elements(By.CSS_SELECTOR, 'a')
        toc = {}
        for link in links:
            url = link.get_attribute('href') or ''
            text = (link.text or '').strip()
            if not url or not text:
                continue
            m = pattern.search(text)
            if not m or 'bettertranslation9.wordpress.com' not in url:
                continue
            # Index page also links the "next series" posts; require the
            # chapter link text to carry a chapter number (already done) and
            # keep the FIRST url seen per chapter number.
            num = int(m.group(1))
            if num not in toc:
                toc[num] = {'url': url, 'title': text}

        if not toc:
            print('✗ No chapter links found on the index page')
            return False

        self.toc = toc
        toc_file = self.config['toc_file']
        with open(toc_file, 'w', encoding='utf-8') as f:
            json.dump(toc, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {len(toc)} chapters to {toc_file} "
              f"(chapters {min(toc)}..{max(toc)})")
        return True

    # ------------------------------------------------------------------ #
    # Chapter scraping                                                    #
    # ------------------------------------------------------------------ #

    def extract_content(self):
        """Extract + clean chapter text (mirrors scraper.py extract_content)."""
        content = self.get_entry_content_html()
        text = trafilatura.extract(content)
        if not text:
            return ''
        text = unidecode(text)

        # Trim trailing page furniture (comments form etc.).
        for marker in self.config.get('trailing_markers', []):
            idx = text.find(marker)
            if idx != -1:
                text = text[:idx]
        return text.rstrip()

    def save_chapter(self, chapter_num, text):
        """Save downloads/<novel_name>/<chapter_num>.txt (main-line format)."""
        try:
            filepath = os.path.join(self.download_dir, f"{chapter_num}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"  ✗ Error saving chapter {chapter_num}: {e}")
            return False

    def scrape_chapter(self, chapter_num, max_retries=2):
        """Scrape one chapter from its TOC URL (mirrors scraper.py retry loop)."""
        entry = self.toc.get(str(chapter_num))
        if not entry:
            print(f"  ✗ Chapter {chapter_num} not in TOC — skipping")
            self.failed_count += 1
            self.failed_chapters.append(chapter_num)
            return False

        for attempt in range(1, max_retries + 1):
            try:
                print(f"  Chapter {chapter_num} (attempt {attempt}): {entry['url']}")
                self.driver.get(entry['url'])
                self.wait_for_page_load()

                text = self.extract_content()
                if not text or len(text) < 200:
                    print(f"  ✗ Empty/too-short content ({len(text)} chars)")
                    continue

                # Captcha/rate-limit detection: stop the whole range.
                if self.config.get('captcha_detection', False):
                    for p in ('You need to enable JavaScript',
                              'Anonymous users can read up to'):
                        if p in text:
                            print('✗ Captcha/rate-limit detected — stopping range')
                            self.stop_requested = True
                            return False

                # Normalize the heading to the main-line convention so
                # combiner.extract_chapter_title picks it up: the site titles
                # are 'The Greatest Estate Developer Chapter N: ...' -> strip
                # the novel prefix and prepend if not already Chapter-led.
                heading = re.sub(r'^.*?(Chapter\s+\d+.*)$', r'\1', entry['title'])
                if not re.match(r'^Chapter\s+\d+', text, re.IGNORECASE):
                    text = f"{heading}\n\n{text}"

                if self.save_chapter(chapter_num, text):
                    print(f"  ✓ Saved chapter {chapter_num} ({len(text)} chars)")
                    self.success_count += 1
                    self.successful_chapters.append(chapter_num)
                    return True
            except Exception as e:
                print(f"  ✗ Error on chapter {chapter_num}: {e}")
            time.sleep(self.config.get('delay', 2))

        self.failed_count += 1
        self.failed_chapters.append(chapter_num)
        return False

    def scrape_range(self):
        """Scrape start..end chapters from the TOC map."""
        toc_file = self.config['toc_file']
        if not os.path.exists(toc_file):
            print(f"✗ TOC file missing: {toc_file} — run the 'toc' command first")
            return False
        with open(toc_file, 'r', encoding='utf-8') as f:
            self.toc = json.load(f)

        chapters = [n for n in range(self.start_chapter, self.end_chapter + 1)
                    if str(n) in self.toc]
        missing = [n for n in range(self.start_chapter, self.end_chapter + 1)
                   if str(n) not in self.toc]
        if missing:
            print(f"  Note: {len(missing)} chapters missing from TOC: {missing[:10]}")

        for num in chapters:
            if self.stop_requested:
                print('✗ Stop requested — aborting remaining chapters')
                break
            filepath = os.path.join(self.download_dir, f"{num}.txt")
            if os.path.exists(filepath) and os.path.getsize(filepath) > 200:
                print(f"  = Chapter {num} already downloaded, skipping")
                self.success_count += 1
                continue
            self.scrape_chapter(num)
            time.sleep(self.config.get('delay', 2))

        print(f"\nDone: {self.success_count} ok, {self.failed_count} failed"
              + (f", failed: {self.failed_chapters}" if self.failed_chapters else ''))
        return self.failed_count == 0 and not self.stop_requested


def main():
    parser = argparse.ArgumentParser(
        description='EXPERIMENTAL scraper for bettertranslation9.wordpress.com')
    parser.add_argument('command', choices=['toc', 'scrape'],
                        help="toc = build chapter URL map; scrape = download range")
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int, default=3)
    parser.add_argument('--config', default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config = load_config(args.config)
    scraper = WordPressTocScraper(config, args.start, args.end)

    if not scraper.initialize_driver():
        sys.exit(1)

    try:
        if args.command == 'toc':
            ok = scraper.build_toc()
        else:
            ok = scraper.scrape_range()
    finally:
        scraper.quit_driver()

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
