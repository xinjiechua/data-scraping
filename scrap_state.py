from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import requests
import pandas as pd
import re


url = 'https://www.lawnet.com.my/egazette/documentlistother?id=362&value=Perak%20Legislative%20Supplement'
pdf_directory = "C:\\Docs\\data-scraping\\Perak\\legislative_supplement_"
csv_file_path = 'perak_legislative_supplement_.csv'
username = 'lawlibrary'  
password = 'lawnet2020'

os.makedirs(pdf_directory, exist_ok=True)

driver_path = "C:\\chromedriver-win64\\chromedriver.exe"
service = Service(driver_path)
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": pdf_directory,  # Set the download directory
    "download.prompt_for_download": False,  # Disable download prompt
    "plugins.always_open_pdf_externally": True  # Disable PDF viewer and directly download the PDF
})
driver = webdriver.Chrome(service=service, options=chrome_options) 

driver.get('https://www.lawnet.com.my/account/login')
time.sleep(2)
username_field = driver.find_element(By.ID, 'username')  # Adjust the selector
password_field = driver.find_element(By.NAME, 'password')  # Adjust the selector
login_button = driver.find_element(By.ID, 'login')

username_field.send_keys(username)
password_field.send_keys(password)
login_button.click()

time.sleep(5)
driver.get(url)

select = Select(driver.find_element(By.NAME, 'myTable_length'))
select.select_by_visible_text('100')

time.sleep(5)

def download_pdf(pdf_url, title):
    file_path = os.path.join(pdf_directory, f"{title}.pdf")
    if os.path.exists(file_path):
        return
    
    try:
        driver.get(pdf_url)
        time.sleep(5)
        
        downloaded_files = os.listdir(pdf_directory)
        downloaded_pdf = max(downloaded_files, key=lambda f: os.path.getctime(os.path.join(pdf_directory, f)))
        
        new_pdf_path = os.path.join(pdf_directory, f"{title}.pdf")
        os.rename(os.path.join(pdf_directory, downloaded_pdf), new_pdf_path)
        print(f"Downloaded and saved: {new_pdf_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {title}: {e}")
        
        
data = []

for i in range(4):
    next_button = driver.find_element(By.XPATH, '//li[@id="myTable_next" and not(contains(@class,"disabled"))]/a')
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    driver.execute_script("arguments[0].click();", next_button)
    time.sleep(2)
        
# while True:
rows = driver.find_elements(By.XPATH, '//table[@id="myTable"]/tbody/tr')
for row in rows:
    try:
        title_elements = row.find_elements(By.XPATH, './td[2]/a')
        first_part = ""
        english_title = ""
        csv_title = ""
        
        pdf_filename_parts = []
        for title_element in title_elements:
            title = title_element.text.strip()
            title_parts = title.split("\n")
            if len(title_parts) >= 2:
                first_part = title_parts[0].strip() 
                english_title = title_parts[-1].strip() 
                if len(english_title) > 50:
                    english_title = english_title[:50]
            sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", f"{first_part}_{english_title}").strip()
            # sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", f"{english_title}").strip()
            pdf_filename_parts.append(sanitized_title)
            csv_title += f"{title}\n"
        pdf_filename_parts = pdf_filename_parts[1:]
        if len(pdf_filename_parts) > 1 and len(pdf_filename_parts) < 3:
            pdf_filename = "_".join(pdf_filename_parts)
        else:
            pdf_filename = pdf_filename_parts[0]
        pdf_link = title_elements[0].get_attribute('href')

        if len(pdf_filename) > 150:
            pdf_filename = pdf_filename[:150]
            
        if pdf_link:
            download_pdf(pdf_link, pdf_filename)
            
        publication = row.find_element(By.XPATH, './td[3]').text.strip()
        data.append([csv_title, publication])

    except Exception as e:
        print("Error processing row: {e}")
        continue
        
    # try:
    #     next_button = driver.find_element(By.XPATH, '//li[@id="myTable_next" and not(contains(@class,"disabled"))]/a')
    #     driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    #     driver.execute_script("arguments[0].click();", next_button)
    #     time.sleep(2)
    # except:
    #     break

df = pd.DataFrame(data, columns=["Title", "Publication"])
df.to_csv(csv_file_path, index=False)

driver.quit()
