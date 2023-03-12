import pandas as pd
import argparse
import os
import glob
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

    # parser.add_argument(
    #     '-s1',
    #     "--save_path_links",
    #     required=True,
    #     type=str,
    #     default='./Data/Reviews/TripAdvisor/loc_reviews/loc_links_Wuhan.csv',
    #     help="local path where you want to save your scraped data",
    # )
    parser.add_argument(
        '-s',
        "--save_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap/all_reviews.csv',
        help="local path where you want to save your processed and combined dataset",
    )
    # parser.add_argument(
    #     '-u',
    #     "--unfound_path",
    #     required=True,
    #     type=str,
    #     default='./Data/Reviews/TripAdvisor/unfound_POIs_reviews_TripAdvisor.txt',
    #     help="Record unfound streets or streets without reviews",
    # )
    # parser.add_argument(
    #     '-ff',
    #     "--found_path",
    #     required=True,
    #     type=str,
    #     default='./Data/Reviews/TripAdvisor/found_POIs_reviews_TripAdvisor.txt',
    #     help="local path where you record streets with complete reviews.",
    # )
    # parser.add_argument(
    #     '-option',
    #     "--option",
    #     required=True,
    #     type=str,
    #     default='street_urls',
    #     help="Get links to street on GoogleMap",
    # )
    # args = parser.parse_args(args=[])
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



def main():
    args = parse_arguments()
    os.chdir(args.root_directory)
    print('Current root directory: ', os.getcwd())
    print('Reading and concatenating all street reviews in {}'.format(args.file_path))
    csv_files =  glob.glob(args.file_path + '/*.csv')
    reviews_df = concat(csv_files)
    reviews_df = reviews_df.drop_duplicates('review_id')
    print('Total number of review texts is {}'.format(len(reviews_df)))

    content = reviews_df.review_text.map(lambda x: correct_space(x)[0])
    reviews_df['review_text'] = content
    reviews_df['word_length'] =reviews_df.review_text.map(lambda x: correct_space(x)[1])
    reviews_df = reviews_df[reviews_df['word_length']>2]
    print('Total number of reviews with texts longer than 2 words is {}'.format(len(reviews_df)))
    reviews_df.to_csv(args.save_path)

if __name__ == '__main__':
    main()


