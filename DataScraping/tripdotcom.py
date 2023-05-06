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
from DataScraping.TripAdvisor import log_unfound,log_found, concat

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
        default='/Users/jie/Downloads/chromedriver1',
        help="chromedriver pathway",
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
        default='./Data/Reviews/Trip_London',
        help="local path where you want to save your scraped data",
    )
    parser.add_argument(
        '-u',
        "--unfound_path",
        required=True,
        type=str,
        default='./Data/Reviews/Trip/unfound_streets_reviews_Trip_London.txt',
        help="Record unfound streets or streets without reviews",
    )
    parser.add_argument(
        '-ff',
        "--found_path",
        required=True,
        type=str,
        default='./Data/Reviews/Trip/found_streets_reviews_Trip_London.txt',
        help="Record scraped streets that have complete reviews",
    )
    parser.add_argument(
        '-s1',
        "--save_path_links",
        required=True,
        type=str,
        default='./Data/Reviews/Trip/loc_reviews/loc_links_London.csv',
        help="local path where you want to save the review links",
    )
    parser.add_argument(
        '-option',
        "--option",
        required=True,
        type=str,
        default='street_urls',
        help="Get links to street on Trip",
    )
    parser.add_argument(
        '-url',
        "--url",
        required=True,
        type=str,
        default = 'https://sg.trip.com/travel-guide/attraction/london-309/tourist-attractions/',
        help="Get links to street on Trip",
    )

    # args = parser.parse_args(args=[])
    args = parser.parse_args()#args=[]

    return args
import re

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--incognito')  # 隐身模式（无痕模式）
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
#
# def log_found(street,args):
#     # global log_street_link_file
#     if os.path.isdir('/'.join(args.found_path.split('/')[:-1])) == False:
#         os.makedirs('/'.join(args.found_path.split('/')[:-1]))
#     if not os.path.exists(args.found_path):
#         open(args.found_path, 'w').write('%s\n' % (street))
#     open(args.found_path, 'a').write('%s\n' % (street))

#
# street = 'covert garden'
# city = 'London'
#Logging unfound streets or streets without reviews
# def log_unfound(street,args):
#     #Check if folder exists, if not, create folder
#     if os.path.isdir('/'.join(args.unfound_path.split('/')[:-1])) == False:
#         os.makedirs('/'.join(args.unfound_path.split('/')[:-1]))
#     #Check if file under the folder exists, if not write into new file
#     if os.path.exists(args.unfound_path) == False:
#         open(args.unfound_path, 'w').write('%s\n' % (street))
#     open(args.unfound_path, 'a').write('%s\n' % (street))


def main():
    os.chdir('/Users/jie/UrbanText')
    print('Current root directory: ', os.getcwd())
    args = parse_arguments()
    ser = Service(r"{}".format(args.chromedriver_path))
    driver = webdriver.Chrome(service=ser, options=options)
    if args.option == 'street_urls':
        scrapy_loc(driver, args)
    else:
        # driver.get('https://www.tripadvisor.com.sg/Attractions')
        loc_df = pd.read_csv(args.save_path_links)
        loc_df = loc_df[loc_df.url.isnull() == False]
        loc_df = loc_df.drop_duplicates('loc')
        city = loc_df.city.iloc[0]
        # Open unfounded street txt and move records from streets_toscrape
        if os.path.exists(args.unfound_path) == True:
            with open(args.unfound_path) as f:
                lines = f.readlines()
            unfounded_locs = [line.split('\n')[0] for line in lines]
            exsiting_streets = list(set(unfounded_locs))
            rest_loc = [loc for loc in loc_df['loc'].to_list() if loc not in unfounded_locs]
            locs_toscrape = loc_df[loc_df['loc'].isin(rest_loc)]

        else:
            locs_toscrape = loc_df
        # Open founded street txt and remove records that are existed in review_dataset (save_path) from streets_toscrape
        if os.path.exists(args.found_path) == True:
            with open(args.found_path) as f:
                lines = f.readlines()
            founded_locs = [line.split('\n')[0] for line in lines]
            rest_loc = [loc for loc in loc_df['loc'].to_list() if loc not in founded_locs]
            locs_toscrape = loc_df[loc_df['loc'].isin(rest_loc)]

        for num, (link, loc) in enumerate(zip(locs_toscrape['url'], locs_toscrape['loc'])):
            # print(num,url,loc)
            # break
            print('Scrapying review of {}'.format(loc))
            if os.path.exists(os.path.join(args.save_path, "{}.csv".format('_'.join(loc.split())))) == True:
                review_df = pd.read_csv(os.path.join(args.save_path, "{}.csv".format('_'.join(loc.split()))))
                total_reviews = review_df.total_reviews.iloc[-1]

                if 'current_page' in review_df.columns:
                    current_page = review_df.current_page.iloc[-1]
                    page_number = review_df.page_number.iloc[-1]

                else:
                    review_number = len(review_df)
                    url_root = review_df.review_id.iloc[1]
                    current_page = 'https://www.tripadvisor.com.sg/Attraction_Review-' + '-'.join(
                        url_root.split('-')[:2] + ['Reviews-or{}'.format(review_number)] + url_root.split('-')[3:])
                    page_number = review_number / 10 - 1
                    review_df['current_page'] = None
                    review_df['page_number'] = None

            else:
                total_reviews = None
                current_page = None
                page_number = None
def expand_read_more(driver):
    read_mores = driver.find_elements(By.XPATH, './/div[@class ="read_more_btn"]')
    index = [num for num, i in enumerate([read.text for read in read_mores]) if i == 'Show All']
    click_mores = [i for num, i in enumerate(read_mores) if num in index]
    for c in click_mores:
        try:
            c.click()
            sleep(4)
        except:
            pass
