# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 03:07:41 2021

@author: Lenovo
"""

import json
import os


# this script is about the selection of content in given bioc files
# the folder 'BioC_files' covers all 356 BIOC files

folder_path = 'BioC_files/'
files = os.listdir(folder_path)
for file_name in files:
    print(file_name)
    f = open(folder_path + file_name).read()
    j = json.loads(f)
    dic = {}
    try:
        dic['kwd'] = j['documents'][0]['passages'][0]['infons']['kwd']
    except:
        dic['kwd'] = []    
    dic['pmid'] = j['documents'][0]['passages'][0]['infons']["article-id_pmid"]
    dic['pmcid'] = j['documents'][0]['passages'][0]['infons']["article-id_pmc"]    
    dic['title'] = j['documents'][0]['passages'][0]['text']
    authors = []
    sections = []
    abstract = ''
    full_text = ''
    for i in j['documents'][0]['passages'][0]['infons'].keys():
        if i[:4] == 'name':
            name_str = j['documents'][0]['passages'][0]['infons'][i]
            authors.append(', '.join([name.split(':')[-1] for name in name_str.split(';')]))    
    for i in j['documents'][0]['passages']:
        if i['infons']['section_type'] == 'ABSTRACT':
            abstract += i['text']
            abstract += '\n'
        if i['infons']['section_type'] == 'ABSTRACT' or i['infons']['section_type'] == 'METHODS':
            sections.append({'text' : i['text'], 'loc' : i['offset'], 'type' : i['infons']['section_type']})
            full_text += i['text']
            full_text += '\n'
            
    dic['authors'] = authors
    dic['abstract'] = abstract
    dic['sections'] = sections
    
    
    # output json files
    x = open('preprocessed_json/'+file_name, 'w', encoding = 'utf-8')
    json.dump(dic, x)
    x.close()
