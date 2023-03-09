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

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--incognito')  # 隐身模式（无痕模式）
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
chromdriver_path = "/Users/jie/Downloads/chromedriver1"#Replacing it with your chromdriver_path
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
        nargs='+',
        help='city list',
    )

    parser.add_argument(
        '-s1',
        "--save_path_links",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/loc_reviews/loc_links_Wuhan.csv',
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
        default='./Data/Reviews/TripAdvisor/unfound_POIs_reviews_TripAdvisor.txt',
        help="Record unfound streets or streets without reviews",
    )
    parser.add_argument(
        '-ff',
        "--found_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/found_POIs_reviews_TripAdvisor.txt',
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
def go_to_city(driver,city,args):
    wait = WebDriverWait(driver, MAX_WAIT)
    try:
        box = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="component_2"]/div/div/form/input[1]')))
        sleep(5)
    except TimeoutException:
        print('Cannot locate search box')
    sleep(3)
    box.send_keys(city)
    sleep(2)
    url = driver.find_element(By.XPATH,
                        './/div[@id="typeahead_results"]/a[@class="GzJDZ w z _S _F Wc Wh Q B- _G"]').get_attribute('href')
    # sleep(5)
    # print('Getting POI links for {} city'.format(city))
    # sleep(5)
    # url = driver.find_element(By.XPATH,'.//a[@class="UikNM _G B- _S _T c G_ P0 wSSLS wnNQG raEkE"]').get_attribute('href')
    # url = driver.current_url
    url = url.split('Activities')[0] + 'oa0' + url.split('Activities')[1]
    scrapy_loc(url, city, args)  # Getting all POIs information (location name, loction url, location review counts) in city
    sleep(8)


def main():
    os.chdir('/Users/jie/UrbanText')
    print('Current root directory: ', os.getcwd())
    args = parse_arguments()
    streets_df = pd.read_csv(args.file_path,encoding='unicode_escape')
    streets = list(streets_df.Street.unique())

    print('Save path:', args.save_path)
    print('File path:', args.file_path)
    print('City lists:', args.cities)


    # print('Need to scrape data for {} streets'.format(len(streets_toscrape)))
    if args.option == 'street_urls':
        driver.get('https://www.tripadvisor.com.sg/Attractions')

        for num, city in enumerate(args.cities):
            go_to_city(driver, city, args)


    if args.option == 'street_reviews':
        driver.get('https://www.tripadvisor.com.sg/Attractions')
        loc_df = pd.read_csv(args.save_path_links)
        loc_df = loc_df[loc_df.url.isnull()==False]
        loc_df = loc_df.drop_duplicates('loc')
        city = loc_df.city.iloc[0]
        # Open unfounded street txt and move records from streets_toscrape
        if os.path.exists(args.unfound_path) == True:
            with open(args.unfound_path) as f:
                lines = f.readlines()
            unfounded_locs = [line.split('\n')[0] for line in lines]
            exsiting_streets = list(set(unfounded_locs))
            rest_loc =[loc for loc in loc_df['loc'].to_list() if loc not in unfounded_locs]
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

        for num, (url,loc) in enumerate(zip(locs_toscrape['url'],locs_toscrape['loc'])):
            # print(num,url,loc)
            # break
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
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])

            Scrolling = True
            if current_page != None:
                print('Picking up scraping reviews for {} from exisiting review dataset'.format(loc))
                driver.get(current_page)
                sleep(5)
                try:
                    local_name = driver.find_element(By.XPATH, './/h1[@class= "biGQs _P fiohW eIegw"]').text
                except:
                    local_name = None

                count = 0
                while Scrolling:
                    #Got to review sections
                    try:
                        review = driver.find_element(By.XPATH, './/a[contains(@href, "#REVIEWS")]')
                        if page_number != 1:
                            start = int(page_number) + 2
                        else:
                            start = 1
                        for i in range(start, math.ceil(total_reviews / 10) + 1):  #
                            print('{} of {}'.format(i, math.ceil(total_reviews / 10)))
                            if i >= page_number + 1:
                                driver.get(current_page)
                                sleep(5)
                                current_page = driver.current_url
                                next_page = current_page.split('Reviews-')[0] + 'Reviews' + '-or{}-'.format(
                                    i * 10 - 10) + \
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
                                sleep(6)
                                if i == 1:
                                    current_page = driver.current_url
                                else:
                                    current_page = next_page
                                review_parser(response, loc, args, i, total_reviews,local_name,city, current_page)
                                sleep(6)
                            else:
                                print("No reviews anymore.")
                                count += 1
                                i = i - 1
                                if count >= 3:
                                    Scrolling = False
                                    break
                        Scrolling = False
                        log_found(loc, args)
                        print("Finishing scraping all pages")
                        break

                            # print('Finished scraping %s' % street)
                            #
                    except:
                        Scrolling = False
                        break
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            else:
                print('Scraping review for {} the first time'.format(loc))
                driver.get('https://www.tripadvisor.com.sg' + url)
                sleep(5)
                try:
                    # If review section exists
                    review = driver.find_element(By.XPATH, './/a[contains(@href, "#REVIEWS")]')
                    try:
                        local_name = driver.find_element(By.XPATH, './/h1[@class= "biGQs _P fiohW eIegw"]').text
                    except:
                        local_name = None
                        # print('Cannot get local name for {}'.format(loc))
                    try:
                        total_reviews = int(
                            driver.find_element(By.XPATH, './/div[@class="Ci"]').text.split()[-1].replace(',', ''))
                    except:
                        total_reviews = None
                    if not total_reviews:
                        try:
                            total_reviews = int(
                                driver.find_element(By.XPATH, './/span[@class="qqniT"]').text.split()[0].replace(',',
                                                                                                                 ''))
                        except:
                            total_reviews = None
                    if not total_reviews:
                        try:
                            total_reviews = int(
                                driver.find_element(By.XPATH, './/span[@class="yyzcQ"]').text.split()[0].replace(',', ''))
                        except:
                            total_reviews = None
                    review.click()  # Go to the review section of the page
                    sleep(4)
                except NoSuchElementException:
                    print('Cannot locate review sections')  # class="Jktgk Mc"
                    log_unfound(loc, args)
                    Scrolling = False


                # Capture current page url
                current_url = driver.current_url
                count = 0
                while Scrolling:
                    try:
                        # Capture "Read more" buttons and click each of them to expand reviews
                        expand_read_more()
                        # Looping through pages and parse the content
                        for i in range(1, math.ceil(total_reviews / 10) + 1):  #

                            print('{} of {}'.format(i, math.ceil(total_reviews / 10)))
                            if i >= 2:
                                next_page = current_url.split('Reviews-')[0] + 'Reviews' + '-or{}-'.format(
                                    i * 10 - 10) + current_url.split('Reviews-')[1]
                                try:
                                    driver.get(next_page)
                                    sleep(5)
                                    expand_read_more()
                                    sleep(5)
                                except NoSuchElementException:
                                    print('Cannot locate next page')
                                    pass
                            if check_review2(driver):  # or check_review1(driver)

                                response = BeautifulSoup(driver.page_source, 'html.parser')
                                sleep(7)
                                if i == 1:
                                    current_page = driver.current_url
                                else:
                                    current_page = next_page
                                review_parser(response, loc, args, i, total_reviews,local_name,city, current_page)
                                sleep(6)
                            else:
                                print("No reviews anymore.")
                                count += 1
                                if count >= 3:
                                    Scrolling = False
                                    break
                        Scrolling = False
                        log_found(loc, args)
                        print("Finishing scraping all pages")
                        break
                    except:
                        Scrolling = False
                        break

                driver.close()
                driver.switch_to.window(driver.window_handles[0])





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

