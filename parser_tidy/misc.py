# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 07:35:39 2021

@author: CPPG02619
"""


import csv
import logging
import os
import io
from cache import TOSParseCache as Cache

def parse_achievements(c = None):
    if c == None:
        c = Cache()
        c.build('itos')
    achievements(c)

def achievements(c):
    logging.warning('Parsing Achievemets...')
    
    try:
        ies_path = os.path.join(c.PATH_INPUT_DATA, 'ies.ipf', 'achieve.ies')
    except:
        logging.warning("achieve.ies not found")
    rows = []
    with io.open(ies_path, 'r',  encoding="utf-8") as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            rows.append(row)
            obj = {}
            obj['$ID']      = row['ClassID']
            obj['$ID_NAME'] = row['ClassName']
            obj['Group']    = row['Group']
            obj['Name']     = c.translate(row['Name'])
            obj['Desc']     = c.translate(row['Desc'])
            obj['DescTitle']     = c.translate(row['DescTitle'])
            obj['Hidden']   = True if row['Hidden'] == 'YES' else False
            obj['Icon']     = row['Icon']
            obj['Image']     = row['Image']
            c.data['achievements'][obj['$ID']] = obj
            
            
            
            
            