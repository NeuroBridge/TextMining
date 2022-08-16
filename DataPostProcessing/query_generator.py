# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 21:19:19 2022

@author: Lenovo
"""

from owlready2 import *
import re
import requests
import pandas as pd




def tokenize_CamelCase(s):
    pCamelCase = re.compile('([A-Z][^A-Z]+)')
    old_end = 0
    tokens = []
    new_end = None
    for m in pCamelCase.finditer(s):
        new_start, new_end = m.span()

        if old_end < new_start:
            tokens.append(s[old_end : new_start])
        tokens.append(s[new_start : new_end])
        old_end = new_end
    if not new_end:
        return [s]
    if new_end < len(s):
        tokens.append(s[new_end :])

    return tokens  

def query_expand(term):
    global subclasses
    subclasses = [term]
    def recur(concept):
        global subclasses
        sub_list = [j for j in list(concept.subclasses()) if j.name.split('.')[-1] != concept.name.split('.')[-1]]
        if sub_list:
            subclasses += sub_list
            for j in sub_list:
                recur(j)
    recur(term)
    return [i.name for i in subclasses]

ONTO = get_ontology("D:/neurobri/Annotation-Project-main/Working_Ontologies/NeuroBridge_093021.owl").load()
CLASSES = ONTO.classes()
DIC_SUB = {}

for i in CLASSES:
    DIC_SUB[i.name] = query_expand(i)











def expanded_NBC_query(query, dic):
    
    term_list = []
    for targeted_term in query:
        for expanded_terms in dic[targeted_term]:
            term_list.append(expanded_terms)
    q_expression = '%20OR%20NBC%3A%20'.join(term_list)
    print("http://neurobridges-ml.edc.renci.org:8983/solr/#/NB/query?indent=true&q.op=OR&q=NBC%3A%20" + q_expression + '&rows=10')
    print()
    results = requests.get("http://neurobridges-ml.edc.renci.org:8983/solr/NB/select?indent=true&q.op=OR&q=NBC%3A%20" + q_expression + '&rows=10')
    results.encoding = results.apparent_encoding
    prefix = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC"
    return [[i['pmid'][0] , i['pmcid'][0],i['title'][0], prefix+str(i['pmcid'][0])] for i in result.json()['response']['docs'][:10]]



def NBC_query(query):
    q_expression = '%20OR%20NBC%3A%20'.join(query)
    print("http://neurobridges-ml.edc.renci.org:8983/solr/#/NB/query?indent=true&q.op=OR&q=NBC%3A%20" + q_expression + '&rows=10')
    print()
    results = requests.get("http://neurobridges-ml.edc.renci.org:8983/solr/NB/select?indent=true&q.op=OR&q=NBC%3A%20" + q_expression + '&rows=10')
    results.encoding = results.apparent_encoding
    prefix = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC"
    return [[i['pmid'][0] , i['pmcid'][0],i['title'][0], prefix+str(i['pmcid'][0])] for i in res.json()['response']['docs'][:10]]

def text_query(query):
    term_list = []
    for term in query:
        term_list.append('(sections.text%3A%20' + '%20AND%20sections.text%3A%20'.join(tokenize_CamelCase(i)) + ')')
    q_expression = '%20OR%20'.join(concat_w)
    print("http://neurobridges-ml.edc.renci.org:8983/solr/#/NB/query?indent=true&q.op=OR&q=" + q_expression + '&rows=10')
    print()
    # return "http://neurobridges-ml.edc.renci.org:8983/solr/#/NB/query?indent=true&q.op=OR&q=" + q_expression
    results = requests.get("http://neurobridges-ml.edc.renci.org:8983/solr/NB/select?indent=true&q.op=OR&q=" + q_expression + '&rows=10')
    results.encoding = results.apparent_encoding
    prefix = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC"
    return [[i['pmid'][0] , i['pmcid'][0], i['title'][0], prefix+str(i['pmcid'][0])] for i in res.json()['response']['docs'][:10]]


    




q1 = ['Schizophrenia',"RestingStateImaging", 'RestingStateImagingProtocol', 'NeurocognitiveTest']
q2 = ['NoKnownDisorder', "RestingStateImaging", 'RestingStateImagingProtocol']
q3 = ['ImpulsivityScale', 'T1WeightedImaging', 'T1WeightedImagingProtocol']
q4 = ["AlcoholAbuse" , 'PersonalityRatingScale', 'TaskParadigmImaging' ,'TaskParadigmImagingProtocol' ]
q5 = ['CannabisAbuse', 'NeurocognitiveTest', 'RestingStateImaging', 'RestingStateImagingProtocol']





df = pd.DataFrame()


query = q5
print(query)
exNBC = expanded_NBC_query(query, DIC_SUB)
NBC = NBC_query(query)
text = text_query(query)



df['PMID'] = [i[0] for i in exNBC]  + [i[0] for i in NBC]
df['PMCID'] = [i[1] for i in exNBC]  + [i[1] for i in NBC]
df['Title'] = [i[2] for i in exNBC]  + [i[2] for i in NBC]
df['Link'] = [i[3] for i in exNBC]  + [i[3] for i in NBC]


previous = pd.read_csv("C:/Users/Lenovo/Desktop/TextMining-main/TokenPipeline/reviewer1/query5.csv")['PMID']
df = df[~df['PMID'].isin(previous)]
df = df.sample(frac = 1).drop_duplicates().reset_index(drop=True)
df.to_csv('reviewer1/query5.csv', encoding = 'GB18030')
print(len(df))



