#!/usr/bin/python
# -*- coding: utf-8 -*-
#Setting up selenium webdriver
import re

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
import os
import glob
import pandas as pd
from time import sleep
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--incognito')  # 隐身模式（无痕模式）
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
chromdriver_path = "/Users/jie/Downloads/chromedriver1" #Replacing it with your chromdriver_path
# driver = webdriver.Chrome(executable_path=, options=options)
ser = Service(r"{}".format(chromdriver_path))
driver = webdriver.Chrome(service=ser, options=options)
from bs4 import BeautifulSoup
# driver.maximize_window()
# driver = webdriver.Chrome(executable_path="/Users/jie/Downloads/chromedriver", chrome_options=options)
sleep(3)
MAX_WAIT = 20
import argparse
import math
import os

def concat(csv_files):
    all_ = pd.DataFrame()
    for i in range(len(csv_files)):
        try:
            df = pd.read_csv(csv_files[i],encoding="utf-8")
            # df['keyword'] = csv_files[i].split('/')[-1].split('.')[0].split('_')[-1]
            all_ = all_.append(df)
        except:
            continue
    return all_

def log_found(street,args):
    # global log_street_link_file
    if os.path.isdir('/'.join(args.found_path.split('/')[:-1])) == False:
        os.makedirs('/'.join(args.found_path.split('/')[:-1]))
    if not os.path.exists(args.found_path):
        open(args.found_path, 'w').write('%s\n' % (street))
    open(args.found_path, 'a').write('%s\n' % (street))

def log_unfound(street,args):
    # global log_street_link_file
    if os.path.isdir('/'.join(args.unfound_path.split('/')[:-1])) == False:
        os.makedirs('/'.join(args.unfound_path.split('/')[:-1]))
    if not os.path.exists(args.unfound_path):
        open(args.unfound_path, 'w').write('%s\n' % (street))
    open(args.unfound_path, 'a').write('%s\n' % (street))

#Specifing arguments (user inputs)
def parse_arguments():

    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        '-ff',
        "--found_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/found_streets_reviews_TripAdvisor.txt',
        help="local path where you record streets with complete reviews.",
    )
    # args = parser.parse_args(args=[])
    args = parser.parse_args()#args=[]

    return args

# weblink  = 'https://www.tripadvisor.com.sg/'

#Function for joining files under the folder
def concat(csv_files):
    all_ = pd.DataFrame()
    for i in range(len(csv_files)):
        try:
            df = pd.read_csv(csv_files[i],encoding="utf-8")
            # df['keyword'] = csv_files[i].split('/')[-1].split('.')[0].split('_')[-1]
            all_ = all_.append(df)
        except:
            continue
    return all_

#
# street = 'covert garden'
# city = 'London'

