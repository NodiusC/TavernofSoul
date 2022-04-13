# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 08:07:28 2021

@author: Temperantia
"""

from csv import DictReader as IESReader
from logging import getLogger
from os.path import exists, join

LOG = getLogger('Parse.IESUtil')

def load(root: str, ies: str,c):
    ies_path = join(root, "ies.ipf", ies)

    if not exists(ies_path):
        LOG.warning('File not found: %s', ies_path)
        return []
    
    ies_data = []

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            for key in row.keys(): # Cast to int or float if possible
                try:
                    row[key] = int(row[key])
                except :
                    try:
                        row[key] = float(row[key])
                    except :
                        row[key] = row[key]

            ies_data.append(row)

    return ies_data