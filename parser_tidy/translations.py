# -*- coding: utf-8 -*-
"""
XML Parser for Translations.

Created on Mon Sep 20 09:12:11 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

from csv import reader as read, QUOTE_NONE
from fnmatch import fnmatch
from logging import getLogger
from os import walk
from os.path import exists, join

from lxml.html import HtmlElement as HTMLElement, parse as parse_xml

from cache import TOSParseCache as Cache
from constants.xml import DIC_TABLE

LOG = getLogger('Parse.Translations')

REGIONS = {
    'itos' : 'English',
    'jtos' : 'Japanese',
    'twtos': 'Taiwanese'
}

class Translator():
    __DICTIONARY = {}

    def __call__(self, text: str) -> str:
        return self.translate(text)

    def __init__(self, cache: Cache):
        self.__TRANSLATION_PATH = join('..', 'Translation', REGIONS[cache.REGION]) if cache.REGION in REGIONS else None

        xml_path = join(cache.PATH_INPUT_DATA, 'language.ipf', DIC_TABLE)

        if not exists(xml_path):
            LOG.error('FILE \'%s\' NOT FOUND', DIC_TABLE)
            return
        
        soup: HTMLElement = parse_xml(xml_path).getroot()

        if self.__TRANSLATION_PATH != '.':
            translations = {}

            for path, _, files in walk(join(self.__TRANSLATION_PATH)):
                for tsv_path in [file for file in files if fnmatch(file, '*.tsv')]:
                    LOG.info('Parsing Translations from %s ...', tsv_path)

                    with open(join(path, tsv_path), 'r', encoding = 'utf-8') as tsv_file:
                        for row in read(tsv_file, delimiter = '\t', quoting = QUOTE_NONE):
                            if len(row) < 2:
                                continue

                            if row[0] != '' and row[1] != '':
                                translations[row[0]] = row[1]

                            if len(row) < 5:
                                continue

                            if row[3] != '' and row[4] != '':
                                translations[row[3]] = row[4]

            data: HTMLElement

            for data in soup.iter('dic_data'):
                id = data.get('id')
                kr = data.get('kr')

                if id not in translations:
                    LOG.warning('Translation for ID \'%s\' not found: %s', id, kr)

                self.__DICTIONARY[kr] = translations[id] if id in translations else kr

        self.__RAW_DICTIONARY = soup

    def cssselect(self, selector: str) -> list[HTMLElement]:
        return self.__RAW_DICTIONARY.cssselect(selector) if self.__RAW_DICTIONARY else []

    def translate(self, text: str) -> str:
        if not text:
            return ''

        if not self.__TRANSLATION_PATH or text not in self.__DICTIONARY:
            return text
        
        return self.__DICTIONARY[text]