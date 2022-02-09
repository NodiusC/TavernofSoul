# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 08:38:06 2021

@author: CPPG02619
"""

import csv
import logging
import io
from cache import TOSParseCache as Cache
import xml.etree.ElementTree as ET
from os.path import join

def parse(c = None):
    if c == None:
        c = Cache()
        c.build("itos")
        
def parseChar(c):
    logging.warning('Parsing char exp...')
    ies_path = join(c.PATH_INPUT_DATA, 'ies.ipf', 'xp.ies')
    rows    = []
    exp     = []
    with io.open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            rows.append(row)
            xp = {
                'Lv'        : int(row['Lv']),
                'TotalXp'   : float(row['TotalXp'] ),                
            }
            exp.append(xp)
    c.data['charxp'] = exp

def parsePetAssister(c):
    logging.warning('Parsing char exp...')
    ies_path    = join(c.PATH_INPUT_DATA, 'xml.ipf', 'pet_exp.xml')
    data        = ET.parse(ies_path).getroot()
    pet         = [i.attrib for i in data[0]]
    assister    = [i.attrib for i in data[2]]
    
    c.data['petxp']       = pet
    c.data['assisterxp']  = assister
    