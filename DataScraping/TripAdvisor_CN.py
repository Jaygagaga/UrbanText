import re
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
import os
import glob
import pandas as pd
from time import sleep
from DataScraping.TripAdvisor import review_parser,concat
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
        "--cities",
        required=True,
        type=list,
        default=['Beijing','Wuhan','Chengdu'],
        help='city list',
    )

    parser.add_argument(
        '-s1',
        "--save_path_links",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/loc_links',
        help="local path where you want to save your scraped data",
    )
    parser.add_argument(
        '-s2',
        "--save_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/loc_reviews',
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
    parser.add_argument(
        '-option',
        "--option",
        required=True,
        type=str,
        default='street_urls',
        help="Get links to street on GoogleMap",
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
    print('Getting POI links for cities')
    wait = WebDriverWait(driver, MAX_WAIT)
    # print('Need to scrape data for {} streets'.format(len(streets_toscrape)))
    if args.option == 'street_urls':
        driver.get('https://www.tripadvisor.com.sg/Attractions')

        for num, city in enumerate(args.cities):
            try:
                # search = wait.until(EC.element_to_be_clickable((By.XPATH, './/span[@class="QLiHN o W"]')))
                # search.click()
                box = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="component_2"]/div/div/form/input[1]')))
            except TimeoutException:
                print('Cannot locate search box')
            sleep(3)
            box.send_keys(city)
            driver.find_element(By.XPATH,
                                './/div[@id="typeahead_results"]/a[@class="GzJDZ w z _S _F Wc Wh Q B- _G"]').click()
            sleep(5)
            driver.find_element(By.XPATH,'.//span[@class="KbzWw"]')
            url = driver.current_url
            url = url.split('Activities')[0]+'oa0'+url.split('Activities')[1]
            driver.get(url)
            scrapy_street(num, city, args)
            sleep(8)
    if args.option == 'street_reviews':
        driver.get('https://www.tripadvisor.com.sg/Attractions')
        csv_files = glob.glob(args.save_path_links + '/*.csv')
        if len(csv_files) != 0:
            all_df = concat(csv_files)
            print('Dataframe columns of scraped files:', all_df.columns)
            loc_urls = list(all_df.urls.unique())
            for url in loc_urls:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(url)
                response = BeautifulSoup(driver.page_source, 'html.parser')
                review_parser(response, city,args,i, total_reviews)









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
    if driver.find_elements(By.XPATH, './/div[@class="YibKl MC R2 Gi z Z BB pBbQr"]'):
        return True
    else:
        return False
def check_review2(driver):
    if driver.find_elements(By.XPATH, './/div[@class="LbPSX"]'):
        return True
    else:
        return False

#Main function for scraping streets
def scrapy_street(url,city,args):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    try:
        total_reviews = int(driver.find_element(By.XPATH, './/div[@class="Ci"]').text.split()[-1].replace(',', ''))
    except:
        total_reviews = None

    count = 0
    Scrolling = True
    current_url = driver.current_url
    while Scrolling:
        try:
            # Capture "Read more" buttons and click each of them to expand reviews
            expand_read_more()
            #Looping through pages and parse the content
            for i in range(1, math.ceil(total_reviews/10)+1): #
                print('Go to page {}'.format(i))
                if i >=2:
                    next_page =current_url.split('-oa')[0]+'-oa{}-'.format(i*10+10)+current_url.split('-oa')[-1].split('-')[-1]
                    try:
                        driver.get(next_page)
                        sleep(7)
                        expand_read_more()
                        sleep(5)
                    except NoSuchElementException:
                        print('Cannot locate next page')
                        pass
                # if check_review2(driver): #or check_review1(driver)
                response = BeautifulSoup(driver.page_source, 'html.parser')
                sleep(2)
                street_parser(response, city, args, i)
                sleep(6)
        except:
            Scrolling = False
            break
    driver.close()
    driver.switch_to.window(driver.window_handles[0])



def street_parser(response,city,args,i):
    #Parsing reviews on single page
    try:
        reviews_boxes = response.find_all("section", class_="jemSU")
    except:
        reviews_boxes = None
        print('Cannot locate review boxes for street {}'.format(city))
    if reviews_boxes:
        for num, review in enumerate(reviews_boxes[1:]):
            print('Parsing review No.{} on page {} for street {}'.format(num,i,city))
            data = {}
            # review = reviews_boxes[1]
            data['loc'] = re.sub(re.compile(r'\d+\.'),'',review.find('span',attrs={'name':'title'}).text).strip() if review.find('span',attrs={'name':'title'}).text else None
            data['url'] = review.find('div',class_="NxKBB").find('a')['href'] if review.find('div',class_="NxKBB").find('a') else None

            data['review_rating'] = review.find('span', class_="biGQs _P pZUbB osNWb").text if review.find('span', class_="biGQs _P pZUbB osNWb").text else None

            df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))
            df['city'] = city

            # review_df =pd.concat([review_df, df])
            if os.path.isdir(args.save_path_links) == False:
                os.makedirs(args.save_path_links)
            file_name = data['loc'].replace(' ', '_')
            file_name = file_name+'_{}'.format(city)
            if os.path.isfile(args.save_path_links + '/{}.csv'.format(file_name)) == False:
                df.to_csv(args.save_path_links + '/{}.csv'.format(file_name))
            else:
                existing = pd.read_csv(args.save_path_links + '/{}.csv'.format(file_name))
                existing = existing[df.columns.to_list()]
                if df.review_id.iloc[0] not in list(existing.review_id.unique()):
                    df.to_csv(args.save_path_links + '/{}.csv'.format(file_name),header=False,mode='a')
    else:
        print('Failed to get reviews on page {}'.format(i))

if __name__ =='__main__':
    main()