def main():
    os.chdir('/Users/jie/UrbanText')
    print('Current root directory: ', os.getcwd())
    args = parse_arguments()
    streets_df = pd.read_csv(args.file_path)
    streets = list(streets_df.Street.unique())

    print('City:',args.city)
    print('Save path:', args.save_path)
    print('File path:', args.file_path)
    # Open unfounded street txt and move records from streets_toscrape
    if os.path.exists(args.unfound_path) == True:
        with open(args.unfound_path) as f:
            lines = f.readlines()
        unfounded_streets = [line.split('\n')[0] for line in lines]
        exsiting_streets = list(set(unfounded_streets))
        streets_toscrape = [street for street in streets if street not in unfounded_streets]
    else:
        streets_toscrape = streets
    #Open founded street txt and remove records that are existed in review_dataset (save_path) from streets_toscrape
    if os.path.exists(args.found_path) == True:
        with open(args.found_path) as f:
            lines = f.readlines()
        founded_streets = [line.split('\n')[0] for line in lines]
        founded_streets = list(set(founded_streets))
        streets_toscrape = [street for street in streets_toscrape if street not in founded_streets]
    # """Checking if we have a considerate number of reviews for each streets, if not, put it into street_toscrape"""
    # if os.path.isdir(args.save_path) == True:
    #     csv_files = glob.glob(args.save_path + '/*.csv')
    #     # all_df = concat(csv_files)

    print('Need to scrape data for {} streets'.format(len(streets_toscrape)))

    driver.get('https://www.tripadvisor.com.sg/')

    for num, street in enumerate(streets_toscrape):
        if os.path.exists(os.path.join(args.save_path, "{}.csv".format('_'.join(street.split())))) == True:
            review_df = pd.read_csv(os.path.join(args.save_path, "{}.csv".format('_'.join(street.split()))))
            total_reviews = review_df.total_reviews.iloc[-1]
            if 'current_page' in review_df.columns:
                current_page = review_df.current_page.iloc[-1]
                page_number = review_df.page_number.iloc[-1]

            else:
                review_number = len(review_df)
                url_root = review_df.review_id.iloc[1]
                current_page = 'https://www.tripadvisor.com.sg/Attraction_Review-'+'-'.join(url_root.split('-')[:2] + ['Reviews-or{}'.format(review_number)] +url_root.split('-')[3:])
                page_number= review_number/10 - 1
                review_df['current_page'] = None
                review_df['page_number'] = None

        else:
            total_reviews = None
            current_page = None
            page_number = None
        scrapy_street(num, street, args,current_page=current_page,total_reviews=total_reviews,page_number=page_number)
        sleep(8)






#Function for expanding reviews
def expand_read_more():
    read_mores = driver.find_elements(By.XPATH, './/span[contains(text(), "Read more")]') #'.//span[@class="Ignyf _S Z"]'
    index = [num for num, i in enumerate([read.text for read in read_mores]) if i == 'Read more']
    click_mores = [i for num, i in enumerate(read_mores) if num in index]
    for c in click_mores:
        try:
            c.click()
            sleep(4)
        except:
            pass
def check_review1(driver):
    if driver.find_element(By.XPATH, './/span[@class="biGQs _P pZUbB KxBGd"]'):
        return True
    else:
        return False
def check_review2(driver):
    if driver.find_element(By.XPATH, './/div[@class="LbPSX"]'):
        return True
    else:
        return False

