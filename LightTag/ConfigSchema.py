import pandas as pd
from requests.auth import HTTPBasicAuth
from LightTag.ltsession import LTSession

def main():
    # args = parse_arguments()
    import  matplotlib.pyplot as plot
    session = LTSession(workspace='urbantext0', user='e0441605@u.nus.edu', pwd='Wxhy137-')
    tags_dict = {}
    file = open('/Users/jie/UrbanText/Data/Helpers/tags.txt', 'r')
    for line in file:
        if line and line != '\n':
            tags_dict[line.split(':')[0]] = line.split(':')[-1].strip().replace('\n', '')
    schema_def = {
        'name': 'Tags_v3',
        'tags': [{'name': t, 'description': tags_dict[t]} for t in tags_dict.keys()],
        'classification_types': [{'name': 'Negative', 'description': 'Negative sentiment on document level'},
                                 {'name': 'Positive', 'description': 'Positive sentiment on document level'},
                                 {'name': 'Netural', 'description': 'Netural sentiment on document level'}]
    }

    new_schema = session.post('v1/projects/default/schemas/bulk/', json=schema_def)
    # schema = session.get('v1/projects/default/schemas/').json()
    schema_id = new_schema.json()['id']
    print('New schema id is {}'.format(schema_id))

    #Reading and spliting dataset by groups
    BS = pd.read_csv('./Data/Reviews/BishanPark.csv')
    new_df = BS.sample(frac=1, random_state=1)
    df_team1 = new_df.iloc[:337]
    df_team2 = new_df.iloc[337:337*2]
    df_team3 = new_df.iloc[337*2:337 * 3]
    df_team1.to_csv('./Data/Reviews/BishanPark_team1.csv')
    df_team2.to_csv('./Data/Reviews/BishanPark_team2.csv')
    df_team3.to_csv('./Data/Reviews/BishanPark_team3.csv')
    # new_df.to_csv('./Data/Reviews/GoogleMap_Singapore.csv')

if __name__ =='__main__':
    main()