# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 18:09:25 2020

@author: Wang
"""


import numpy as np
from owlready2 import *
from collections import Counter
from Solr_Mapping import solr_search
from copy import deepcopy
from ner_eval import collect_named_entities
from ner_eval import compute_metrics
from ner_eval import compute_precision_recall_wrapper
import csv

#  Given binary predicted results returned by BERT-NER, mapping them to specific entity type


def data_read(path):
  f = open(path).read().split('\n')[:-1]
  pred_list, test_list = [], []
  for line in f:
    y_test, y_pred = line.split('\t')[1:]
    if y_test != 'O':
      y_test = y_test.split('-')[0] + '-' + 'E'
    pred_list.append(y_pred)
    test_list.append(y_test)
  return pred_list, test_list

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
    
    
    
def tokenize_CamelCase(s):
    pCamelCase = re.compile('([A-Z][^A-Z]+)')
    old_end = 0
    tokens = []
    for m in pCamelCase.finditer(s):
        new_start, new_end = m.span()

        if old_end < new_start:
            tokens.append(s[old_end : new_start])
        tokens.append(s[new_start : new_end])
        old_end = new_end
    if new_end < len(s):
        tokens.append(s[new_end :])

    return tokens  


def ent_linking(tokens, onto):

  # s: input string
  # onto: list of classes in ontology
  # search for closest entity based on Jaccard similarity
  
  s = ' '.join(tokens)
  if solr_search(tokens, 'Fuzzy_Matching'):
           return solr_search(tokens, 'Fuzzy_Matching')
  
  
  onto_list = [str(i).split('.')[-1] for i in onto.classes()]
  ent = onto_list[0]
  maxi = Jaccard(s, ent, 3)
  for i in onto_list:
      smi = Jaccard(s, i, 3)
      if smi>maxi:
        maxi = smi
        ent = i
  return ent
  return ''.join(ent)
  
  

# load the ontology
onto = get_ontology("NeuroBridge_093021.owl").load()

# load predicted results
recog_file = open("output/result_dir/label_test.txt",'r',encoding = 'utf-8')
lines = recog_file.read().split('\n')

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
    #print(n)
    word = words[n]
    #y_test = y_test.split('-')[-1]
    #y_pred = y_pred.split('-')[-1]
    if y_pred.split('-')[0] == 'B':
      if span:
          label = ent_linking(span, onto)
          y_pred_list.append('B-'+label)
          for i in range(1, len(span)):
            y_pred_list.append('I-'+label)
          span = []
    if y_pred != 'O':
      span.append(word)
      y_test_list.append(y_test)
    else:
      if span:
        label = ent_linking(span, onto)
        y_pred_list.append('B-'+label)
        for i in range(1, len(span)):
          y_pred_list.append('I-'+label)
        span = []
      y_test_list.append(y_test)
      y_pred_list.append(y_pred)
    n = n+1
if span:
        label = ent_linking(span, onto)
        for i in range(len(span)):
          y_pred_list.append(label)
          
          
# Output of the linking results
output_file = open("2stage_res.txt",'w',encoding = 'utf-8')
for i in range(len(y_test_list)):
  output_file.write(words[i] + '   '+ y_test_list[i]+'   '+y_pred_list[i]+'\n')
output_file.close()

# obtain all concepts mentioned in test set and predicted results
y_pred,y_test = y_pred_list,y_test_list
classes = list(set(list(set(y_test)) + list(set(y_pred))))
classes.remove('O')
classes = list(set([i.split('-')[-1] for i in classes]))
pred_stat = Counter(y_pred)
test_stat = Counter(y_test)
print(pred_stat, test_stat)


# if binary evaluation: change the flag to 1
binary_eval = 0
if binary_eval:
  for i in range(len(y_test)):
    if y_test[i]!='O':
      y_test[i] = y_test[i][:2]+'E'
      
  for i in range(len(y_pred)):
    if y_pred[i]!='O':
      y_pred[i] = y_pred[i][:2]+'E'
  classes = ['E']
    

print(classes)




metrics_results = {'correct': 0, 'incorrect': 0, 'partial': 0,
                   'missed': 0, 'spurious': 0, 'possible': 0, 'actual': 0, 'precision': 0, 'recall': 0}

# overall results
results = {'strict': deepcopy(metrics_results),
           'ent_type': deepcopy(metrics_results),
           'partial':deepcopy(metrics_results),
           'exact':deepcopy(metrics_results)
          }


# results aggregated by entity type
evaluation_agg_entities_type = {e: deepcopy(results) for e in classes}
true_ents, pred_ents = y_test, y_pred


# compute results for one message
tmp_results, tmp_agg_results = compute_metrics(
    collect_named_entities(true_ents), collect_named_entities(pred_ents),  classes
)

#print(tmp_results)

# aggregate overall results
for eval_schema in results.keys():
    for metric in metrics_results.keys():
        results[eval_schema][metric] += tmp_results[eval_schema][metric]
        
# Calculate global precision and recall
    
results = compute_precision_recall_wrapper(results)


# aggregate results by entity type
 
for e_type in classes:

    for eval_schema in tmp_agg_results[e_type]:

        for metric in tmp_agg_results[e_type][eval_schema]:
            
            evaluation_agg_entities_type[e_type][eval_schema][metric] += tmp_agg_results[e_type][eval_schema][metric]
            
    # Calculate precision recall at the individual entity level
            
    evaluation_agg_entities_type[e_type] = compute_precision_recall_wrapper(evaluation_agg_entities_type[e_type])
    e = evaluation_agg_entities_type


# calculate span-level results
print('Entity Type:')
num, cu_p,cu_r,cu_f, cu_total, cu_tp, cu_pos = 0,0,0,0,0,0,0
fil = open('res_detail.csv','w',encoding  = 'gbk')
csv_w = csv.writer(fil)
for keys in sorted(e):
        # print(e[keys]['ent_type'])
        num += 1
        p = e[keys]['ent_type']['precision']
        r = e[keys]['ent_type']['recall']
        #total = e[keys]['ent_type']['correct'] + e[keys]['ent_type']['missed']
        if 'B-' + keys in test_stat.keys():
          total = test_stat['B-' + keys]
        else:
          total = 0
        tp = e[keys]['ent_type']['correct']
        pos = e[keys]['ent_type']['actual']
        fn = e[keys]['ent_type']['missed']
        

        if p == 0 or r == 0:
            f = 0
        else:
            f = round(2*p*r/(p+r),4)
        p,r = round(p,4),round(r,4)
        # if pos != 0 and total!= 0:
        print(keys,' ',p,' ',r, ' ',f)
        cu_total += total
        cu_tp += tp
        cu_pos+= pos
        cu_p+=p
        cu_f+=f
        cu_r+=r
        csv_w.writerow([keys, str(tp)+"/"+str(pos), str(tp)+"/"+str(total)]) 
        print(keys, cu_tp, cu_pos, cu_total)
print(cu_p/num,cu_r/num,cu_f/num)

p, r = cu_tp/cu_total, cu_tp/cu_pos
csv_w.writerow([np.round(cu_p/num,4),np.round(cu_r/num,4),np.round(cu_f/num,4), str(cu_tp)+'/'+str(cu_pos), str(cu_tp)+'/'+str(cu_total), round(2*p*r/(p+r),4)])
fil.close()






















