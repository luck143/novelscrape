import csv
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unidecode import unidecode
import undetected_chromedriver as uc

# Initialize undetected_chromedriver
options = webdriver.ChromeOptions()
driver = uc.Chrome(use_subprocess=True)

# Read the CSV file
input_file = "wanderinginn/list.csv"


# Directory to save the extracted content
output_directory = "downloads/wandering_inn"

if not os.path.exists(output_directory):
    os.makedirs(output_directory)  # Create the directory if it doesn't exist

link="https://wanderinginn.com/2020/01/30/mini-stories-crabs-and-drinks/"

# Use Selenium to fetch the webpage
driver.get(link)

# Wait for the content to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "entry-content"))
)

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
content_div = soup.find('div', class_='entry-content')

# Check if content exists
if content_div:
    # Extract the content while retaining formatting
    content = []

    for element in content_div.find_all(['p', 'br', 'em', 'strong', 'i']):
        if element.name == 'p':
            # Process paragraph content, including inline tags like <em>, <strong>, etc.
            # Don't separate inline tags - just extract the full HTML of the <p> element
            content.append(str(element))
        elif element.name == 'br':
            # Handle <br> tags as line breaks
            content.append('\n')

    # Join the extracted content into a single string with proper spacing
    full_content = "\n\n".join(content)
    
    # Save the content to a text file with an index
    output_file = os.path.join(output_directory, f"15.txt")
    with open(output_file, mode='w', encoding='utf-8') as output:
        output.write(full_content)

    print(f"Content extracted and saved for: 1")
else:
    # Raise an error if no content is found
    raise ValueError(f"No content found in the webpage: {link}")


# Quit the driver
driver.quit()
