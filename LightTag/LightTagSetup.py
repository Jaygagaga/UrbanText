from collections import defaultdict

import requests
import json
import pandas as pd
from pprint import pprint
from requests.auth import HTTPBasicAuth
from LightTag.ltsession import LTSession
import glob
import argparse
import math
import os
from nltk.stem.snowball import SnowballStemmer
snowBallStemmer = SnowballStemmer("english")
from nltk import word_tokenize
# from flair.data import Sentence
# from flair.models import SequenceTagger
import spacy
import re
import ast
# big_nlp = spacy.load("en_core_web_lg") # Load the big spacy model
#Load the small spacy model

#
# schema = session.get('v1/projects/default/schemas/').json() #Use the slug of the schema to fetch it from the schemas endpoint
# allTasks = session.get('v1/projects/default/task_definitions').json()
# for t in allTasks:
#     if t['active'] == True:
#         print(t)
# my_task_name = "another"
# my_task = next(filter(lambda task: task['name'] == my_task_name,allTasks))
# my_task_models = my_task['suggestion_models']
# my_task_models.append(model['id']) # Add the id of the model you created to this task



# urban_design_term_path = '../Data/Helpers/design_dictionary_eng.txt'
# path = '../Data/Helpers'
def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        "--helper_path",
        required=True,
        type=str,
        default='./Data/Helpers',
        help="Local path where you put keywords lists",
    )
    parser.add_argument(
        '-r',
        "--reformat_dict",
        required=True,
        type=int,
        default=0,
        help="Whether to reformat the keyword dictionaries",
    )
    parser.add_argument(
        '-j',
        '--suggestion_json_path',
        required = True,
        type = str,
        default= './LightTag/NER_suggestions.json',
        help = 'The path where you put NER model suggestions as json file'
    )

    # args = parser.parse_args(args=[])
    args = parser.parse_args()#args=[]

    return args
#

# old2newid = {re.split('\t| ',i)[0]:re.split('\t| ',i)[-1] for i in smell_term[1:18]}


# head = [smell_term[0]] +[re.split('\t| ',i)[-1] + '\t' + re.split('\t| ',i)[1] for i in smell_term[1:18]] + [smell_term[18]]
combined = []
# for line in smell_term[19:]:
#     if len(line.split('\t'))>1 and ',' not in line.split('\t')[-1]:
#         combined.append(line.split('\t')[0]+'\t'+old2newid[line.split('\t')[1]])
#     if len(line.split('\t')) > 1 and ',' in line.split('\t')[-1]:
#         for id in ast.literal_eval(line.split('\t')[-1]).split(','):
#             combined.append(line.split('\t')[0] + '\t' + old2newid[id])

# term101 = [i.lower()+'\t'+'201' for i in design_term[8:17]]
# term102 = [i.lower()+'\t'+'202' for i in design_term[19:35]]
# term103 = [i.lower()+'\t'+'203' for i in design_term[37:43]]
# term104 = [i.lower()+'\t'+'204' for i in design_term[45:55]]
# term105 = [i.lower()+'\t'+'205' for i in design_term[57:59]]
#
# with open('/Users/jie/UrbanText/Data/Helpers/smell_dictionary_eng_.txt', 'w') as f:
#     for term in head+combined:
#         f.write(f"{term}\n")

