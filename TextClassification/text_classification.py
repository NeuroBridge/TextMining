# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 19:55:32 2021

@author: Lenovo
"""

import fasttext

model = fasttext.train_supervised(input="sen_train.txt", lr=1.0, epoch=25, wordNgrams=2)
print(model.test("sen_test.txt"))