#Main function for scraping streets
def scrapy_street(num,street, args,current_page=None, total_reviews=None,page_number=None):
    print('Scraping for No.{} street {}'.format(num,street))
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://www.tripadvisor.com.sg/')
    if current_page != None:
        print('Picking up scraping reviews for {} from exisiting review dataset'.format(street))
        driver.get(current_page)

        sleep(5)
        count=0
        Scrolling = True
        while Scrolling:
            try:
                # Capture "Read more" buttons and click each of them to expand reviews
                expand_read_more()
                # Looping through pages and parse the content
                if page_number != 1:
                    start = int(page_number)+2
                else:
                    start = 1
                for i in range(start, math.ceil(total_reviews / 10) + 1):  #
                    print('{} of {}'.format(i, math.ceil(total_reviews / 10)))
                    if i >= page_number+1:
                        driver.get(current_page)
                        sleep(5)
                        current_page = driver.current_url
                        next_page = current_page.split('Reviews-')[0] + 'Reviews' + '-or{}-'.format(i * 10 - 10) + \
                                    current_page.split('Reviews-')[1]
                        try:
                            driver.get(next_page)
                            sleep(5)
                            expand_read_more()
                            sleep(5)
                        except NoSuchElementException:
                            print('Cannot locate next page')
                    sleep(10)
                    if check_review2(driver):  # or check_review1(driver)
                        response = BeautifulSoup(driver.page_source, 'html.parser')
                        sleep(2)
                        if i == 1:
                            current_page = driver.current_url
                        else:
                            current_page = next_page
                        review_parser(response, street, args, i, total_reviews, current_page)
                        sleep(6)
                    else:
                        print("No reviews anymore.")
                        count += 1
                        i = i - 1
                        if count >= 3:
                            Scrolling = False
                            break
                Scrolling = False
                log_found(street, args)
                print("Finishing scraping all pages")
                break

                # print('Finished scraping %s' % street)
                # driver.close()
                # driver.switch_to.window(driver.window_handles[0])
            except:
                Scrolling = False
                log_unfound(street, args)
                break

        driver.close()
        driver.switch_to.window(driver.window_handles[0])


    else:
        print('Scraping review for {} the first time'.format(street))
        wait = WebDriverWait(driver, MAX_WAIT)
        sleep(8)
        try:
            # search = wait.until(EC.element_to_be_clickable((By.XPATH, './/span[@class="QLiHN o W"]')))
            # search.click()
            box = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lithium-root"]/main/div[3]/div/div/div/form/input[1]')))
        except TimeoutException:
            print('Cannot locate search box')
        sleep(3)
        street_name = street+', '+args.city
        box.send_keys(street_name)
        sleep(4)
        # search.send_keys(Keys.RETURN)
        # sleep(3)
        #Clicking the first matched result
        driver.find_element(By.XPATH, './/div[@id="typeahead_results"]/a[@class="GzJDZ w z _S _F Wc Wh Q B- _G"]').click()
        sleep(5)

        # Going to review section
        headlines = ['Restaurant','Hotel','Flight','VacationRentals']
        if not any(ext in driver.current_url for ext in headlines):
            try:
                review = driver.find_element(By.XPATH, './/a[contains(@href, "#REVIEWS")]')
                try:
                    total_reviews = int(driver.find_element(By.XPATH,'.//div[@class="Ci"]').text.split()[-1].replace(',', ''))
                except:
                    total_reviews = None
                if not total_reviews:
                    try:
                        total_reviews = int(driver.find_element(By.XPATH, './/span[@class="qqniT"]').text.split()[0].replace(',', ''))
                    except:
                        total_reviews = None
                if not total_reviews:
                    try:
                        total_reviews = int(
                            driver.find_element(By.XPATH, './/span[@class="yyzcQ"]').text.split()[0].replace(',', ''))
                    except:
                        total_reviews = None

                review.click() #Go to the review section of the page
                sleep(4)
            except NoSuchElementException:
                print('Cannot locate review sections') #class="Jktgk Mc"
                log_unfound(street,args)
                pass

            # Capture current page url
            current_url = driver.current_url
            count = 0
            Scrolling = True
            while Scrolling:
                try:
                    # Capture "Read more" buttons and click each of them to expand reviews
                    expand_read_more()
                    #Looping through pages and parse the content
                    for i in range(1, math.ceil(total_reviews/10)+1): #
                        print('{} of {}'.format(i, math.ceil(total_reviews/10)))
                        if i >=2:
                            # driver.get(current_url)
                            # sleep(5)
                            # current_url = driver.current_url
                            next_page =current_url.split('Reviews-')[0]+ 'Reviews'+'-or{}-'.format(i*10-10)+current_url.split('Reviews-')[1]
                            try:
                                driver.get(next_page)
                                sleep(5)
                                expand_read_more()
                                sleep(5)
                            except NoSuchElementException:
                                print('Cannot locate next page')
                        sleep(6)
                        if check_review2(driver): #or check_review1(driver)
                            response = BeautifulSoup(driver.page_source, 'html.parser')
                            sleep(2)
                            if i ==1:
                                current_page = driver.current_url
                            else:
                                current_page = next_page
                            review_parser(response, street,args,i, total_reviews,current_page)
                            sleep(6)
                        else:
                            print("No reviews anymore.")
                            count += 1
                            i = i-1
                            if count >=3:
                                Scrolling = False
                                break
                    if i ==1:
                        log_unfound(street, args)
                    Scrolling = False
                    log_found(street, args)
                    print("Finishing scraping all pages")
                    break


                    # print('Finished scraping %s' % street)
                    # driver.close()
                    # driver.switch_to.window(driver.window_handles[0])
                except:
                    Scrolling = False
                    break

        else:
            print('No reviews for No.{} street {}.'.format(num, street))
            log_unfound(street,args)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])




