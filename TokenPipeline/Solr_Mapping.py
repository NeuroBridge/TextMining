# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 14:03:45 2021

@author: Lenovo
"""

import requests
import json

# r = requests.get(url = "http://browser.ihtsdotools.org/api/v2/snomed/en-edition/v20180131/descriptions?query=asthma&searchMode=partialMatching&lang=english&statusFilter=english&skipTo=0&returnLimit=5&normalize=true&semanticFilter=finding&moduleFilter=900000000000207008&refsetFilter=450970008")

def solr_search(q):
    
    q_expression = ' OR%20text%3A%20'.join(q)
    r = requests.get("http://neurobridges-ml.edc.renci.org:8983/solr/Fuzzy_Matching/select?indent=true&q.op=OR&q=text%3A%20" + q_expression)
    # print(r.json())
    if 'response' in r.json() and r.json()['response']['numFound']:
        return r.json()['response']['docs'][0]['label_name'][0]
    else:
        return None


q = ['Known', 'Disorder']
print(solr_search(q))


# import requests

# x = requests.get('https://w3schools.com')
# print(x.headers['Content-Type'])
