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
import ast
import pandas as pd
from time import sleep
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('--incognito')  # 隐身模式（无痕模式）
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
chromdriver_path = "/Users/jie/Downloads/chromedriver1" #Replacing it with your chromdriver_path
# driver = webdriver.Chrome(executable_path=, options=options)
from bs4 import BeautifulSoup
# driver.maximize_window()
# driver = webdriver.Chrome(executable_path="/Users/jie/Downloads/chromedriver", chrome_options=options)
sleep(3)
MAX_WAIT = 20
import argparse
import math
import os
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
        help="The city or country where the streets belong to",
    )

    parser.add_argument(
        '-s',
        "--save_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap',
        help="local path where you want to save your scraped data",
    )
    parser.add_argument(
        '-option',
        "--option",
        required=True,
        type=str,
        default='street_urls',
        help="Get links to street on GoogleMap",
    )
    # parser.add_argument(
    #     '-o2',
    #     "--street_reviews",
    #     required=True,
    #     type=bool,
    #     default=True,
    #     help="Get reviews of streets",
    # )
    parser.add_argument(
        '-u',
        "--unfound_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap/unfound_streets_reviews_GoogleMap.txt',
        help="Record unfound streets or streets without reviews",
    )

    # args = parser.parse_args(args=[])
    args = parser.parse_args()#args=[]

    return args

# weblink  = 'https://www.tripadvisor.com.sg/'
import re
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
#Logging information about the founded street (url, category, address)
def log_url(index,street, local_name,url,category, address,log_street_link_file):
    if os.path.exists(log_street_link_file) == False:
        open(log_street_link_file, 'w').write('%s==%s==%s==%s==%s==%s\n' % (index,street,local_name,url,category, address))
    open(log_street_link_file, 'a').write('%s==%s==%s==%s==%s==%s\n' % (index,street,local_name,url,category, address))

#Logging unfound streets or streets without reviews
def log_unfound(street,args):
    #Check if folder exists, if not, create folder
    if os.path.isdir('/'.join(args.unfound_path.split('/')[:-1])) == False:
        os.makedirs('/'.join(args.unfound_path.split('/')[:-1]))
    #Check if file under the folder exists, if not write into new file
    if os.path.exists(args.unfound_path) == False:
        open(args.unfound_path, 'w').write('%s\n' % (street))
    open(args.unfound_path, 'a').write('%s\n' % (street))

 #Open new window for a street, record the url, and close it and return to the very first window
def get_street_link(index,street,street_name, driver,args,log_street_link_file):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://www.google.com.sg/maps')
    sleep(4)
    search = driver.find_element(By.ID,'searchboxinput')
    sleep(1)
    search.send_keys(street_name)
    sleep(4)
    # search.send_keys(Keys.RETURN)
    # sleep(5)
    # driver.find_element(By.XPATH,'//button[@id="searchbox-searchbutton"]').click()
    wait = WebDriverWait(driver, MAX_WAIT)
    #The first result
    try:
        # driver.find_element(By.XPATH,'//*[@id="searchboxinput"]').click()
        driver.find_elements(By.XPATH, '//div[@class="sbsb_c "]')[1].click()
        print('Go to the first result')
    # driver.find_elements(By.XPATH,'//div[@class="sbsb_c "]/[1]').click()
        sleep(10)
    except:
        pass
    if review_exists(driver) == False:
        print('Go the second recommended location in the drop-down list')
        search = driver.find_element(By.ID, 'searchboxinput')
        search.clear()
        sleep(4)
        search.send_keys(street_name)
        sleep(4)
        #Go the second result
        try:
            driver.find_element(By.XPATH, '//div[@class="sbsb_b"]/div[2]').click()
            sleep(4)

        except:
            pass
    # Go to the review page
    if review_exists(driver) == True:
        # Get category of the street or POI
        try:
            category = driver.find_element(By.XPATH, '//button[@class="DkEaL u6ijk"]').text
        except:
            category = None
        # Get address of the street or POI
        try:
            address = \
                driver.find_element(By.XPATH, './/div[contains(@aria-label, "Information for ")]').text.split(
                    '\n')[0]
        except:
            address = None

        # driver.find_element(By.XPATH, '//div[@class="jANrlb"]//button').click()
        # sleep(5)
        try:
            local_name = driver.find_element(By.XPATH, '//h1[class="DUwDvf fontHeadlineLarge"]').text
        except:
            local_name = None

        # log_url(index, street,local_name, driver.current_url, log_street_link_file, category, address)
        if os.path.exists(log_street_link_file) == False:
            open(log_street_link_file, 'w').write(
                '%s==%s==%s==%s==%s==%s\n' % (index, street, local_name, driver.current_url, category, address))
        open(log_street_link_file, 'a').write(
            '%s==%s==%s==%s==%s==%s\n' % (index, street, local_name, driver.current_url, category, address))
        print('Saved url link to street {}'.format(street))
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        sleep(5)

    else:
        print('No reviews')
        log_unfound(street, args)
        print('Saved unfound street for {}'.format(street))
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        sleep(5)


