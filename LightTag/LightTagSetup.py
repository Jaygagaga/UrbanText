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

dictname2tagname = {
    'activity_dictionary_eng':'ACTIVITY',
    # 'spatial_dictionary_eng':'SPATIAL',
    # 'smell_dictionary_eng':'SMELL',
    'social_dictionary_eng':'PEOPLE',
    'weather_dictionary_eng':'WEATHER',

}

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

    # args = parser.parse_args(args=[])
    args = parser.parse_args()#args=[]

    return args
#
# path = './Data/Helpers/smell_dictionary_eng.txt'
# def creat_label_dict(path):
#     with open(path, 'r') as f:
#         dic = [l.replace('\n', '') for l in f.readlines()]
#     return dic
# smell_term = creat_label_dict(path)
# old2newid = {re.split('\t| ',i)[0]:re.split('\t| ',i)[-1] for i in smell_term[1:18]}
# #
# head = [smell_term[0]] +[re.split('\t| ',i)[-1] + '\t' + re.split('\t| ',i)[1] for i in smell_term[1:18]] + [smell_term[18]]
# combined = []
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
#
# key = ['201','202','203','204','205']
# for k in key:
#     print(design_term[design_term.index(k)])
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
            if num % 10 == 0:
                print(num)
        return {'models': model_dict, 'example_ids': example_ids}


def main():
    args = parse_arguments()
    text_files = glob.glob(args.helper_path + '/*.txt')
    dict_with_levels = ['smell_dictionary_eng.txt', 'design_dictionary_eng.txt']
    print('Configuring dictionaries as look-tables for keyword matching')
    config_dict = ConfigDict(helper_path=args.helper_path, dict_with_levels=dict_with_levels,
                             dictname2tagname=dictname2tagname)
    dictionaries = config_dict.concat(text_files)
    print('Available dictionary names: {}'.format(dictionaries.keys()))
    print('Fetching texts from LightTag')
    session = LTSession(workspace='urbantext0', user='e0441605@u.nus.edu', pwd='Wxhy137-')  # Start an API session
    dataset1 = session.get(
        'v1/projects/default/datasets/googlemap/examples/').json()  # Use the slug of the dataset to fetch it from the datasets endpoint
    dataset2 = session.get(
        'v1/projects/default/datasets/tripadvisor/examples/').json()  # Use the slug of the dataset to fetch it from the datasets endpoint
    examples = dataset1 + dataset2  # Use the slug of the dataset to fetch it from the datasets endpoint
    print(len(dataset1), len(dataset2), len(examples))
    print('Setting up models for extracting entities as suggestions')
    examples =examples[:100]
    models = ConfigModels(examples=examples,dictionaries=dictionaries)
    print('Running models to get different entity suggestions')
    result_dict = models.process_multiple_examples()
    # This is what the results look like
    model_outputs = result_dict['models']
    print(model_outputs['stanford'][0])
    maper_dict = dict(ORGANIZATION='ORG', CARDINAL='NUMBER', LOCATION='GPE', LOC='GPE', COUNTRY='GPE',
                      STATE_OR_PROVINCE='GPE',
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

    for model_name in model_outputs:
        model_outputs[model_name] = list(map(normalize_suggestion, model_outputs[model_name]))

    print('defining a new schema')
    tags = AllSuggestions.tag.unique().tolist()
    # schema_def = {
    #     'name': 'ner_models',
    #     'tags': [{'name': t, 'description': t} for t in tags]
    # }
    # new_schema = session.post('v1/projects/default/schemas/bulk/', json=schema_def)
    schema = session.get('v1/projects/default/schemas/').json()
    schema_id = schema[0]['id']
    print('New schema id is {}'.format(schema_id))
    print('Registering the models and uploading suggestions.')
    registerd_models = {}  # Capture the models we registered already
    # session = LTSession(workspace='urbantext0', user='e0441605@u.nus.edu', pwd='Wxhy137-')
    # LIGHTTAG_DOMAIN = 'urbantext0'  # should be your lighttag domain
    # SERVER = 'https://{domain}.lighttag.io/api/'.format(domain=LIGHTTAG_DOMAIN)
    # API_BASE = SERVER + 'v1/'
    # MY_USER = 'e0441605@u.nus.edu'
    # MY_PWD = 'Wxhy137-'
    #
    # response = requests.post(SERVER + 'auth/token/login/',
    #                          json={"username": MY_USER, "password": MY_PWD})
    # assert response.status_code == 200, "Couldn't authenticate"
    # auth_details = response.json()
    # token = auth_details['key']
    # assert auth_details['is_manager'] == 1, "not a manager"  # Check you are a manager
    # #
    # session = requests.session()
    # session.headers.update({"Authorization": "Token {token}".format(token=token)})

    for model_name in model_outputs:
        model_name = 'dictionary_search'
        model_def = {  # definition of the model
            'schema': schema_id,
            'name': model_name,
            'metadata': {
                'date': '12-03-2023'
            }
        }
        # response = session.post(API_BASE + 'v2/models/', json=model_def)
        response = session.post('http://urbantext0.lighttag.io/api/v2/models/', json=model_def)  # Send it to LightTag

        model = response.json()  # Get back the model we just regitered
        registerd_models[model_name] = model  # Store it for later

        session.post('http://urbantext0.lighttag.io/api/v2/models/f27d086c-2396-4d65-806c-99401c397657/'+'suggestions/', json=model_outputs[model_name])  # Send the suggestions
        session.post(model['results'][-1]['url'] + 'testaments/',
                     json=result_dict['example_ids'])  # Testaments, tells LightTag all of the exampl



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