def review_parser(response, loc, args, page, total_reviews, city):
    try:
        review_boxes = response.find_all("div", class_="TripReviewItemContainer-sc-1fopyhi-0 review-item")
    except:
        reviews_boxes = None
    if reviews_boxes:
        for box in review_boxes:
            data = {}

            data['user'] = box.find('div', class_="review-user-name max-lines-2").text
            review = box.find("div", class_="gl-poi-detail_comment-content")
            data['review_text'] = review.find_all("div")[4].text
            photos = review.find("div",class_='photo_wall').find_all('img')
            data['review_rating'] = review.find('span', class_='review_score').text
            data['picture_url'] = ','.join([pic['src'] for pic in photos]) if photos else None
            data['loc'] = loc
            data['city'] = city
            df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
            df['total_reviews'] = total_reviews
            df['current_page'] = page
            # df['page_number'] = re.findall(r"-or(\d+)-", current_page)[0]
            # df['page_number'] = i
            if os.path.isdir(args.save_path) == False:
                os.makedirs(args.save_path)
            file_name = loc.replace(' ', '_')
            if os.path.isfile(args.save_path + '/{}.csv'.format(file_name)) == False:
                df.to_csv(args.save_path + '/{}.csv'.format(file_name))
            else:
                existing = pd.read_csv(args.save_path + '/{}.csv'.format(file_name))
                existing = existing[df.columns.to_list()]
                if df.review_id.iloc[0] not in list(existing.review_id.unique()):
                    df.to_csv(args.save_path + '/{}.csv'.format(file_name),header=False,mode='a')




def scrapy_review(driver, args,link, loc):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(link)
    sleep(3)
    address = driver.find_element(By.XPATH, './/span[@class="field"]').text
    #go to review section
    driver.find_element(By.XPATH, './/span[@class="review-more-btn"]').click()
    #Expand review
    current_url = driver.current_url
    page = 0
    Scrolling = True
    while Scrolling:
        try:
            expand_read_more(driver)
            response = BeautifulSoup(driver.page_source, 'html.parser')
            total_reviews = response.find('span', class_='tab-item-count').text.split(' reviews')[0]
            review_parser(response, loc, args, page, total_reviews, args.city)
            try:
                driver.find_element(By.XPATH, './/button[@class="btn-next "]').click()
                sleep(4)
                page += 1
            except:
                Scrolling = False
                log_found(loc, args)
                break

        except:
            Scrolling = False
            log_unfound(loc, args)
            break
    driver.close()
    driver.switch_to.window(driver.window_handles[0])







    # # driver.find_element(By.XPATH, './/div[@class="mc-srh-box__tab-name"]').click()
    # for num, street in enumerate(streets_toscrape):
    #     city_input = driver.find_element(By.XPATH, './/input[@id="tnt-online-input"]')
    #     city_input.clear()
    #     city_input.send_keys(args.city)
    #     destination_input = driver.find_element(By.XPATH, './/input[@id="tnt-online-keyinput"]')
    #     destination_input.send_keys(street)
    #     sleep(2)
    #     driver.find_element(By.XPATH, './/div[@class="search-icon"]').click()
    #

def parser_loc(driver, args):
    destination_cards = driver.find_elements(By.XPATH, './/ul[@class="poi-list-card"]/li')
    for card in destination_cards:
        data = {}
        try:
            data['loc'] = card.find_element(By.XPATH, './/div[@class="poi-name margin-bottom-gap"]/h3').text
        except:
            data['loc'] = None
        try:
            data['url'] = card.find_element(By.XPATH, './/a').get_attribute('href')
        except:
            data['url'] = None
        try:
            data['rating'] = card.find_element(By.XPATH, './/div[@class="online-trip-review"]//span[@class="rating"]').text
        except:
            data['rating'] = None
        try:
            data['address'] = card.find_element(By.XPATH, './/span[@class="location"]').text
        except:
            data['address'] = None
        try:
            if card.find_element(By.XPATH, './/span[contains(text(), "No reviews yet")]'):
                data['reviews_num'] = '0'
        except:
            data['reviews_num'] = card.find_element(By.XPATH, './/span[@class="reviews"]').text.replace(' Reviews', '')
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
        df['city'] = args.city
        log_found(data['loc'], args)

        if os.path.isdir(args.save_path) == False:
            os.makedirs(args.save_path)

        if os.path.isfile(args.save_path_links) == False:
            df.to_csv(args.save_path_links)
        else:
            existing = pd.read_csv(args.save_path_links)
            existing = existing[df.columns.to_list()]
            if df.url.iloc[0] not in list(existing.url.unique()):
                df.to_csv(args.save_path_links, header=False, mode='a')

def scrapy_loc(driver,args):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(args.url)
    sleep(5)
    parser_loc(driver, args)
    Scrolling = True
    count = 0
    while Scrolling:
        try:
            # last_review = driver.find_elements(By.XPATH, '//div[@jstcache="652"]')
            driver.execute_script('arguments[0].scrollIntoView(true);', driver.find_elements(By.XPATH, '//a[@class="online-poi-item-card"]')[-1])
            driver.find_element(By.XPATH, './/ul[@class="ant-pagination"]//li[@title="Next Page"]').click()
            count += 1
            print('Go to page {}'.format(count))
            sleep(3)
            parser_loc(driver, args)
        except:
            Scrolling = False
            break
    driver.close()
    driver.switch_to.window(driver.window_handles[0])




if __name__ =='__main__':
    main()