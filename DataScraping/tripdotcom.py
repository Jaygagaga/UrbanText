#Setting up selenium webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd

import os
import glob
from time import sleep
import argparse
import math
import os

# you might need to run this: xattr -d com.apple.quarantine /usr/local/bin/chromedriver
# this is to allow using chromedriver

# parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-ch',
        "--chromedriver_path",
        required=True,
        type=str,
        default='./Data/chrome_driver/chromedriver',
        help="Local path where you put the list of streets",
    )
    
    parser.add_argument(
        '-f',
        "--file_path",
        required=True,
        type=str,
        default='./Data/London_streets.csv',
        help="Local path where you put the list of streets",
    )

    parser.add_argument(
        '-c',
        "--city",
        required=True,
        type=str,
        default='London',
        help="The city where the streets belong to",
    )

    parser.add_argument(
        '-s',
        "--save_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor',
        help="local path where you want to save your scraped data",
    )
    parser.add_argument(
        '-u',
        "--unfound_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/unfound_streets_reviews_TripAdvisor.txt',
        help="Record unfound streets or streets without reviews",
    )
    # args = parser.parse_args(args=[])
    args = parser.parse_args()#args=[]

    return args

class TripScraper:
    def __init__(self, args: argparse.ArgumentParser) -> None:
        # set constant
        self.MAX_WAIT = 20
        self.args = args
        # initialize webdriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--incognito')  # 隐身模式（无痕模式）
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # driver = webdriver.Chrome(executable_path=, options=options)
        ser = Service(f"{args.chromedriver_path}")
        self.driver = webdriver.Chrome(service=ser, options=options)
        # load street names
        streets_df = pd.read_csv(args.file_path)
        streets = list(streets_df.Street.unique()) 
        # read and concatenate csv files
        csv_files = glob.glob(self.args.save_path+'/*.csv')
        data_frames = []
        for file_name in csv_files:
            df = pd.read_csv(file_name)
            data_frames.append(df)
        if len(csv_files) != 0:
            all_df = pd.concat(data_frames)
            print('Dataframe columns of scraped files:', all_df.columns)
            scraped_streets = list(all_df.street.unique())
            self.streets_toscrape = [street for street in streets if street not in scraped_streets]
        else:
            self.streets_toscrape = streets  
            
    #Main unction for scraping streets
    def scrapy_street(self, street):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get('https://sg.trip.com/?locale=en-sg')

        wait = WebDriverWait(self.driver, self.MAX_WAIT)
        sleep(5)
        try:
            # search = wait.until(EC.element_to_be_clickable((By.XPATH, './/span[@class="QLiHN o W"]')))
            # search.click()
            box = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ibuHeaderSearch"]/div/div/div[1]/input')))
        except TimeoutException:
            print('Cannot locate search box')
        sleep(3)
        street_name = street+', '+ self.args.city
        print(street_name)
        box.send_keys(street_name)
        sleep(4)
        # search.send_keys(Keys.RETURN)
        # sleep(3)
        #Clicking the first matched result
        self.driver.find_element(By.XPATH, '//*[@id="react-tabs-92"]/div').click()
        sleep(5)

        # # Going to review section
        # try:
        #     review = self.driver.find_element(By.XPATH, './/a[contains(@href, "#REVIEWS")]')
        #     try:
        #         total_number = int(self.driver.find_element(By.XPATH,'.//div[@class="Ci"]').text.split()[-1].replace(',', ''))
        #     except:
        #         total_number = None
        #     if not total_number:
        #         try:
        #             total_number = int(self.driver.find_element(By.XPATH, './/span[@class="qqniT"]').text.split()[0].replace(',', ''))
        #         except:
        #             total_number = None
        #     review.click() #Go to the review section of the page
        #     sleep(4)
        # except NoSuchElementException:
        #     print('Cannot locate review sections') #class="Jktgk Mc"
        #     log_unfound(street,args)
        #     pass

        # # Capture current page url
        # current_url = self.driver.current_url
        # count = 0
        # Scrolling = True
        # while Scrolling:
        #     try:
        #         # Capture "Read more" buttons and click each of them to expand reviews
        #         expand_read_more()
        #         #Looping through pages and parse the content
        #         for i in range(1, math.ceil(total_number/10)): #
        #             if i >=2:
        #                 next_page =current_url.split('Reviews-')[0]+ 'Reviews'+'-or{}-'.format(i*10-10)+current_url.split('Reviews-')[1]
        #                 try:
        #                     self.driver.get(next_page)
        #                     sleep(5)
        #                     expand_read_more()
        #                     sleep(5)
        #                 except NoSuchElementException:
        #                     print('Cannot locate next page')
        #                     pass
        #             if check_review2(self.driver): #or check_review1(self.driver)
        #                 response = BeautifulSoup(self.driver.page_source, 'html.parser')
        #                 sleep(2)
        #                 review_parser(response, street,args,i)
        #                 sleep(6)
        #             else:
        #                 print("No reviews anymore.")
        #                 count += 1
        #                 if count >=3:
        #                     Scrolling = False
        #                     break


        #         # print('Finished scraping %s' % street)
        #         # self.driver.close()
        #         # self.driver.switch_to.window(self.driver.window_handles[0])
        #     except:
        #         Scrolling = False
        #         break
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

   

    # run all the functions
    def execute(self) -> None:
        print('Need to scrape data for {} streets'.format(len(self.streets_toscrape)))
        self.driver.get('https://sg.trip.com/?locale=en-sg')
        for street in self.streets_toscrape:
            self.scrapy_street(street)
        pass
    
if __name__ == "__main__":
    args = parse_arguments()
    print('City:',args.city)
    print('Save path:', args.save_path)
    print('File path:', args.file_path)
    print('Getting streets that have been scraped...')
    trip_scraper = TripScraper(args)
    trip_scraper.execute()
    