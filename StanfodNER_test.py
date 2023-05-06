import pandas as pd
BS = pd.read_csv('./Data/Reviews/BishanPark.csv')
import re
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
import requests
def doc_id(df, col='body'):  # col1 =keyword, col2 = content
    # combined_bri.keyword = [re.sub('\d', '', string) for string in combined_bri[col1]]
    # df.rename(columns={'Unnamed: 0': 'id'}, inplace=True)
    # df['lower_body'] = df[col].str.lower()
    lens= len(df)
    # df = df[df.lower_body.str.contains('belt and road|silk road|one belt one road')==True]
    # print('Number of news about BRI: {}, about {} of the total dataset'.format(len(df),len(df)/lens))
    df['doc_id'] = range(0, len(df))
    # df['content'] = [i.strip('\n') for i in df[col]]
    # df = df.drop(['lower_body'], axis = 1)
    return df

def split_sentence(df, col1='review_text'):  # col1 = content, col2 = sentences
    if 'doc_id' in df.columns:
        spilt_sentence_df = pd.DataFrame(columns=['sentences', 'doc_id'])
    else:
        df['doc_id'] = range(0, len(df))
        spilt_sentence_df = pd.DataFrame(columns=['sentences', 'doc_id'])
    for i in range(len(df)):
        sentences = [j.strip() for j in re.split('\.|!|;|\r', df[col1].iloc[i])]  # add more splitter
        # sentences = [j.strip() for j in self.combined_bri.content.iloc[i].split('。')]
        doc_id = [df.doc_id.iloc[i]] * len(sentences)

        new = pd.DataFrame(list(zip(sentences, doc_id)), columns=['sentences', 'doc_id'])
        spilt_sentence_df = pd.concat([spilt_sentence_df, new], axis=0)
    spilt_sentence_df = spilt_sentence_df.merge(df, how='left', on='doc_id')
    # Remove sentence with na value or duplicated
    spilt_sentence_df = spilt_sentence_df[spilt_sentence_df.sentences != '']
    spilt_sentence_df = spilt_sentence_df.drop_duplicates(subset=['sentences'])
    spilt_sentence_df['id'] = range(0, len(spilt_sentence_df))
    print(spilt_sentence_df[['id','doc_id','sentences']].head())
    return spilt_sentence_df
subset = BS.loc[BS.review_rating ==2]
# BS_split = split_sentence(BS, col1='review_text')
BS_split_2 = split_sentence(subset, col1='review_text')

def stanford_ner(text):
    '''
    Need to run {java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "ner" -port 9000 -timeout 30000} under directory {stanford-corenlp-4.5.3}
    Gets a LightTag example, runs coreNLP on it and returns a list of suggestions in LightTag format
    '''
    results = []
    # This is the URL of the CORENLP server running in a docker container
    url = 'http://localhost:9000/?properties={"annotators":"ner","outputFormat":"json"}'
    txt = text.encode('utf8')  # We need to send it bytes

    data = requests.post(url, data=txt).json()  # Send to the container
    cursor = -1  # Track the last position of a corenlp annotation, so we can ignore overlapping
    entities = {}
    for sentence in data['sentences']:  # Corenlp does sentence parsing as well, which we dont care about
        for entity in sentence["entitymentions"]:  # iterate over the entities
            if entity['ner'] not in ['MISC'] and len(
                    intersection([entity['text'].lower()], ['belt and road', 'silk road'])) == 0:
                if entity['ner'] not in entities:
                    entities[entity['ner']] = [entity['text']]
                else:
                    entities[entity['ner']] += [entity['text']]

    return entities  # The list of lighttag suggestions
ner_tags = []
BS.review_text = BS.review_text.astype(str)
for num, text in enumerate(BS.review_text):
    print(num)
    ner_tags.append(stanford_ner(text))
BS['ner_tags'] = ner_tags
entities = ['ORGANIZATION','IDEOLOGY','CAUSE_OF_DEATH','CRIMINAL_CHARGE']
persons = ['NATIONALITY']
locations = ['LOCATION','CITY', 'STATE_OR_PROVINCE','COUNTRY','TITLE']
time = ['DATE', 'TIME', 'DURATION']
#Removing non-useful tags
list_tags = []
for tags in BS.ner_tags:
  if tags:
    new = {}
    for key, value in tags.items():
      if key in entities+locations+persons:
        if key in locations:
          if 'LOCATION' not in new:
            new['LOCATION'] = [value]
          if 'LOCATION' in new:
            new['LOCATION'] += [value]
        elif key in persons:
          if 'PERSON' not in new:
            new['PERSON'] = [value]
          if 'PERSON' in new:
            new['PERSON'] += [value]
        elif key in time:
          if 'TIME' not in new:
            new['TIME'] = [value]
          if 'TIME' in new:
            new['TIME'] += [value]
        else:
          if key not in new:
            new[key]= [value]
          if key in new:
            new[key] += [value]
    if bool(new):
      list_tags.append({k:list(set([i for sub in v for i in sub])) for k, v in new.items()})
    else:
      list_tags.append(None)
  else:
    list_tags.append(None)

BS['list_tags'] = list_tags
BS['organization_tag'] =BS.list_tags.map(lambda x:
                                                     x['ORGANIZATION'] if x and 'ORGANIZATION' in x else None)
BS['person_tag'] =BS.list_tags.map(lambda x:
                                                     x['PERSON'] if x and 'PERSON'  in x else None)
BS['location_tag'] =BS.list_tags.map(lambda x:
                                                     x['LOCATION'] if x and 'LOCATION'  in x else None)
BS['time_tag'] =BS.list_tags.map(lambda x:
                                                     x['TIME'] if x and 'TIME'  in x else None)
assert len(list_tags) == len(BS), 'Length does not match!'
BS.to_csv('./Data/BS_with_NER_tags.csv')