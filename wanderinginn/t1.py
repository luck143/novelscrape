from re import I
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import requests
import sys
import trafilatura
import re
from unidecode import unidecode
import csv
# options = uc.ChromeOptions()
# options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
# driver = uc.Chrome(options=options, version_main=94)
# driver = uc.Chrome(options=options)


options = webdriver.ChromeOptions() 
#options.headless = False
driver = uc.Chrome(use_subprocess=True)
time.sleep(5)
#sys.exit("aaa")

def scrape_data(url):
  
    driver.get(url)
    #wait = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'topnav')))
    wait = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME , "chapter-entry")))
    content = driver.page_source
    #print(content)
    
    filename=re.sub('[^A-Za-z0-9]+', '', url)+'.html'
    print(filename)
    file = open('sourcecodes/'+filename, 'w')
    file.write(unidecode(content))
    file.close()

    pattern = r'<a href="([^"]+)">([^<]+)</a>'

    # Finding all matches
    matches = re.findall(pattern, content)

    # Displaying the results
    for match in matches:
        link, title = match
        print("Link:", link)
        print("Title:", title)

        # File to save the results
        output_file = "links_and_titles.csv"

        # Write results to CSV
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Link", "Title"])  # Writing the header

            for match in matches:
                writer.writerow(match)  # Writing each link-title pair

        print(f"Data saved to {output_file}")


url='https://wanderinginn.com/table-of-contents/'

scrape_data(url)
        
        
driver.quit()
#sys.exit("end")

