# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 18:09:25 2020

@author: Wang
"""

from sklearn.metrics import classification_report
from ner_eval import collect_named_entities
from ner_eval import compute_metrics
from ner_eval import compute_precision_recall_wrapper
from copy import deepcopy
import re
import csv
import numpy as np
from sys import argv
from owlready2 import *



#  Given binary predicted results returned by BERT-NER, mapping them to specific entity type



def Jaccard(x,y,n):

    # x, y: two words/spans
    # n: number of grams
    x,y = x.lower(), y.lower()
    x_grams, y_grams = [],[]
    for i in range(len(x)-n+1):
      x_grams.append(x[i:i+n])
    for i in range(len(y)-n+1):
      y_grams.append(y[i:i+n])
    x,y = set(x_grams),set(y_grams)
    union = x|y
    intersection = x&y
    return len(intersection)/len(union)
    
def cos_sim(x,y):

    # calculate cosine similarity given two word vector
    return np.sum(x*y)/(np.linalg.norm(x)*np.linalg.norm(y))
    
    

def get_emb(emb):

    # get wordembedding in form of dictionary from .txt file 
    # not used in current experiments
    dic = open(emb,'r',encoding='ISO-8859-1').read()
    dic = dic.split('\n')
    for i in range(len(dic)):
      dic[i] = dic[i].split(' ')
    key, va = [],[]
    for line in dic:
      key.append(line[0])
      va.append(line[1:])
      dic = dict(zip(key,va))
      return dic
def feat(x, dic):

      # map a word to wordembedding, not used in current practice
      offset = []
      words = []
      for i in range(len(x)):
        if x[i] == x[i].upper():
            offset.append(i)
      if offset:
        for i in range(len(offset)-1):
          words.append(x[offset[i]:offset[i+1]])
        words.append(x[offset[-1]:])
      else:
        words.append(x)
      fea = np.around(np.array([0 for i in range(50)]).astype("float")*(1),decimals=7)
      for i in words:
        if i.lower() in dic.keys():
            vec =  np.around(np.array(emb[i.lower()][:-1]).astype("float")*(1),decimals=7)
        else:
            vec =  np.around(np.array([0 for i in range(50)]).astype("float")*(1),decimals=7)
        fea += vec
      return fea  
      
      
def ent_linking(s, onto):

  # s: input string
  # onto: list of classes in ontology
  # search for closest entity based on Jaccard similarity
  onto_list = [str(i).split('.')[-1] for i in onto.classes()]
  ent = onto_list[0]
  maxi = Jaccard(s, ent, 3)
  for i in onto_list:
      smi = Jaccard(s, i, 3)
      if smi>maxi:
        maxi = smi
        ent = i
  return ent
  
  

# load the ontology
onto = get_ontology("NeuroBridge_093021.owl").load()

# load predicted results
f = open("output/result_dir/label_test.txt",'r',encoding = 'utf-8')
lines = f.read().split('\n')

# load raw text
words = [i for i in open("data/test.txt",'r',encoding = 'utf-8').read().split('\n') if i!='' and i!=' ']
words = [i.split(' ')[0] for i in words]


y_test_list,y_pred_list= [],[]
span = []
n = 0

# reason why raw text in the label_test.txt cannot be used:
# due to the nature of masked language model, words will be splited into several pieces
# hence, words in the label_test.txt file are frequently incomplete, harm the performance of string matching
# so the test dataset itself is used instead

# span level string match: detect span in the predicted file and do the entity linking using n-grams Jaccard similarity 
for line in lines[:-1]:
    y_test,y_pred = line.split('\t')[1:3]
    word = words[n]
    y_test = y_test.split('-')[-1]
    y_pred = y_pred.split('-')[-1]
    if y_pred!='O':
      span.append(word)
      y_test_list.append(y_test)
    else:
      if span:
        label = ent_linking(''.join(span), onto)
        for i in range(len(span)):
          y_pred_list.append(label)
        span = []
      y_test_list.append(y_test)
      y_pred_list.append(y_pred)
    n = n+1
if span:
        label = ent_linking(''.join(span), onto)
        for i in range(len(span)):
          y_pred_list.append(label)
          
          
# Output of the linking results
f = open("2stage_res.txt",'w',encoding = 'utf-8')
for i in range(len(y_test_list)):
  f.write(words[i] + '   '+ y_test_list[i]+'   '+y_pred_list[i]+'\n')
f.close()
    

# print classification report
recall_str=classification_report(y_test_list,y_pred_list)
print(recall_str)



