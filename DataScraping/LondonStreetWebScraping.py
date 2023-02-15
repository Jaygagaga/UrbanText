from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service



import os

import pandas as pd
from time import sleep

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--incognito')  # 隐身模式（无痕模式）
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
# driver = webdriver.Chrome(executable_path="/Users/jie/Downloads/chromedriver1", options=options)
ser = Service(r"/Users/jie/Downloads/chromedriver1")
driver = webdriver.Chrome(service=ser, options=options)
# driver.maximize_window()
# driver = webdriver.Chrome(executable_path="/Users/jie/Downloads/chromedriver", chrome_options=options)
sleep(3)

driver.get('https://www.londononline.co.uk/streetindex/')
sleep(100)
WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.XPATH, './/div[@class="col-sm-6 col-xs-12"]')))
# driver.find_element_by_xpath('//input[@name="username"]').click()

MAX_WAIT = 20
wait = WebDriverWait(driver, MAX_WAIT)
import string
alphabet = list(string.ascii_lowercase)
# London_streets = []
for alpha in alphabet[1:]:
    # alpha = alphabet[0]
    link = 'https://www.londononline.co.uk/streetindex/{}/'.format(alpha)
    print('Opening page {}'.format(link))
    driver.get(link)
    sleep(5)
    streets = driver.find_elements(By.XPATH,'.//li[@class="list-group-item"]/a')
    streets = [' '.join(street.text.split()[:-1]) for street in streets]
    streets =list(set(streets))
    print('Length of streets starting with {}: {}'.format(alpha,len(streets)))
    city = ['London']*len(streets)
    data = pd.DataFrame(list(zip(streets, city)),columns=['Street', 'City'])
    if os.path.exists('./Data/London_streets.csv') == False:
        data.to_csv('./Data/London_streets.csv')
    else:
        data.to_csv('./Data/London_streets.csv', header=False,mode='a')
