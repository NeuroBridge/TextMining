# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 14:03:45 2021

@author: Lenovo
"""

import requests
import json


def solr_search(q, core):
    
    print(q)
    q_expression = ' OR%20text%3A%20'.join(q)
    r = requests.get("http://neurobridges-ml.edc.renci.org:8983/solr/" + core + "/select?indent=true&q.op=OR&q=text%3A%20" + q_expression)
    print(r.status_code)
    if r.status_code != 500:
      if 'response' in r.json() and r.json()['response']['numFound']:
          return r.json()['response']['docs'][0]['label_name'][0]
      else:
          return None
    else:
      return None 


