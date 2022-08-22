# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 01:39:49 2022

@author: Lenovo
"""

import json 
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize




# generate conll files for articles without annotation, based on jsons
files = os.listdir('preprocessed_json')
anno_list = [i.split('.')[0] for i in os.listdir('OUTPUT_Annotated_Papers_train_dev')]
total_conll = open('all_conll_files/total.txt', 'w', encoding = 'utf-8')
for i in range(len(files)):
    if files[i].split('.')[0] not in anno_list:
        j = json.loads(open('preprocessed_json/' + files[i], 'r', encoding = 'utf-8').read())
        sent = j['title']+' '+ ' '.join([i['text'] for i in j['sections'] if (i['type'] == 'ABSTRACT' or i['type'] == 'METHODS')])
        sen_tokens = [word_tokenize(i) for i in sent_tokenize(sent)]
        conll = open('all_conll_files/' + files[i].split('.')[0] + '.txt', 'w', encoding = 'utf-8')
        
        for sen in sen_tokens:
            # ignore long sentence for the sake of NER model's drawback
            if len(sen)<200:
                for token in sen:
                    conll.write(token + ' ' + 'O' + '\n')
                    total_conll.write(token + ' ' + 'O' + '\n')
                conll.write('\n')
                total_conll.write('\n')
        conll.close()
total_conll.close()
    