class ReformatDict(object):
    def __init__(self):
        pass
        # self.dict_path = dict_path
        # self.save_path = save_path
        # self.coding = coding
    @staticmethod
    def indices(lst, item):
        return [i for i, x in enumerate(lst) if x == item]
    @staticmethod
    def creat_label_dict(path):
        with open(path, 'r') as f:
            dic = [l.replace('\n', '') for l in f.readlines()]
        return dic

    def reformat_dic(self, dict_path, save_path, coding):
        act_term = self.creat_label_dict(dict_path)
        category_indices = self.indices(act_term, '%')
        head = [act_term[category_indices[0]]] +[re.split('\t| ',i)[0] + '\t' + re.split('\t| ',i)[1] for i in act_term[category_indices[0]+1:category_indices[1]]] + [act_term[category_indices[0]]]
        ids = []
        print('Head:', head)
        for k in coding:
            print('category id {} lies in line No.{}'.format(k, act_term.index(k)))
            ids.append(act_term.index(k))
        assert len(coding) == len(ids), "The numbers of category ids does not match"
        terms = []
        for i in range(len(ids)-1):
            print(ids[i], ids[i+1])
            term = [j.lower() + '\t' + coding[i] for j in act_term[ids[i]+1:ids[i+1]-1]]
            print(term)
            terms+= term
        with open(save_path, 'w') as f:
            for term in head+terms:
                f.write(f"{term}\n")
        print('Finshed reformating dictionaries')




# term101 = [i.lower()+'\t'+'401' for i in act_term[12:17]]
# term102 = [i.lower()+'\t'+'402' for i in act_term[16:35]]
# term103 = [i.lower()+'\t'+'403' for i in act_term[30:43]]
# term104 = [i.lower()+'\t'+'404' for i in act_term[39:55]]
# term105 = [i.lower()+'\t'+'405' for i in act_term[48:59]]
# term105 = [i.lower()+'\t'+'405' for i in act_term[56:59]]
# term105 = [i.lower()+'\t'+'405' for i in act_term[59:59]]
# term105 = [i.lower()+'\t'+'405' for i in act_term[62:59]]
import re
"""Model 1: using dictionaries as look-up tables"""
dict_with_levels = ['smell_dictionary_eng.txt','design_dictionary_eng.txt']
class ConfigDict(object):
    def __init__(self, helper_path=None,dict_with_levels=None, dictname2tagname=None):
        """
        :param helper_path: path to dictionaries
        :param dict_with_levels: the names of dictionaries that contain multi levels of categories
        """
        if helper_path:
            self.helper_path = helper_path
        if dict_with_levels:
            self.dict_with_levels = dict_with_levels
        if dictname2tagname:
            self.dictname2tagname = dictname2tagname
    @staticmethod
    def indices(lst, item):
        return [i for i, x in enumerate(lst) if x == item]

    def concat(self, txt_files): #concate all dictionaries into a dictionary data format
        all_dict = {}
        for file in txt_files:
            if file.split('/')[-1] in self.dict_with_levels: #check if dictionaries contains multi levels of categories
                category2id = {}
                category_tems_dcit = {}
                with open(file, 'r') as f:
                    lines = [re.sub(r'\n', '',l)for l in f.readlines()]
                    lines = [l for l in lines if l != '']
                    category_indices = self.indices(lines,'%')
                    # line = f.readline()
                for num, line in enumerate(lines):
                    # print(num, line)
                    if num+1 < category_indices[1] and len(line.split('\t'))>1:
                        category_id = line.split('\t')[0].lower()
                        category_name = line.split('\t')[1].lower()
                        category2id[category_name] = category_id
                        # print(category2id)
                    else:
                        if len(line.split('\t'))>1 and ',' not in line.split('\t')[-1]:
                            if line.split('\t')[1] not in category_tems_dcit:
                                category_tems_dcit[line.split('\t')[1]] = [line.split('\t')[0]]
                                # print(category_tems_dcit)
                            else:
                                category_tems_dcit[line.split('\t')[1]] += [line.split('\t')[0]]
                                # print(category_tems_dcit)
                        if len(line.split('\t')) > 1 and ',' in line.split('\t')[-1]:
                            for id in ast.literal_eval(line.split('\t')[-1]).split(','):
                                if id not in category_tems_dcit:
                                    category_tems_dcit[id] = [line.split('\t')[0]]
                                else:
                                    category_tems_dcit[id] += [line.split('\t')[0]]
                combined_dict = {}
                for key, term in category2id.items():
                    combined_dict[key] = (term, category_tems_dcit[term])
                all_dict[file.split('/')[-1].split('.')[0]] = combined_dict
            else:
                with open(file, 'r') as f:
                    lines = f.readlines()
                    terms = [l.replace('\n','').lower() for l in lines if l != '\n']
                    # terms = [l for l in lines if l != '']
                if file.split('/')[-1].split('.')[0] in self.dictname2tagname:
                    all_dict[file.split('/')[-1].split('.')[0]] = (self.dictname2tagname[file.split('/')[-1].split('.')[0]],terms)
        return all_dict
    # def simple_keys(self,dic):
    #     simple_names = {k: v for k, v in zip(list(dic.keys()),
    #                           [key.split('_')[0] for key in dic.keys()])}
    #     new_dict = {}
    #     for key, value in dic.items():
    #         if simple_names[key] in new_dict:
    #             new_dict[simple_names[key]] = value
    #
    #     return new_dict


