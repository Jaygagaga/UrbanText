# #---------Translation to English-------------------
#     def translate(self,posts):
#       translateds = []
#       for post in posts:
#         translated = '{}'.format(self.translate_en(post))
#         translateds.append(translated)
#       return translateds
#
#
#     def translate_en(self,sent):
#
#       # Add your key and endpoint
#       key = "d82fbb787a544d99ba930f1b6b38b37e"
#       endpoint = "https://api.cognitive.microsofttranslator.com"
#
#       # Add your location, also known as region. The default is global.
#       # This is required if using a Cognitive Services resource.
#       location = "global"
#
#       path = '/translate'
#       constructed_url = endpoint + path
#
#       params = {
#           'api-version': '3.0',
#           # 'from': 'en',
#           'to': ['en']
#       }
#
#       headers = {
#           'Ocp-Apim-Subscription-Key': key,
#           'Ocp-Apim-Subscription-Region': location,
#           'Content-type': 'application/json',
#           'X-ClientTraceId': str(uuid.uuid4())
#       }
#
#       # You can pass more than one object in body.
#
#       body = [{'text':'{}'.format(sent)}]
#
#       request = requests.post(constructed_url, params=params, headers=headers, json=body)
#       response = request.json()
#       translated= response[0]['translations'][0]['text']
#       return translated

"""Using DeepL api"""
import deepl
import pandas as pd
auth_key = '350084ed-0613-d640-4117-ca92ac02ea7c'
translator = deepl.Translator(auth_key)
# text = 'Watertorenplein'
streets = pd.read_csv('./Data/Amsterdam_streets.csv')
#only translate streets without numbers
import re
street_names  = list(streets[streets.Street.map(lambda x: False if re.search('\d', x) else True)].Street.unique())

streets_foreign = []
translated_en = []
# translated_en = [i.text for i in translated_en]
for num, street in enumerate(street_names[10:1000]):
    try:
        translated = translator.translate_text(street, target_lang="EN-GB", source_lang="NL")
        translated_en.append(translated.text)
        streets_foreign.append(street)
        print('Translated No. {} {} to {}'.format(num, street,translated))
    except:
        print('Failed to translate No. {} {} to English'.format(num,street))

trans_df = pd.DataFrame(list(zip(streets_foreign, translated_en)), columns=['Street', 'English_name'])
trans_df.to_csv('./Data/Amsterdam_streets_en.csv')