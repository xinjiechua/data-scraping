import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import re

csv_file_path = 'scraped_data.csv'
pdf_directory = 'downloaded_pdfs'
os.makedirs(pdf_directory, exist_ok=True)

base_url = 'https://lom.agc.gov.my/'
driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
service = Service(driver_path)
chrome_options = Options()
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get('https://lom.agc.gov.my/principal.php?type=updated')

time.sleep(5)  

soup = BeautifulSoup(driver.page_source, 'html.parser')

table = soup.find('table', {'id': 'data-updated'})

data = []
if table:
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        act_no = cells[0].text.strip()
        title_links = cells[1].find_all('a')
        titles = [link.get_text(strip=True) for link in title_links]
        download_links = cells[2].find_all('a')
        downloads = [base_url + link['href'] for link in download_links] 

        for idx, (pdf_url, title) in enumerate(zip(downloads, titles)):
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                sanitized_title = re.sub(r'[\\/*?:"<>|\n]', "", title).strip()
                pdf_filename = f"{act_no}_{sanitized_title}.pdf"
                pdf_path = os.path.join(pdf_directory, pdf_filename)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"Downloaded: {pdf_filename}")

        row_data = {
            'Act No.': act_no,
            'Titles': ' | '.join(titles), 
        }
        data.append(row_data)
else:
    print("Table not found.")

driver.quit()

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['Act No.', 'Titles', 'Download Links'])
    writer.writeheader() 
    writer.writerows(data) 

print(f"Data successfully saved to {csv_file_path}")