#Main function for scraping locations in the city, different from scrapy_street in TripAdvisor
def scrapy_loc(url,city,args):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)
    sleep(5)
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
            for i in range(1, math.ceil(total_reviews/30)+1): #
                print('Go to page {}'.format(i))
                if i >=2:
                    next_page =current_url.split('-oa')[0]+'-oa{}-'.format((i-1)*30)+current_url.split('-oa')[-1].split('-')[-1]
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
                sleep(4)
                loc_parser(response, city, args, i)
                sleep(6)
            log_found(city, args)
            Scrolling = False
            break

        except:
            Scrolling = False
            break
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def review_box(review):
    try:
        review.find('div', class_="XfVdV o AIbhI").text
        return True
    except:
        return False


def loc_parser(response,city,args,i):
    #Parsing reviews on single page
    try:
        reviews_boxes = response.find_all("section", class_="jemSU")
    except:
        reviews_boxes = None
        print('Cannot locate review boxes for street {}'.format(city))
    if reviews_boxes:
        for num, review in enumerate(reviews_boxes):
            if num != 0:
                if review_box(review)==True:
                    # review.find('div',class_="XfVdV o AIbhI").text
                    print('Parsing location information No.{} on page {} for street {}'.format(num, i, city))
                    data = {}
                    # review = reviews_boxes[1]
                    data['loc'] = re.sub(re.compile(r'\d+\.'), '',
                                         review.find('div', class_="XfVdV o AIbhI").text).strip() if review.find('div',
                                                                                                                 class_="XfVdV o AIbhI").text else None
                    data['url'] = review.find('div', class_="NxKBB").find('a')['href'] if review.find('div',
                                                                                                      class_="NxKBB").find(
                        'a') else None

                    data['reviews_num'] = review.find('span', class_="biGQs _P pZUbB osNWb").text if review.find('span',
                                                                                                                 class_="biGQs _P pZUbB osNWb") else None

                    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
                    df['city'] = city

                    if os.path.isdir(args.save_path) == False:
                        os.makedirs(args.save_path)

                    if os.path.isfile(args.save_path_links) == False:
                        df.to_csv(args.save_path_links)
                    else:
                        existing = pd.read_csv(args.save_path_links)
                        existing = existing[df.columns.to_list()]
                        if df.url.iloc[0] not in list(existing.url.unique()):
                            df.to_csv(args.save_path_links, header=False, mode='a')
                else:
                    pass


    else:
        print('Failed to get reviews on page {}'.format(i))



def review_parser(response, loc, args, i, total_reviews,local_name, city, current_page):
    #Parsing reviews on single page

    try:
        reviews_boxes = response.find("div", class_="LbPSX").find_all('div', class_="C") if response.find("div", class_="LbPSX") else None
        #response.find_all('div', class_='YibKl MC R2 Gi z Z BB pBbQr')
    except:
        reviews_boxes = None
        print('Cannot locate review boxes for location {}'.format(loc))
    if reviews_boxes:
        # reviews_boxes = reviews_boxes.find_all('div', class_="C")

        for num, review in enumerate(reviews_boxes):
            print('Parsing review No.{} on page {} for street {}'.format(num,i,loc))
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
            data['loc'] = loc if loc else None
            data['local_name'] = local_name
            data['city'] = city
            df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))
            df['total_reviews'] = total_reviews
            df['current_page'] = current_page
            # df['page_number'] = re.findall(r"-or(\d+)-", current_page)[0]
            df['page_number'] = i

            # review_df =pd.concat([review_df, df])
            if os.path.isdir(args.save_path) == False:
                os.makedirs(args.save_path)
            file_name = loc.replace(' ', '_')
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