#check if review section exists
def review_exists(driver):

    try:
        # Go to the review page
        driver.find_element(By.XPATH, '//div[@class="jANrlb"]//button')
        # driver.find_element_by_xpath('//a[@aria-label="{}"]'.format(street)).click()
    except NoSuchElementException:
        return False
    return True
#For scrolling the reviews
def scrolling(last_review, driver):

    # last_review = driver.find_elements(By.XPATH, '//div[@jstcache="652"]')
    driver.execute_script('arguments[0].scrollIntoView(true);', last_review[-1])
    sleep(4)
    next_review = driver.find_elements(By.XPATH, '//div[contains(@data-review-id,"C")]')
    return next_review

def scrapy(url,street,args,driver,existing_streets_num=0):
    #Open one window for a street link and then close it and return to the very first window
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    sleep(3)
    driver.get(url)
    sleep(4)
    wait = WebDriverWait(driver, MAX_WAIT)

    try:
        local_name = driver.find_element(By.XPATH, '//h1[class="DUwDvf fontHeadlineLarge"]').text
    except:
        local_name = None
    total_reviews = int(driver.find_element(By.XPATH,'.//div[@class="skqShb"]').text.split('\n')[1].split(' reviews')[0].replace(',','')) if driver.find_element(By.XPATH,'.//div[@class="skqShb"]').text.split('\n')[1].split(' reviews')[0].replace(',','') else driver.find_element(By.XPATH,'.//div[@class="skqShb"]').text
    total_rating = driver.find_element(By.XPATH, './/div[@class="skqShb"]').text.split('\n')[0] if total_reviews else None
    category = driver.find_element(By.XPATH, './/div[@class="skqShb"]').text.split('\n')[-1] if total_reviews and len(driver.find_element(By.XPATH, './/div[@class="skqShb"]').text.split('\n')) > 2 else None
    # Go to review section
    try:
        driver.find_element(By.XPATH, './/span[contains(@aria-label, "reviews")]').click()
        sleep(4)
    except:
        pass
    try:
        morereviews = driver.find_elements(By.XPATH,'//span[contains(text(), "More reviews")]')
        sleep(3)
        morereviews.click()
        print('Clicked "More reviews"')
        sleep(5)
    except:
        pass
    #Expand reviews
    try:
        seemores= driver.find_elements(By.XPATH,'.//button[@aria-label=" See more "]')
        for seemore in seemores:
            seemore.click()
            print('Clicked "See more"')
            sleep(2)
    except:
        pass
    #Expand picture collections
    try:
        picturesmores = driver.find_elements(By.XPATH, './/div[@class="KtCyie"]/button[@data-photo-index="3"]')
        for pic in picturesmores:
            try:
                pic.click()
                sleep(5)
            except:
                pass
    except:
        pass

    #initialize last_review variale for scrolling
    last_review = driver.find_elements(By.XPATH, '//div[contains(@data-review-id,"C")]')
    # Get page_source and extract texts
    response = BeautifulSoup(driver.page_source, 'html.parser')
    review_parser(response, street, args,total_reviews,total_rating,category,local_name)
    # Scrolling to get new boxes
    count =0
    Scrolling = True
    page=0
    while Scrolling:
        next_review = scrolling(last_review,driver)
        page += 1
        print('Going to next page {}'.format(page))
        if last_review[-1].text != next_review[-1].text:
            #Get page_source and extract texts
            response = BeautifulSoup(driver.page_source, 'html.parser')
            review_parser(response,street,args,total_reviews,total_rating,category,local_name)
            last_review = next_review
            sleep(5)
        else:
            count += 1
            if count >= 3:
                Scrolling = False
                print('No more reviews')
                sleep(5)
                break


    driver.close()
    driver.switch_to.window(driver.window_handles[0])

#Parsing the reviews
def review_parser(response,street,args,total_reviews,total_rating,category,local_name):
    reviews_boxes = response.find_all("div",attrs={"data-review-id": True})
    for num, box in enumerate(reviews_boxes):
        # print(num)
        # box = reviews_boxes[1]
        # print(num,box.find("div",class_='d4r55').text.strip())
        data = {}
        data['review_id'] = box['data-review-id']
        data['user'] = box.find("div",class_='d4r55').text.strip() if box.find("div",class_='d4r55') else None
        data['guide'] = box.find("div", class_='RfnDt').find_all('span')[0].text if box.find("div", class_='RfnDt') else None
        data['review_text'] = box.find("span", class_='wiI7pd').text if box.find("div", class_='wiI7pd') else None
        data['review_date'] = box.find('span',class_='rsqaWe').text if box.find('span',class_='rsqaWe') else None
        try:
            data['review_rating'] = box.find('span', attrs={'aria-label': re.compile('stars')})['aria-label'].strip().split(' star')[0] if box.find('span', attrs={'aria-label': re.compile('stars')})['aria-label'].strip().split(' star')[0] != 'stars' else box.find('span', class_='fzvQIb').text
        except:
            data['review_rating'] = None
        pictures = box.find("div", class_='KtCyie').find_all('button') if box.find("div", class_='KtCyie') else None
        picture_urls = []
        if pictures:
            try:
                for ind, pic in enumerate(pictures):
                    # print('pic:',ind)
                    if re.search('\(.*?http.*?\)', pic['style'])[0]:
                        picture_urls.append(re.search('\(.*?http.*?\)', pic['style'])[0])
                data['picture_urls'] = ','.join([ast.literal_eval(url) for url in picture_urls])
            except:
                data['picture_urls'] = None

        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
        df['total_reviews'] = total_reviews
        df['total_rating'] = total_rating
        df['category'] = category
        df['street'] = street
        df['local_name'] = local_name

        # review_df =pd.concat([review_df, df])

        file_name = street.replace(' ', '_')
        if os.path.isfile(args.save_path + '/{}.csv'.format(file_name)) == False:
            df.to_csv(args.save_path + '/{}.csv'.format(file_name))
        else:
            existing = pd.read_csv(args.save_path + '/{}.csv'.format(file_name))
            existing = existing[df.columns.to_list()]
            if df.review_id.iloc[0] not in list(existing.review_id.unique()):
                df.to_csv(args.save_path + '/{}.csv'.format(file_name), header=False, mode='a')
