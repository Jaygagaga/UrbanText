import shutil

import pandas as pd
import argparse
import os
import glob

def save_zip(df, zip_path):
    compression_options = dict(method='zip', archive_name=f'{zip_path}.csv')
    df.to_csv(f'{zip_path}.zip', compression=compression_options)
def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        "--file_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap',
        help="Local path where scraped reviews are",
    )

    parser.add_argument(
        '-r',
        "--root_directory",
        required=True,
        default='/Users/jie/UrbanText',
        help='Root directory of the project',
    )

    parser.add_argument(
        '-s',
        "--save_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap/all_reviews',
        help="local path where you want to save your processed and combined dataset",
    )
    parser.add_argument(
        '-e',
        "--extension",
        required=True,
        type=str,
        default='csv',
        help="file extension",
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
from nltk.tokenize import WordPunctTokenizer
text = "Reset your password; if you just can't remember your old one?"



def correct_space(doc):
    tokens = WordPunctTokenizer().tokenize(doc)
    lens = len(tokens)
    new_sent = ''
    for token in tokens:
        if token != "'":
            new_sent += token + ' '
        else:
            new_sent +=token
    return new_sent, lens
import zipfile


def main():
    args = parse_arguments()
    os.chdir(args.root_directory)
    print('Current root directory: ', os.getcwd())
    print('Reading and concatenating all street reviews in {}'.format(args.file_path))
    if 'zip' in args.file_path:
        reviews_df = pd.DataFrame()
        with zipfile.ZipFile(args.file_path) as z:
            for filename in z.namelist():
                if'__MACOSX' not in filename and filename.split('/')[-1] != '':
                    try:
                        df = pd.read_csv(z.open(filename),encoding="utf-8")
                        reviews_df = pd.concat([reviews_df, df])
                    except:
                        print('Cannot open file {}'.format(filename))
    else:
        csv_files =  glob.glob(args.file_path + '/*.csv')
        reviews_df = concat(csv_files)
    reviews_df = reviews_df.drop_duplicates('review_id')
    print('Total number of review texts is {}'.format(len(reviews_df)))
    reviews_df.review_text = reviews_df.review_text.astype(str)
    content = reviews_df.review_text.map(lambda x: correct_space(x)[0])
    reviews_df['review_text'] = content
    reviews_df['word_length'] =reviews_df.review_text.map(lambda x: correct_space(x)[1])
    reviews_df = reviews_df[reviews_df['word_length']>2]
    print('Total number of reviews with texts longer than 2 words is {}'.format(len(reviews_df)))
    if args.extension == 'zip':
        save_zip(reviews_df, args.save_path)
    if args.extension == 'csv':
        reviews_df.to_csv(args.save_path)
    print('Saved processed csv file in {}'.format(args.save_path))

if __name__ == '__main__':
    main()


