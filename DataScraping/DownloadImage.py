import re
#Setting up selenium webdriver
import shutil
import os
import glob
import pandas as pd
from time import sleep

sleep(3)
MAX_WAIT = 20
import argparse
import math
import os
import requests
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
        default='./Data/Reviews/TripAdvisor',
        help="Local path where you put street reviews",
    )
    parser.add_argument(
        '-i',
        "--image_save_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/images',
        help="Local path where you put review images",
    )
    parser.add_argument(
        '-u',
        "--unfound_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/images/unfound_images.txt',
        help="Record unfound images by review id",
    )
    parser.add_argument(
        '-ff',
        "--found_path",
        required=True,
        type=str,
        default='./Data/Reviews/TripAdvisor/images/found_images.txt',
        help="local path where you record images with review id",
    )
    args = parser.parse_args()#args=[]

    return args


def concat(csv_files):
    all_ = pd.DataFrame()
    for i in range(len(csv_files)):
        try:
            df = pd.read_csv(csv_files[i], encoding="utf-8")
            # df['keyword'] = csv_files[i].split('/')[-1].split('.')[0].split('_')[-1]
            all_ = all_.append(df)
        except:
            continue
    return all_


def main():
    os.chdir('/Users/jie/UrbanText')
    print('Current root directory: ', os.getcwd())
    args = parse_arguments()
    print('File path:', args.file_path)
    print('Reading all reviews in the folder')
    csv_files = glob.glob(args.file_path+'/*.csv')
    review_df = concat(csv_files)

    review_df =review_df.drop_duplicates(['review_id','review_text'])
    print('Total reviews: {}'.format(len(review_df)))
    review_df.picture_url =review_df.picture_url.astype(str)
    review_df = review_df.where(pd.notnull(review_df), None)
    review_with_pic = review_df[(review_df.picture_url.isnull()==False) & (review_df.picture_url != 'nan')]

    for num, urls in enumerate(review_with_pic.picture_url):
        urls_ = urls.split(',')
        id = review_with_pic.review_id.iloc[num] + '$$' + '_'.join(review_with_pic.review_date.iloc[num].split())
        for i, url in enumerate(urls_):
            try:
                response = requests.get(url, stream=True)
                id_ = id+'_{}'.format(i)
                if os.path.isdir(args.image_save_path) == False:
                    os.makedirs(args.image_save_path)
                with open('./Data/Reviews/TripAdvisor/images/{}.png'.format(id_), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                log_found(id_, args)
            except:
                log_unfound(id_,args)
            # driver.get(url)
            #
            # sleep(5)
            # image = driver.find_element(By.TAG_NAME,'img').get_attribute('src')
            # urllib.urlretrieve(image, id)

import urllib3


if __name__ =='__main__':
    main()