# -*- coding: utf-8 -*-
"""
XML Parser for Translations.

Created on Mon Sep 20 09:12:11 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

import csv
import glob
import logging
from os.path import exists, join, normpath, sep

from lxml.html import parse as parse_xml

from cache import TOSParseCache as Cache

LOG = logging.getLogger('Parse.Translations')
LOG.setLevel(logging.INFO)

def parse_translations(cache: Cache):
    translations = {}

    for tsv_path in glob.glob(join(cache.TRANSLATION_PATH, '*.tsv')):
        LOG.info('Parsing Translations from %s ...', normpath(tsv_path).split(sep)[-1])

        with open(tsv_path, 'r', encoding = 'utf-8') as tsv_file:
            for row in csv.reader(tsv_file, delimiter = '\t', quoting = csv.QUOTE_NONE):
                if len(row) < 2:
                    continue

                if row[0] != '' and row[1] != '':
                    translations[row[0]] = row[1]

                if len(row) < 5:
                    continue

                if row[3] != '' and row[4] != '':
                    translations[row[3]] = row[4]

    xml_path = join(cache.PATH_INPUT_DATA, 'language.ipf', 'DicIDTable.xml')

    if not exists(xml_path):
        LOG.warning('File not found: DicIDTable.xml')
        return

    dictionary = {}
    
    soup = parse_xml(xml_path).getroot()

    for data in soup.iter('dic_data'):
        id = data.get('id')
        kr = data.get('kr')

        if id not in translations:
            LOG.warning('Translation not found (%s): %s', id, kr)

        dictionary[kr] = translations[id] if id in translations else id

    cache.data['dictionary'] = dictionary