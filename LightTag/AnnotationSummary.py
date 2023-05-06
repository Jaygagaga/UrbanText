import pandas as pd
import json
import os
import argparse
from pprint import pprint
from nltk.stem.snowball import SnowballStemmer
snowBallStemmer = SnowballStemmer("english")






def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r',
        "--root_directory",
        required=True,
        type=str,
        default='/Users/jie/UrbanText',
        help="Specify your root directory",
    )
    parser.add_argument(
        '-f',
        "--data_path",
        required=True,
        type=str,
        default='./Data/Anntated_data/',
        help="Local path where you put downloaded LightTag annotations",
    )
    parser.add_argument(
        '-a',
        "--save_annotations",
        required=True,
        type=str,
        default='./Data/Anntated_data/BishanParkAnnotations.csv',
        help="Local path where you want to save parsed annotations",
    )
    parser.add_argument(
        '-s',
        "--save_summary",
        required=True,
        type=str,
        default='./Data/Anntated_data/BishanParkAnnotationsSummary.csv',
        help="Local path where you want to save parsed annotation summary",
    )
    args = parser.parse_args()#args=[]

    return args

def parse_json(example):
    data = pd.DataFrame(columns = ['content', 'example_id','tag','token','token_index', 'reviewed','annotator', 'tag_id'])

    num_annotations = len(example['annotations'])
    print('Content: ', example['content'])
    print('This example has {} annotations'.format(num_annotations))
    content= [example['content']]
    example_id =[example['example_id']]

    tags = []
    tokens = []
    token_index = []

    revieweds =[]
    annotators = []
    tag_ids = []

    for num, annotation in enumerate(example['annotations']):
        print('-----Parsing annotations No. {}'.format(num))
        tags.append(parse_annotations(annotation)[0][0])
        tokens.append(parse_annotations(annotation)[0][1])
        token_index.append(parse_annotations(annotation)[0][1])

        revieweds.append(parse_annotations(annotation)[1])
        annotators.append(parse_annotations(annotation)[2])
        tag_ids.append(parse_annotations(annotation)[3])
    df = pd.DataFrame(list(zip(content * num_annotations, example_id * num_annotations,tags, tokens,
                               token_index,revieweds,annotators,tag_ids)),
                      columns=['content', 'example_id','tag','token','token_index', 'reviewed','annotator', 'tag_id'])
    return df

def parse_annotations(annotation):
    # token_index = ()
    tag = annotation['tag']
    tag_id = annotation['tag_id']
    token = annotation['value']
    token_index = (annotation['start'], annotation['end'])
    reviewed = annotation['reviewed']
    annotator = ', '.join([a['annotator'] if a['annotator'] else 'None' for a in annotation['annotated_by']])
    return ((tag, token, token_index),reviewed,annotator,tag_id)
def analysis(df):
    category_frequency =df.groupby(['category'])['token_index'].count().reset_index().rename(columns ={'token_index':'category_frequency'})
    tag_frequency =df.groupby(['tag'])['token_index'].count().reset_index().rename(columns ={'token_index':'tag_frequency'})
    token_frequency = df.groupby(['tag','token'])['token_index'].count().reset_index().rename(columns ={'token_index':'token_frequency'})
    df_subset = df[['tag', 'category']]
    token_frequency= token_frequency.merge(df_subset,how = 'left', on = 'tag')
    token_frequency = token_frequency.merge(category_frequency, how='left', on='category')
    token_frequency = token_frequency.merge(tag_frequency, how='left', on='tag')
    token_frequency = token_frequency[['category','category_frequency','tag','tag_frequency', 'token','token_frequency']]
    token_frequency=token_frequency[token_frequency.token!=' ']
    # token_frequency['token_freq_tuples'] = tuple(zip(token_frequency.token, token_frequency.token_frequency))
    token_frequency = token_frequency.drop_duplicates(['token','category','tag'])
    return token_frequency
cross_tag_dict = {}
#key: token, value:[tag1,tag2]
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
def border_interect_condition_2(string1, string2):
    assert len(string1.split())==2
    assert len(string2.split())==2

    if len(intersection(string1.split(),string2.split())) >=1:
        return True
    else:
        return False


def border_interect_condition_more(string1, string2):
    assert len(string1.split()) >= 3
    assert len(string2.split()) >= 3
    # print(string1.split(), string2.split())
    if len(intersection(string1.split(), string2.split())) >= 2:
        return True
    else:
        return False

def embed_condition(string1, string2):
    longer_string = string1 if len(string1) > len(string2) else string2
    shorter_string = string1 if len(string1) < len(string2) else string2
    try:
        longer_string.index(shorter_string)
        return True
    except ValueError:
        return False
def add2dic(token,token_tag, another_token, dic,df):
    if token not in dic:
        print('token_tag',token_tag)
        option = [(another_token,tag) for tag in list(df[df.stemmed_token == another_token].tag.unique()) if tag != token_tag]
        print('option',option)
        if len(option) != 0:
            dic[token] = option
    else:
        if not any(x in list(df[df.stemmed_token == another_token].tag.unique()) for x in
                dic[token]):
            option = [(another_token,tag) for tag in list(df[df.stemmed_token == another_token].tag.unique()) if tag != token_tag]
            if len(option) != 0:
                dic[token] += option
                dic[token] = list(set(dic[token]))
    return dic