def review_parser(response,street,args,i,total_reviews,current_page):
    #Parsing reviews on single page
    try:
        local_name = response.find('h1',class_ = 'QdLfr b d Pn').text if response.find('h1',class_ = 'QdLfr b d Pn') else response.find('h1',class_="biGQs _P fiohW eIegw").text
    except:
        local_name =None
        print('Cannot get local name for {}'.format(street))
    try:
        reviews_boxes = response.find("div", class_="LbPSX").find_all('div', class_="C") if response.find("div", class_="LbPSX") else None
        #response.find_all('div', class_='YibKl MC R2 Gi z Z BB pBbQr')
    except:
        reviews_boxes = None
        print('Cannot locate review boxes for street {}'.format(street))
    if reviews_boxes:
        # reviews_boxes = reviews_boxes.find_all('div', class_="C")

        for num, review in enumerate(reviews_boxes):
            print('Parsing review No.{} on page {} for street {}'.format(num,i,street))
            data = {}
            # review = reviews_boxes[1]
            data['user_id'] = review.find('span', class_ = 'biGQs _P fiohW fOtGX').text if review.find('span', class_ = 'biGQs _P fiohW fOtGX') else None
            data['user_loc'] = review.find('div', class_ = 'biGQs _P pZUbB osNWb').text if review.find('div', class_ = 'biGQs _P pZUbB osNWb') else None
            data['review_id'] = review.find('div', class_ = '_c').select_one("div:nth-of-type(3)").find('a')['href'].replace('/ShowUserReviews-','') if review.find('div', class_ = '_c').select_one("div:nth-of-type(3)") else None
            data['review_title'] = review.find('div', class_ = 'biGQs _P fiohW qWPrE ncFvv fOtGX').find('span', class_ = 'yCeTE').text if review.find('div', class_ = 'biGQs _P fiohW qWPrE ncFvv fOtGX').find('span', class_ = 'yCeTE') else None
            data['review_date'] = review.find('div', class_ = 'TreSq').find('div').text.replace('Written ','') if review.find('div', class_ = 'TreSq').find('div') else None
            data['review_text'] = review.find('div',class_= 'biGQs _P pZUbB KxBGd').find('span',class_='yCeTE').text if review.find('div',class_= 'biGQs _P pZUbB KxBGd').find('span',class_='yCeTE') else None
            pictures = review.find('div', class_= 'LblVz _e q').find_all('picture',class_='NhWcC _R mdkdE') if review.find('div', class_= 'LblVz _e q') else None
            data['picture_url'] = ','.join([pic.find('img')['src'] for pic in pictures]) if pictures else None
            data['review_rating'] = review.find('svg', attrs={"aria-label": True})['aria-label'][:3]
            data['street'] = street if street else None
            data['city'] = args.city if args.city else None
            data['local_name'] = local_name
            df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))
            df['total_reviews'] = total_reviews
            df['current_page']  = current_page
            # df['page_number'] = re.findall(r"-or(\d+)-", current_page)[0]
            df['page_number'] = i

            # review_df =pd.concat([review_df, df])
            if os.path.isdir(args.save_path) == False:
                os.makedirs(args.save_path)
            file_name = street.replace(' ', '_')
            if os.path.isfile(args.save_path + '/{}.csv'.format(file_name)) == False:
                df.to_csv(args.save_path + '/{}.csv'.format(file_name))
            else:
                existing = pd.read_csv(args.save_path + '/{}.csv'.format(file_name))
                existing = existing[df.columns.to_list()]
                if 'current_page' not in existing.columns:
                    existing['current_page'] = None
                    existing['page_number'] = None
                if df.review_id.iloc[0] not in list(existing.review_id.unique()):
                    df.to_csv(args.save_path + '/{}.csv'.format(file_name),header=False,mode='a')
    else:
        print('Failed to get reviews on page {}'.format(i))

if __name__ =='__main__':
    main()