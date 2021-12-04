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



class token():
    def __init__(self,line):
        
        # store location information of a token for potential usage
        
        line = line.split("\t")
        self.order = line[0]
        self.loc = line[1]
        self.text = line[2]
        self.tag = 'O' if line[-2] == '_' else line[-2].split('#')[-1].split('[')[0]
     
class document():
    
    
    #  given path of a folder, transform all the data in the form of class.
    
    def __init__(self,path):
        self.files = os.listdir(path)
        self.sens_list = []
        for i in self.files:
            self.content = open(path+i,'r',encoding = 'utf-8').read().split("\n")
            self.sens_dict = {}
            for line in self.content:
                if not line.startswith('#') and line:
                    t = token(line)
                    index = int(t.order.split('-')[0])
                    if index not in self.sens_dict.keys():
                        self.sens_dict[index] = []
                    self.sens_dict[index].append(t)
            self.sens_list = self.sens_list + [ self.sens_dict[key] for key in self.sens_dict.keys()]
    


    def data_formating(self, binary = False, sent_filter = False):
        
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
                    if binary == True:
                        y[i][g] = 'E'
                        
                    # add BIO tag for the further usage of NER model 
                    if g == 0:
                        y[i][g] = 'B-'+ y[i][g]
                    else:
                        if y[i][g-1].split('-')[-1] != y[i][g]:
                            y[i][g] = 'B-'+ y[i][g]
                        else:
                            y[i][g] = 'I-'+ y[i][g]
        x_filtered, y_filtered = [],[]
        if sent_filter == True:
            for i in range(len(x)):
                if not all(l == 'O' for l  in y[i]):
                    x_filtered.append(x[i])
                    y_filtered.append(y[i])
            return x_filtered,y_filtered  
        else:
            return x,y
    


            
    
    def to_conll(self, outputfile, split = [0,1]):
        
        # write tokens and their corresponding labels to a file in Conll format
        # the variable 'split' is used to divide train, validation and test datasets
        # example: 
        # to_conll("train.txt", split = [0,0.6])
        # to_conll("dev.txt", split = [0.6,0.7])
        # to_conll("test.txt", split = [0.7,1])
        
        
        # read the data from documents
        f = open(outputfile,'w', encoding  = 'utf-8')
        x,y = self.data_formating()
        for i in range(int(split[0]*len(x)), int(split[1]*len(x))):
            for g in range(len(x[i])):
                f.write(x[i][g] + ' ' + y[i][g] + '\n')
            f.write('\n')
        f.close()
        
        
        
        
        
    def to_sen(self, outputfile, split = [0,1]):
        
        # write sentence and its given label to a txt file
        # the variable 'split' is used to divide train, validation and test datasets
        # example: 
        # to_sen("train.txt", split = [0,0.6]
        # to_sen("dev.txt", split = [0.6,0.7])
        # to_sen("test.txt", split = [0.7,1])
        
        
        # read the data from documents
        
        f = open(outputfile,'w', encoding  = 'utf-8')
        x,y = self.data_formating()
        for i in range(int(split[0]*len(x)), int(split[1]*len(x))):
            if list(set(y[i])) == ['O']:
                f.write('__label__1 '+' '.join(x[i]))
                f.write('\n')
            else:
                f.write('__label__0 '+' '.join(x[i]))
                f.write('\n')
        f.close()
        
    
 
    
if __name__ == '__main__':
    train = document("Abstract_Methods/")
    train.to_conll('token_dataset.txt')
    train.to_sen('sentence_dataset.txt')

    



