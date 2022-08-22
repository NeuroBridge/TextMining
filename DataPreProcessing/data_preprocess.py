# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 13:27:19 2021

@author: Lenovo
"""

import numpy as np
import pandas as pd
from copy import deepcopy
import xlrd 
import os
import re
import string
import nltk
from nltk.corpus import stopwords
from collections import Counter
import csv
import json
from nltk.tokenize.treebank import TreebankWordDetokenizer
 





class Token():
    def __init__(self,line):
        
        # store location information of a token for potential usage
        
        line = line.split("\t")
        self.order = line[0]
        self.loc = line[1]
        self.text = line[2]
        self.tag = 'O' if line[-2] == '_' else line[-2].split('#')[-1].split('[')[0]
     
class Document():
    
    
    #  given path of a folder, transform all the data in the form of objects.
    
    def __init__(self,path, type_slec, binary):
        
        # by specifying the subset of all files, we can choose train/dev/test set
        
        self.num_files = len(os.listdir(path))
        if type_slec == 'train':
            self.files = os.listdir(path)[:int(0.7*self.num_files)]
        elif type_slec == 'dev':
            self.files = os.listdir(path)[int(0.7*self.num_files):int(0.8*self.num_files)]
        elif type_slec == 'test':
            self.files = os.listdir(path)[int(0.8*self.num_files):int(1*self.num_files)]
        elif type_slec == 'all':
            self.files = os.listdir(path)
        self.sens_list = []
        self.sens_doc = {}
        self.section_range = {}
        self.binary = binary
        
        train_dev = os.listdir("OUTPUT_Annotated_Papers_train_dev")
        
        for i in self.files:
            
            # locate start and end of abstract and location parts
            
            json_file = open('preprocessed_json/' + i.split('.')[0] + '.json').read()
            json_sections = json.loads(json_file)['sections']
            abs_start, met_start = 100000000000, 100000000000
            abs_end, met_end = -1, -1
            for j in range(len(json_sections)):
                if json_sections[j]['type'] == 'ABSTRACT' or json_sections[j]['type'] == 'TITLE':
                    abs_start = min(abs_start, json_sections[j]['loc'])
                else:
                    if json_sections[j-1]['type'] == 'ABSTRACT' or json_sections[j]['type'] == 'TITLE':
                        abs_end = json_sections[j]['loc']
                if json_sections[j]['type'] == 'METHODS':
                    met_start = min(met_start, json_sections[j]['loc'])
                else:
                    if json_sections[j-1]['type'] == 'METHODS':
                        met_end = json_sections[j]['loc']
                        
                        
            # preserve abstract and location part, delete rest of sections
            self.section_range[i] = [[abs_start, abs_end], [met_start, met_end]]
            self.content = open(path+i,'r',encoding = 'utf-8').read().split("\n")
            self.sens_dict = {}
            for line in self.content:
                if not line.startswith('#') and line:
                    t = token(line)
                    # index: order of sentences
                    index = int(t.order.split('-')[0])
                    if index not in self.sens_dict.keys():
                        self.sens_dict[index] = []
                    # filter words not in the range of abstract and methods
                    if (int(t.loc.split('-')[0]) >= abs_start and int(t.loc.split('-')[1]) <= abs_end) or (int(t.loc.split('-')[0]) >= met_start and int(t.loc.split('-')[1]) <= met_end): 
                        self.sens_dict[index].append(t)
            self.sens_list = self.sens_list + [ self.sens_dict[key] for key in self.sens_dict.keys()]
            self.sens_doc[i] = [ self.sens_dict[key] for key in self.sens_dict.keys()]
            
            

            
            

    def data_formating(self, sent_filter = False):
        
        # store tokens and labels in two lists separately   
        # binary: return binary labels or not 
        # sent_filter: delete sentences do not contain entity or not(used to alleviate imbalanced level)
        
        num_sens = len(self.sens_list)
        x,y = [[] for i in range(num_sens)],[[] for i in range(num_sens)]
        for i in range(num_sens):
            for g in range(len(self.sens_list[i])):
                x[i].append(self.sens_list[i][g].text)
                y[i].append(self.sens_list[i][g].tag)
            for g in range(len(self.sens_list[i])):
                
                # filter sentence-level annotation
                if y[i][g] == "RecruitmentProtocol":
                    y[i][g] = 'O'
                if y[i][g] != 'O':
                    if self.binary == True:
                        y[i][g] = 'E'
                        
                    # add BIO tag for the further usage of NER model 
                    if g == 0:
                        y[i][g] = 'B-'+ y[i][g]
                    else:
                        if y[i][g-1].split('-')[-1] != y[i][g]:
                            y[i][g] = 'B-'+ y[i][g]
                        else:
                            y[i][g] = 'I-'+ y[i][g]
                            
        # an abandoned function: delete empty sentences
        x_filtered, y_filtered = [],[]
        if sent_filter == True:
            for i in range(len(x)):
                if not all(l == 'O' for l  in y[i]):
                    x_filtered.append(x[i])
                    y_filtered.append(y[i])
            return x_filtered,y_filtered  
        else:
            return x,y
    


            
    
    def to_conll(self, outputfile):
        
        # write tokens and their corresponding labels to a file in Conll format
 
        
        
        # read the data from documents
        f = open(outputfile,'w', encoding  = 'utf-8')
        x,y = self.data_formating()
        for i in range(len(x)):
            # delete very long sentences that cannot be handled by BERT
            # should only be applied to test set
          if len(x[i])<200:
            for j in range(len(x[i])):
                # write words in conll format one by one
                f.write(x[i][j] + ' ' + y[i][j] + '\n')
            if len(x[i])!=0:
                f.write('\n')
        f.close()
        
        
        
        
        
        
    def to_sen(self, outputfile):
        
        # write sentence and its given label to a txt file

        
        
        # read the data from documents
        
        f = open(outputfile,'w', encoding  = 'utf-8')
        x,y = self.data_formating(binary = False)
        for i in range(len(x)):
            if list(set(y[i])) == ['O']:
                f.write('__label__0 '+' '.join(x[i]))
                f.write('\n')
            elif len(list(set(y[i]))) >= 2:
                f.write('__label__1 '+' '.join(x[i]))
                f.write('\n')
        f.close()
    
 


        
if __name__ == '__main__':
    train = Document("OUTPUT_Annotated_Papers", "all", binary = False)
    train.to_conll('aLl_tokens.txt')
    