class ConfigModels(object):
    def __init__(self, examples, dictionaries):
        self.dictionaries = dictionaries
        self.examples = examples
        self.small_nlp = spacy.load("en_core_web_sm")

    def stanford_to_lighttag_format(self, example:dict, ent):
        preWhiteSpace = re.compile('^\s+')
        '''
        Takes a LightTag example and a stanford entitty and returns a LightTag Suggestion
        '''
        match = preWhiteSpace.search(example['content'])
        offset = match.end(0) if match else 0  # CORENLP strips whitespaces so we use that regex to adjust offsets
        start = ent["characterOffsetBegin"] + offset
        end = ent["characterOffsetEnd"] + offset
        return {
            "example_id": example["id"],
            "start": start,
            "end": end,
            "tag": ent["ner"],
            "value": example['content'][start:end]
            #                     "tag_id":tagMap[sug["ner"]]
        }

    @staticmethod
    def spacyToSug(example:dict, ent):
        return {
            "example_id": example["id"],
            "start": ent.start_char,
            "end": ent.end_char,
            "tag": ent.label_,
            "value": example['content'][ent.start_char:ent.end_char]

        }

    # @staticmethod
    def process_with_spacy_small(self, example:dict):

        results = []
        doc = self.small_nlp(example['content'])
        for ent in doc.ents:
            results.append(self.spacyToSug(example, ent))
        return results

    def process_with_stanford(self, example):
        '''
        Need to run {java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "ner" -port 9000 -timeout 30000} under directory {stanford-corenlp-4.5.3}
        Gets a LightTag example, runs coreNLP on it and returns a list of suggestions in LightTag format
        '''
        results = []
        # This is the URL of the CORENLP server running in a docker container
        url = 'http://localhost:9000/?properties={"annotators":"ner","outputFormat":"json"}'
        txt = example['content'].encode('utf8')  # We need to send it bytes

        data = requests.post(url, data=txt).json()  # Send to the container
        cursor = -1  # Track the last position of a corenlp annotation, so we can ignore overlapping
        for sentence in data['sentences']:  # Corenlp does sentence parsing as well, which we dont care about

            for entity in sentence["entitymentions"]:  # iterate over the entities
                sug = self.stanford_to_lighttag_format(example, entity)  # covert stanford entitiy to lighttag format
                if sug['start'] > cursor:  # don't accept overlaps
                    results.append(sug)
                    cursor = sug['end']
        return results  # The list of lighttag suggestions

    def process_with_dict(self, example:dict):
        """

        :param
               example: dict of LightTag example, keys: example_id, content,,,
               dictionaries: {dict_name1:
                                       {tag_name: (tag_id, [item1,item2,,])},
                              dict_name2:
                                       (tag_name: [item1,item2,,,])
                              }
        :return:
               list of suggestion objects, one object for one entity; one list for one exmaple/text
        """
        content = example['content']
        lens = len(content.split())
        tokens = content.split()
        suggestions = []

        for token in tokens:
            for dict_name, term_dicts in self.dictionaries.items():
                if type(term_dicts) == tuple:
                    if snowBallStemmer.stem(token) in term_dicts[1]:
                        start = content.index(token)
                        end = start + len(token)
                        text = content[start:end]
                        suggestion = {
                            'example_id': example['id'],
                            'start': start,
                            'end': end,
                            'tag': term_dicts[0],
                            'text': text
                        }
                        if suggestion not in suggestions:
                            suggestions.append(suggestion)
                else:
                    for category, tuples in term_dicts.items():
                        for token in tokens:
                            if snowBallStemmer.stem(token) in tuples[1]:
                                start = content.index(token)
                                end = start + len(token)
                                text = content[start:end]
                                suggestion = {
                                    'example_id': example['id'],
                                    'start':start,
                                    'end':end,
                                    'tag':category,
                                    'text':text
                                }
                                if suggestion not in suggestions:
                                    suggestions.append(suggestion)

        return suggestions

    def process_multiple_examples(self):
        model_dict = {  # Dictionary of models, each has a list of suggestions
            'dictionary_search': [],
            'spacy_small':[],
            'stanford': [],
            # 'flair': [],
        }
        example_ids = []  # we use this to track which examples have been seen. Later we'll submit a testament to LightTag for each model
        for num, example in enumerate(self.examples):
            model_dict['dictionary_search'] += self.process_with_dict(example)
            model_dict['spacy_small'] += self.process_with_spacy_small(example)
            model_dict['stanford'] += self.process_with_stanford(example)
            example_ids.append(example['id'])  # Take note of the example_id we just processed
            if num % 100 == 0:
                print(num)
        return {'models': model_dict, 'example_ids': example_ids}


