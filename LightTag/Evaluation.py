from collections import defaultdict
import plotly
import plotly.express as px
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
# from nltk.stem.snowball import SnowballStemmer
# snowBallStemmer = SnowballStemmer("english")
# from nltk import word_tokenize
# from flair.data import Sentence
# from flair.models import SequenceTagger
import spacy
import re
import ast
"""Evaulation"""
def main():
    # args = parse_arguments()
    import  matplotlib.pyplot as plot
    session = LTSession(workspace='urbantext0', user='e0441605@u.nus.edu', pwd='Wxhy137-')

    #Tag counts
    task_url =session.get('v1/projects/default/task_definitions/').json()[0]['url']
    data = session.get(task_url + 'tag_count/').json()
    data = pd.DataFrame(data).set_index('name').reset_index().sort_values('count')
    fig = px.bar(data, x='name', y='count',title='Number of tags')
    fig.show()

    #Tag aggreements
    tag_aggreements=  session.get(task_url+'tag_agg/').json()
    tag_aggreements = pd.DataFrame(tag_aggreements).pivot_table(index='name', columns='agrees', values='count')
    tag_aggreements = tag_aggreements.fillna(0).reset_index()
    fig = px.bar(tag_aggreements, x="name", y=[1, 2, 3, 4, 5, 6], title="Internal Aggreements")
    fig.show()

    #Tag confusion
    import seaborn as sns
    confusion_data = session.get(task_url + 'tag_confusion/').json()  # Fetch the tag level
    D = pd.DataFrame(confusion_data).fillna('')  # Fill null entriess with a blank string
    D.head(10)
    Res = D.pivot_table(index=['tag_a', 'tag_b'], columns=['error'], values='count', )
    Res = Res.fillna(0)
    Res


    plot1 = pd.DataFrame(data).set_index('name').plot.bar(
        title="Disribution of tags for task {name}".format(name="test-set-tags-and-classes"))
    fig = px.bar(data, x='name', y='count')
    aggreements = session.get(task_url + 'tag_agg/').json()