def main():
    os.chdir('/Users/jie/UrbanText')
    print('Current root directory: ', os.getcwd())
    args = parse_arguments()
    streets_df = pd.read_csv(args.file_path)
    streets = list(streets_df.Street.unique())
    if os.path.isdir(args.save_path) == False:
        os.makedirs(args.save_path)
    log_street_link_file = args.save_path+'/street_link_file_GoogleMap.txt'
    print('City:', args.city)
    print('Save path:', args.save_path)
    print('File path:', args.file_path)
    print('File path:', args.unfound_path)
    print('log_street_link_file', log_street_link_file)
    # print('Getting streets that have been scraped...')
    # csv_files = glob.glob(args.save_path + '/*.csv')
    # all_df = concat(csv_files)
    # print('Dataframe columns of scraped files:', all_df.columns)
    # scraped_streets = list(all_df.street.unique())
    # streets_toscrape = [street for street in streets if street not in scraped_streets]
    # print('Need to scrape data for {} streets'.format(len(streets_toscrape)))
    ser = Service(r"{}".format(chromdriver_path))
    driver = webdriver.Chrome(service=ser, options=options)
    sleep(1)
    driver.get('https://www.google.com.sg/maps')
    if os.path.isdir(args.save_path) == False:
        os.makedirs(args.save_path)
    exsiting_streets = []
    if args.option == 'street_urls':
        print(args.street_url)
        #if run before, open logged street records and remove them
        if os.path.exists(log_street_link_file)==True:
            with open(log_street_link_file) as f:
                lines = f.readlines()
            exsiting_streets += [line.split('==')[1] for line in lines]
            exsiting_streets = list(set(exsiting_streets))
            streets_toscrape = [street for street in streets if street not in exsiting_streets]
        #if scraping the street links before and also failed, remove the records as well
        if os.path.exists(args.unfound_path)==True:
            with open(args.unfound_path) as f:
                lines = f.readlines()
            exsiting_streets += [line.split('\n')[0] for line in lines]
            exsiting_streets = list(set(exsiting_streets))
            streets_toscrape = [street for street in streets if street not in exsiting_streets]
        # Scrapy all the street review page url
        else:
            streets_toscrape = streets

        print('Need to scrape data for {} streets.'.format(len(streets_toscrape)))

        for i, street in enumerate(streets_toscrape):
            street_name = street + ', ' + args.city
            get_street_link(i,street, street_name,driver,args,log_street_link_file)
    if args.option == 'street_reviews':
        ser = Service(r"{}".format(chromdriver_path))
        driver = webdriver.Chrome(service=ser, options=options)
        with open(log_street_link_file) as f:
            lines = f.readlines()
        streets = [line.split('==')[1] for line in lines]
        # local_names = [line.split('==')[2] for line in lines]
        streets_urls = [line.split('==')[3] for line in lines]
        print('Check if any scraped data saved locally.')
        csv_files = glob.glob(args.save_path + '/*.csv')
        if len(csv_files) !=0:
            print('Getting streets that have been scraped...')
            all_df = concat(csv_files)

            for street,url in zip(streets,streets_urls):
                # if street not in existing_streets:
                print(street)
                existing_streets_num = all_df[all_df.street == street].count()[0]
                if existing_streets_num < int(all_df[all_df.street == street].total_reviews.iloc[-1])-10:
                    scrapy(url,street,args,driver,existing_streets_num=existing_streets_num)
                else:
                    continue
        else:
            print('Strating scrapying from scratch...')
            for street, url in zip(streets, streets_urls):
                print(street)
                scrapy(url, street, args, driver,existing_streets_num=0)

    # driver.get('https://www.tripadvisor.com.sg/')

    wait = WebDriverWait(driver, MAX_WAIT)
    # print('Please click the searching box in 5 seconds!!')
    sleep(5)


if __name__ =='__main__':
    main()