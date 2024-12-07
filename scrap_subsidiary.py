import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import csv
import re

csv_file_path = 'subsidiary_pu_b__.csv'
pdf_directory = 'Federal Legislation/subsidiary_pu_b__'
base_url = 'https://lom.agc.gov.my/'
targeted_url = 'https://lom.agc.gov.my/subsid.php?type=pub'

os.makedirs(pdf_directory, exist_ok=True)

driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
service = Service(driver_path)
chrome_options = Options()
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(targeted_url)

time.sleep(5) 

def scrape_page():
    page_data = []
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'id': 'datatable1'})

    if table:
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            publication_date = cells[0].text.strip()
            pu_no = cells[1].text.strip()
    
            act_links = cells[2].find_all('a')
            acts = [link.get_text(strip=True) for link in act_links]
            
            title_with_acts = cells[2]
            for a_tag in title_with_acts.find_all('a'):
                a_tag.decompose()
            titles = [text.strip() for text in title_with_acts.stripped_strings if text.strip()]
            if len(titles) >= 2:
                malay_title = titles[0]
                english_title = titles[1]
            elif len(titles) == 1:
                malay_title = titles[0]
                english_title = malay_title
            else:
                malay_title = ""
                english_title = malay_title
                
            status = cells[3].text.strip()
            related_legislation = cells[4].text.strip()
            date_of_commencement = cells[5].text.strip()
            download_links = cells[6].find_all('a')
            downloads = [base_url + link['href'] for link in download_links]

            for idx, (pdf_url, title) in enumerate(zip(downloads, [english_title])):
                pdf_response = requests.get(pdf_url)
                if pdf_response.status_code == 200:
                    sanitized_pu_no = re.sub(r'[\\/*?:"<>|\n]', "_", pu_no).strip()
                    sanitized_title = re.sub(r'[\\/*?:"<>|\n]', "", title).strip()
                    max_length = 150
                    if len(title) > max_length:
                        sanitized_title = sanitized_title[:max_length]
                    pdf_filename = f"{sanitized_pu_no}_{sanitized_title}.pdf"
                    pdf_path = os.path.join(pdf_directory, pdf_filename)
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"Downloaded: {pdf_filename}")

            row_data = {
                'Publication Date' : publication_date,
                'P.U. No.': pu_no,
                'Titles': ' | '.join(titles),
                'Act' : ' | '.join(acts),
                'Status of Legislation': status,
                'Related Legislation': related_legislation,
                'Date of Commencement': date_of_commencement,
            }
            page_data.append(row_data)
    else:
        print("Table not found on this page.")
    
    return page_data

entries_select_element = driver.find_element(By.NAME, "datatable1_length")
entries_select = Select(entries_select_element)

entries_select.select_by_value('100')
time.sleep(5)

all_data = []

select_element = driver.find_element(By.XPATH, "//div[@class='dataTables_paginate paging_listbox']/select")
select = Select(select_element)


for index in range(len(select.options)):
    try:
        select.select_by_index(index)
        time.sleep(5) 
        print(f"Scraping page {index + 1} of {len(select.options)}")
        all_data.extend(scrape_page())
    except Exception as e:
        print(f"Error scraping page {index + 1}: {e}")
        continue

# index = 81
# select.select_by_index(index)
# time.sleep(5) 
# print(f"Scraping page {index + 1} of {len(select.options)}")
# all_data.extend(scrape_page())
# driver.quit()

try:
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['Publication Date', 'P.U. No.', 'Titles', 'Act', 'Status of Legislation', 'Related Legislation', 'Date of Commencement'])
        writer.writeheader()  
        writer.writerows(all_data)  
    print(f"Data successfully saved to {csv_file_path}")
except Exception as e:
    print(f"Error saving CSV file: {e}")