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

# Loop through each link in the CSV with an index
with open(input_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for index, row in enumerate(reader, start=1):
        link = row["Link"]
        title = row["Title"]

        try:
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
                content = "\n".join(
                    [unidecode(p.get_text(strip=True)) for p in content_div.find_all(['p', 'br'])]
                )
                # Extract the content while retaining formatting
                extracted_content = []
                for element in content_div.descendants:
                    if element.name == 'p':  # Paragraphs
                        extracted_content.append(unidecode(element.get_text(strip=True)) + "\n\n")
                    elif element.name == 'br':  # Line breaks
                        extracted_content.append("\n\n")
                    elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # Headings
                        heading = f"\n{unidecode(element.get_text(strip=True)).upper()}\n"
                        extracted_content.append(heading)
                    elif element.name == 'em':  # Italics
                        italic_text = f"*{unidecode(element.get_text(strip=True))}*"
                        extracted_content.append(italic_text)
                    elif element.name == 'strong':  # Bold text
                        bold_text = f"**{unidecode(element.get_text(strip=True))}**"
                        extracted_content.append(bold_text)

                content = ''.join(extracted_content)

                # Save the content to a text file with an index
                output_file = os.path.join(output_directory, f"{index}_{title}.txt")
                with open(output_file, mode='w', encoding='utf-8') as output:
                    output.write(content)

                print(f"Content extracted and saved for: {index}_{title}")
            else:
                # Raise an error if no content is found
                raise ValueError(f"No content found in the webpage: {link}")

        except Exception as e:
            print(f"Error fetching {link}: {e}")

# Quit the driver
driver.quit()
