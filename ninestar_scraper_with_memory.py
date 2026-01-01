"""
Nine Star Hegemon Body Arts scraper with Memory Bank integration
Based on empirenovel.py but with memory bank tracking
"""

import os
import sys
import time
from re import I
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
import trafilatura
from unidecode import unidecode
import concurrent.futures
from memory_bank import memory_bank

# Configuration
NUM_THREADS = 5
NOVEL_NAME = "ninestar"
BASE_URL = "https://www.empirenovel.com/novel/nine-star-hegemon-body-arts/"
START_CHAPTER = 5000  # Default start chapter
END_CHAPTER = 5156    # Default end chapter

# Initialize Chrome driver
options = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True)


def scrape_data(novel_name, chapter_num, url):
    """
    Scrape a single chapter and save it to file
    Integrated with memory bank to track progress
    """
    # Check if chapter already downloaded using memory bank
    if memory_bank.is_chapter_downloaded(novel_name, chapter_num):
        print(f"Chapter {chapter_num} already downloaded, skipping...")
        return True
    
    print(f"Scraping chapter {chapter_num}: {url}")
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, 'read-novel'))
        )
        time.sleep(2)
        content = driver.page_source
        
        text = trafilatura.extract(content)
        
        if 'You need to enable JavaScript to run this app' in text:
            print("Captcha Found")
            time.sleep(30)
            return False
        elif 'Anonymous users can read up to 10 chapters' in text:
            print("Limit Reached")
            return False
        else:
            # Create directory if it doesn't exist
            os.makedirs(f'downloads/{novel_name}', exist_ok=True)
            
            # Save chapter to file
            filename = f"{chapter_num}.txt"
            file_path = f'downloads/{novel_name}/{filename}'
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(unidecode(text))
            
            # Mark chapter as downloaded in memory bank
            memory_bank.mark_chapter_downloaded(
                novel_name, 
                chapter_num, 
                file_path
            )
            
            print(f"Chapter {chapter_num} downloaded successfully")
            return True
            
    except Exception as e:
        print(f"Error scraping chapter {chapter_num}: {e}")
        return False


def register_novel_in_memory_bank():
    """Register the novel in the memory bank if not already registered"""
    if memory_bank.get_novel_info(NOVEL_NAME) is None:
        memory_bank.register_novel(
            NOVEL_NAME,
            BASE_URL,
            END_CHAPTER,
            {
                "title": "Nine Star Hegemon Body Arts",
                "source": "empirenovel.com",
                "scraper": "ninestar_scraper_with_memory.py"
            }
        )
        print(f"Novel '{NOVEL_NAME}' registered in memory bank")
    else:
        print(f"Novel '{NOVEL_NAME}' already exists in memory bank")


def get_resume_point():
    """
    Get the chapter number to resume from based on memory bank
    Returns the next chapter to download
    """
    next_chapter = memory_bank.get_next_chapter_to_download(NOVEL_NAME)
    if next_chapter:
        print(f"Resuming from chapter {next_chapter}")
        return next_chapter
    
    # If no chapters downloaded yet, start from START_CHAPTER
    print(f"No previous downloads found, starting from chapter {START_CHAPTER}")
    return START_CHAPTER


def main():
    """Main function to run the scraper with memory bank integration"""
    print("Nine Star Hegemon Body Arts Scraper with Memory Bank")
    print("=" * 50)
    
    # Register novel in memory bank
    register_novel_in_memory_bank()
    
    # Get starting point (resume if interrupted)
    start_chapter = get_resume_point()
    
    # Set novel status to downloading
    memory_bank.set_novel_status(NOVEL_NAME, "downloading")
    
    try:
        # Scrape chapters from start to end
        for chapter_num in range(start_chapter, END_CHAPTER + 1):
            url = f"{BASE_URL}{chapter_num}"
            
            success = scrape_data(NOVEL_NAME, chapter_num, url)
            
            if not success:
                print(f"Failed to download chapter {chapter_num}, stopping...")
                memory_bank.set_novel_status(NOVEL_NAME, "error")
                break
                
            # Small delay between requests to be respectful
            time.sleep(1)
        else:
            # All chapters downloaded successfully
            memory_bank.set_novel_status(NOVEL_NAME, "completed")
            print(f"All chapters downloaded successfully!")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        memory_bank.set_novel_status(NOVEL_NAME, "paused")
    except Exception as e:
        print(f"Unexpected error: {e}")
        memory_bank.set_novel_status(NOVEL_NAME, "error")
    finally:
        driver.quit()
        
        # Print summary
        downloaded_chapters = memory_bank.get_downloaded_chapters(NOVEL_NAME)
        print(f"\nScraping summary:")
        print(f"Total chapters downloaded: {len(downloaded_chapters)}")
        print(f"Last chapter downloaded: {max(downloaded_chapters) if downloaded_chapters else 'None'}")
        print(f"Novel status: {memory_bank.get_novel_status(NOVEL_NAME)}")


if __name__ == "__main__":
    # Check if custom range provided via command line
    if len(sys.argv) >= 3:
        try:
            START_CHAPTER = int(sys.argv[1])
            END_CHAPTER = int(sys.argv[2])
            print(f"Using custom range: {START_CHAPTER} to {END_CHAPTER}")
        except ValueError:
            print("Invalid chapter range provided. Using defaults.")
    
    main()