def stemming(string_list):
    stemmed = ' '.join([snowBallStemmer.stem(j) for j in string_list.split()])
    return stemmed
import glob


def main():

    args = parse_arguments()
    os.chdir(args.root_directory)
    print('Current root directory: ', os.getcwd())
    """Reading all annotation json files downloaded from Light tag and parsing them into dataframe
       dataframe columns:
       'content': the original review text
       'example_id': index to the review text defined in LightTag's way
       'tag': tag out of 54 labels we have
       'token': word/phrased that are selected for the tag
       'token_index': the start and end index of the token (word/phrase)
       'reviewed': True or False (if confusions have been solved or annotations confirmed)
       'annotator': individual
       'tag_id': index to tag
    """
    json_files = glob.glob(args.data_path+'/*.json') #
    all_df =  pd.DataFrame(columns = ['content', 'example_id','tag','token','token_index', 'reviewed','annotator', 'tag_id'])
    for file in json_files:
        with open(file, 'r') as json_file:
            annotated = json.load(json_file)
            for num, example in enumerate(annotated['examples']):
                print('Parsing example No. {}'.format(num))
                df = parse_json(example)
                all_df= pd.concat([all_df,df])
    all_df['category'] = all_df['tag'].map(lambda x: x.split('_')[0])
    print('Save parsed dataframe')
    all_df.to_csv(args.save_annotations)

    """Annotation analysis
       1. tag_frequency
       2. token_frequency
       3. category_frequency
       4. tag_confusion 
    """

    summary = analysis(all_df)

    print('Stemming tokens')
    summary['stemmed_token'] = summary.token.map(lambda x: stemming(x) if x else None)
    summary['index'] = range(0, len(summary))


    print('Capture high frequency tokens (more than 2 times)')
    token_high_freq = {token:freq  for token, freq in summary['stemmed_token'].value_counts().to_dict().items() if freq > 1 }

    # print('Create a dictionary of high frequently appeared tokens and its indices in the dataframe')
    length_token_dict = {}
    for token in summary['stemmed_token'].unique():
        length = len(token.split())
        if length not in length_token_dict:
            length_token_dict[length] = [token]
        else:
            length_token_dict[length] += [token]

    token_tags_exact = {}
    # 1. First level of confusion: exact match and exact confusion (same span and same token)
    for token in token_high_freq.items():
        if len(summary[summary.stemmed_token == token].tag.unique()) >1:
            if token not in token_tags_exact:
                token_tags_exact[token] = summary[summary.stemmed_token == token].tag.unique().to_list()
    # 2. Second level of confusion: boundary intersection (2 tokens case)
    token_tags_inter_2 = {}
    token_tags_inter_more = {}
    same_length_tokens_2 = length_token_dict[2]
    same_length_tokens_more = set(list([i for sub in [v for k, v in length_token_dict.items() if k > 2] for i in sub]))
    for i in range(len(summary)):
        print('Check confusion cases for token No. {} (2 tokens case)'.format(i))
        token = summary.stemmed_token.iloc[i]
        tag =  summary.tag.iloc[i]
        if len(token.split()) ==2:
            for another_token in [t for t in same_length_tokens_2 if t != token]:
                if border_interect_condition_2(token,another_token):
                    token_tags_inter_2= add2dic(token, tag,another_token, token_tags_inter_2, summary)

        # Second level of confusion: boundary intersection (2 tokens case)
        if len(token.split()) >2:
            print('Check confusion cases for token No. {} (more tokens case)'.format(i))
            for another_token in [t for t in same_length_tokens_more if t != token]:
                # print(token,another_token)
                if border_interect_condition_more(token,another_token):
                    token_tags_inter_more = add2dic(token, tag,another_token, token_tags_inter_more, summary)


    # 3. Third level of confusion: embedd tokens
    # token_tags_3 = {}
    # for i in range(len(summary)):
    #     print('Check confusion cases for token No. {}'.format(i))
    #     token = summary.stemmed_token.iloc[i]
    #     another_tokens =summary[summary.stemmed_token != token].stemmed_token.to_list()
    #     for another_token in another_tokens:
    #         if embed_condition(another_token, token):
    #             token_tags_3 = add2dic(token, another_token, token_tags_3, summary)
    print('Add other tag options if exist to dataframe')
    summary['similar_tokens_2'] = None
    summary['similar_tags_2'] = None
    summary['similar_tokens_more'] = None
    summary['similar_tags_more'] = None
    summary['other_tag_option_exact'] = None
    for token,option in token_tags_inter_2.items():
        print(token, option)
        # similar_tokens = [i[0] for i in option]
        # similar_tags = [i[1] for i in option]
        summary.loc[summary.stemmed_token==token, 'similar_tokens_2'] =', '.join([i[0] for i in option])
        summary.loc[summary.stemmed_token == token, 'similar_tags_2'] = ', '.join([i[1] for i in option])
    for token,option in token_tags_inter_more.items():
        summary.loc[summary.stemmed_token == token, 'similar_tokens_more'] =', '.join([i[0] for i in option])
        summary.loc[summary.stemmed_token == token, 'similar_tags_more'] = ', '.join([i[1] for i in option])
    if token_tags_exact:
        for token,option in token_tags_exact.items():
            summary.loc[summary.stemmed_token == token, 'other_tag_option_exact'] = ', '.join(option)
    print('Save annotation summary')
    summary.to_csv(args.save_summary)










if __name__ == '__main__':
    main()