def main():
    args = parse_arguments()

    text_files = glob.glob(args.helper_path + '/*.txt')

    dictname2tagname = {
        # 'activity_dictionary_eng':'ACTIVITY',
        # 'spatial_dictionary_eng':'SPATIAL',
        # 'smell_dictionary_eng':'SMELL',
        'social_dictionary_eng': 'PEOPLE',
        'weather_dictionary_eng': 'WEATHER',

    }
    if args.reformat_dict == 1:
        fac_path = './Data/Helpers/facility_dictionary_eng.txt'
        act_path = './Data/Helpers/activity_dictionary_eng.txt'
        act_coding = ['401', '402', '403', '404', '405', '406', '407', '408']
        fac_coding = ['301', '302', '303', '304', '305', '306', '307']
        fac_save_path = './Data/Helpers/facility_dictionary_eng_.txt'
        act_save_path = './Data/Helpers/activity_dictionary_eng_.txt'

        reformat_dict = ReformatDict()
        reformat_dict.reformat_dic(fac_path, fac_save_path, fac_coding)
        reformat_dict.reformat_dic(act_path, act_save_path, act_coding)
    dict_with_levels = ['smell_dictionary_eng.txt', 'design_dictionary_eng.txt', 'facility_dictionary_eng_.txt', 'activity_dictionary_eng_.txt']
    print('Configuring dictionaries as look-tables for keyword matching')
    config_dict = ConfigDict(helper_path=args.helper_path, dict_with_levels=dict_with_levels,
                             dictname2tagname=dictname2tagname)
    dictionaries = config_dict.concat(text_files)
    print('Available dictionary names: {}'.format(dictionaries.keys()))
    print('Fetching texts from LightTag')
    session = LTSession(workspace='', user='', pwd='')
    dataset1 = session.get(
        'v1/projects/default/datasets/googlemap/examples/').json()  # Use the slug of the dataset to fetch it from the datasets endpoint
    dataset2 = session.get(
        'v1/projects/default/datasets/tripadvisor/examples/').json()  # Use the slug of the dataset to fetch it from the datasets endpoint
    examples = dataset1 + dataset2  # Use the slug of the dataset to fetch it from the datasets endpoint
    print(len(dataset1), len(dataset2), len(examples))
    print('Setting up models for extracting entities as suggestions')
    examples =examples[:1000]
    models = ConfigModels(examples=examples,dictionaries=dictionaries)
    print('Running models to get different entity suggestions')

    result_dict = models.process_multiple_examples()
    #Due to bugs in models.process_with_dict, have to remove duplicated suggetion from the list
    duplicated_removed =[i for n, i in enumerate(result_dict['models']['dictionary_search'])
            if i not in result_dict['models']['dictionary_search'][n + 1:]]
    result_dict['models']['dictionary_search'] = duplicated_removed
    with open(args.suggestion_json_path, "w") as fp:
        json.dump(result_dict, fp)
    # model_dict1 = {  # Dictionary of models, each has a list of suggestions
    #     'dictionary_search': [], }
    # for num, example in enumerate(models.examples):
    #     model_dict1['dictionary_search'] += models.process_with_dict(example)
    # with open(args.suggestion_json_path, "w") as fp:
    #     result_dict = json.load(fp)
    print('Saved model suggestions to local disk')

    print('Got entity suggestions from NER models')
    # This is what the results look like
    model_outputs = result_dict['models']
    print(model_outputs['stanford'][0])
    maper_dict = dict(ORGANIZATION='ORG', CARDINAL='NUMBER', LOCATION='GPE', COUNTRY='GPE',
                      STATE_OR_PROVINCE='GPE',TITLE = 'PERSON',DATE='TIME',
                      NATIONALITY='NORP', WORK_OF_ART='MISC', CITY='GPE', IDEOLOGY='NORP', PER='PERSON',
                      ORDINAL='NUMBER',
                      PRODUCT='MISC', RELIGION='NORP'
                      )

    replace_if_need = lambda tag: maper_dict.get(tag,tag)  # if the tag is in the dict, give its replacement, otherwise keep it

    def normalize_suggestion(suggestion):
        suggestion['tag'] = replace_if_need(suggestion['tag'])
        return suggestion

    AllSuggestions = pd.DataFrame()
    for model_name in model_outputs:
        suggestions_pd = pd.DataFrame(model_outputs[model_name])
        suggestions_pd['model'] = model_name
        AllSuggestions = AllSuggestions.append(suggestions_pd)
    print(AllSuggestions.pivot_table(index='model',columns='tag',values='start',aggfunc=len).fillna(0).T)
    """Group suggestions by examples, and add detected tag to original content"""
    suggestions_groupby_contents ={}
    for model_name, suggestions in model_outputs.items():
        for suggestion in suggestions:
            if 'example_id' in suggestion:
                if suggestion['example_id'] not in suggestions_groupby_contents:
                    # temp = suggestion
                    # temp.pop('example_id')
                    suggestions_groupby_contents[suggestion['example_id']] = [suggestion]
                else:
                    # temp = suggestion
                    # temp.pop('example_id')
                    suggestions_groupby_contents[suggestion['example_id']] += [suggestion]
    import itertools
    def solve_nested(lst):
        removed = []
        for x in itertools.combinations(lst, 2):
            if x[0][0] in x[1][0]:
                removed.append(x[0])
        return [i for i in lst if i not in removed]



    text_with_suggestions = []
    for id, example in enumerate(examples):
        print('No. {} example'.format(id))
        # content = examples[6496]['content']
        content = example['content']
        # print(example)
        review_id = example['metadata']['review_id']
        # print(review_id)
        # count = -1
        for example_id, suggestions in suggestions_groupby_contents.items():
            # count +=1
            # print('No.',count)
            #remove duplicated suggestion dicts
            suggestions = [i for n, i in enumerate(suggestions) if i not in suggestions[n + 1:]]
            if example_id == example['id']:
                # print(suggestions[0])
                values_start_end=[[i['text'],i['tag'], int(i['start']), int(i['end'])] if 'text' in i else [i['value'],i['tag'], int(i['start']), int(i['end'])] for i in suggestions]
                # print('values_start_end',values_start_end)
                #Sort suggestion list by tag's end position
                values_sorted= sorted(values_start_end, key=lambda x: x[3])
                #Retain the longest tag
                values_sorted = solve_nested(values_sorted)
                new_content = content
                for num, suggestion in enumerate(values_sorted):
                    # print('NO.',num)
                    # print('suggestion0', suggestion)
                    value_lens = len(' $${}$$ '.format(suggestion[1])) + 1
                    # print('1',suggestion)

                    if num >0:
                        # suggestion[2] += previous_value_lens
                        try:
                            new_start = new_content.index(suggestion[0]) + len(suggestion[0])+1
                            new_content = new_content[:new_start] + ' $${}$$ '.format(suggestion[1].upper()) + new_content[new_start:]
                        except:
                            pass
                    else:
                        # print('suggestion',suggestion)
                        # print(content)
                        new_content = new_content[:suggestion[3]] + ' $${}$$ '.format(suggestion[1].upper()) + new_content[suggestion[3]:]
                    previous_value_lens =  value_lens

                text_with_suggestions.append((review_id,new_content))
                # break
    gm_path = './Data/Reviews/GoogleMap/all_reviews.csv'
    ta_path = './Data/Reviews/TripAdvisor/all_reviews.csv'
    data = pd.read_csv(gm_path)
    data1= pd.read_csv(ta_path)
    data1.rename(columns = {'picture_url':'picture_urls'}, inplace=True)

    common_cols = ['review_id', 'review_text', 'review_date', 'review_rating', 'picture_urls', 'total_reviews', 'street', 'local_name', 'page_number', 'word_length']
    data = data[common_cols]
    data1 = data1[common_cols]
    df = pd.concat([data,data1])
    new =  pd.DataFrame(text_with_suggestions, columns =['review_id', 'text_with_suggestions'])
    #Subseting dataset by text_with_suggestions
    df_ = df[df.review_id.isin(new.review_id.to_list())]
    #Integrate text_with_suggestions property to subset
    new_df = df_.merge(new, how = 'left', on = 'review_id')
    # new_df_ = new_df[new_df.text_with_suggestions.isnull()==False]
    new_df['text_with_suggestions'] =  new_df['text_with_suggestions'].fillna(new_df.review_text)
    new_df.to_csv('./Data/Reviews/London_pilot.csv')
    new_df = new_df.sample(frac=1, random_state=1)
    df_team1 = new_df.iloc[:227]
    df_team2 = new_df.iloc[227:227*2]
    df_team3 = new_df.iloc[227*2:227 * 3]
    df_team1.to_csv('./Data/Reviews/pilot_team1.csv')
    df_team2.to_csv('./Data/Reviews/pilot_team2.csv')
    df_team3.to_csv('./Data/Reviews/pilot_team3.csv')
    # for model_name in model_outputs:
    #     model_outputs[model_name] = list(map(normalize_suggestion, model_outputs[model_name]))
    #
    # print('defining a new schema')
    tags = AllSuggestions.tag.unique().tolist()
    tags_ =[t.upper() for t in tags]
    print('Reading tag descriptions')
    with open('./Data/tags.txt', 'r') as f:
        tags_des = f.readlines()
        tags_des = [l.replace('\n', '') for l in tags_des if l != '\n']
    tags_des_dict = {l.split(':')[0].upper(): l.split(':')[1].strip() for l in tags_des}

    additional_tags = [t for t in tags_des_dict if t not in tags_]
    no_tags = ['LANGUAGE', 'CITY', 'LOCATION', 'MISC', 'CAUSE_OF_DEATH', 'RELIGION', 'FAC','SET',  'LAW', 'MONEY','PERCENT','PRODUCT', 'NUMBER',
               'CRIMINAL_CHARGE','TITLE','STATE_OR_PROVINCE', 'NATIONALITY','LOC']
    schema_def = {
        'name': 'Combined Tags',
        'tags': [{'name': t, 'description': tags_des_dict[t] if t in tags_des_dict else t} for t in tags_+additional_tags if t not in no_tags],
        'classification_types':[{'name': 'Negative', 'description': 'Negative sentiment'},
                                {'name': 'Positive', 'description': 'Positive sentiment'}]
    }

    new_schema = session.post('v1/projects/default/schemas/bulk/', json=schema_def)
    # schema = session.get('v1/projects/default/schemas/').json()
    # schema_id = new_schema.json()['id']
    # print('New schema id is {}'.format(schema_id))
    #
    #
    #
    #
    # print('Registering the models and uploading suggestions.')
    # registerd_models = {}  # Capture the models we registered already
    # # session = LTSession(workspace='urbantext0', user='e0441605@u.nus.edu', pwd='Wxhy137-')
    # LIGHTTAG_DOMAIN = 'urbantext0'  # should be your lighttag domain
    # SERVER = 'https://{domain}.lighttag.io/api/'.format(domain=LIGHTTAG_DOMAIN)
    # API_BASE = SERVER + 'v1/'
    # MY_USER = 'jie.zhang137547@icloud.com'
    # MY_PWD = 'Wxhy137-'
    # #
    # response = requests.post(SERVER + 'auth/token/login/',
    #                          json={"username": MY_USER, "password": MY_PWD})
    # assert response.status_code == 200, "Couldn't authenticate"
    # auth_details = response.json()
    # token = auth_details['key']
    # assert auth_details['is_manager'] == 1, "not a manager"  # Check you are a manager
    # # #
    # session = requests.session()
    # session.headers.update({"Authorization": "Token {token}".format(token=token)})
    # registerd_models = {}
    # for num, model_name in enumerate(model_outputs):
    #     model_name = 'spacy_small'
    #     if num >=1:
    #         model_def = {  # definition of the model
    #             'schema': schema_id,
    #             'name': model_name,
    #             'metadata': {
    #                 'date': '12-03-2023'
    #             }
    #         }
    #         # response = session.post(API_BASE + 'v2/models/', json=model_def)
    #         response = session.post('v2/models/',json=model_def) # Send it to LightTag
    #         model = response.json()
    #         pprint(model)
    #
    #
    #         model = response.json()  # Get back the model we just regitered
    #         # break
    #         registerd_models[model_name] = model  # Store it for later
    #
    #         session.post(model['url']+'suggestions/', json=model_outputs[model_name])  # Send the suggestions
    #         session.post(model['url']+'testaments/',json=result_dict['example_ids'])  # Testaments, tells LightTag all of the exampl
    #
    # """Attaching a model to an existing task with the API"""
    # # Retreive the tasks from LightTag API
    # allTasks = session.get('v1/projects/default/task_definitions').json()
    # # Find your task by it's name
    # my_task_name = "london1"
    # my_task = next(filter(lambda task: task['name'] == my_task_name, allTasks))
    # # model_name = ''
    # my_task_models = my_task['suggestion_models']
    # my_task_models.append(model['id'])  # Add the id of the model you created to this task
    # session.post(my_task['url'], json={'suggestion_models': my_task_models})
    """Setting up teams"""
    annotators = session.get('v1/projects/default/annotators/').json()
    team1 =[annotators[-1], annotators[0]]
    team2 =[annotators[1], annotators[3]]
    team3 = [a for a in annotators if a['id'] == 6] + [a for a in annotators if a['id'] == 3]
    # team3 =[annotators[2], annotators[0]]
    Team1 = {"name": "Team1", "description": "Team1", "members": team1}
    Team2 = {"name": "Team2", "description": "Team1", "members": team2}
    Team3 = {"name": "Team3", "description": "Team3", "members": team3}
    session.post('v1/projects/default/teams/', json=Team1)
    session.post('v1/projects/default/teams/', json=Team2)
    session.post('v1/projects/default/teams/', json=Team3)
    teams = session.get('v1/projects/default/teams/').json()
    pprint(teams)


if __name__ =='__main__':
    main()

#
#
#
#
# model_definition = {
#     'schema': schema[0]['id'],
#     'name': 'Look-up dictionaries',
#     'metadata': {
#         'Date': '11-03-2023'  # You can add an arbitrary JSON of metadata to your model
#     }
# }
#
#
# response = session.post('v2/models/',json=model_definition)
# model = response.json()
# pprint(model)
#
#

#Try it out
# session.get(API_BASE+'projects/').json()

