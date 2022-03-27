# -*- coding: utf-8 -*-
"""
IES Parser for Attributes.

Created on Thu Sep 23 08:05:03 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

import csv
import logging
from os.path import exists, join

from cache import TOSParseCache as Cache

LOG = logging.getLogger('Parse.Attributes')
LOG.setLevel(logging.INFO)

def parse_attributes(cache: Cache):
    attributes = {}
    
    for job in cache.data['classes']:
        attribute_file = 'ability_%s.ies' % job['InternalName']

        ies_path = join(cache.PATH_INPUT_DATA, 'ies_ability.ipf', attribute_file)

        if not exists(ies_path):
            LOG.warning('File not found: %s' % attribute_file)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            LOG.info('Parsing Attribute Acquisition from %s ...', attribute_file)

            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                if row['ClassName'] in attributes:
                    attribute = attributes[row['ClassName']]

                else:
                    attribute = {}

                    attribute['MaxLevel']    = int(row['MaxLevel'])

                    attribute['Unlock'] = {}

                    # TODO: Manual Cost Parsing for Cost Dictionary
                    attribute['BaseCost']   
                    attribute['CostFactor'] 
                    attribute['LevelCost']  

                attribute['Unlock'][job['$ID_NAME']] = cache.translate(row['UnlockDesc'])
                    
                attributes[row['ClassName']] = attribute

    LOG.info('Parsing Attributes from ability.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies_ability.ipf', 'ability.ies')

    if not exists(ies_path):
        LOG.warning('File not found: ability.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            attribute = {}

            attribute['$ID']         = row['ClassID']
            attribute['$ID_NAME']    = row['ClassName']
            attribute['Name']        = cache.translate(row['Name'])
            attribute['Icon']        = cache.parse_entity_icon(row['Icon'])
            attribute['Description'] = cache.translate(row['Desc'])

            attribute['Default']    = 'DEFAULT_ABIL' in row['Keyword']
            attribute['Arts']       = row['Hidden'] == '1'
            attribute['Toggleable'] = row['AlwaysActive'] == 'NO'

            # Default Attributes do not have additional data and are obtained at Level 1 maxed by default at no cost
            if attribute['Default']:
                attribute['Type'] = 'CLASS'

                attribute['MaxLevel'] = 1

                attribute['Unlock'] = {job: 'Default Attribute' for job in row['Job'].split(';')}
                
                attribute['BaseCost']   = 0
                attribute['CostFactor'] = 0
                attribute['LevelCost']  = 0
            else:
                attribute['Type'] = 'UNUSED'

                attribute['MaxLevel'] = -1

                attribute['Unlock'] = {job: '' for job in row['Job'].split(';')}
                
                attribute['BaseCost']   = -1
                attribute['CostFactor'] = -1
                attribute['LevelCost']  = -1

            # Parse additional data only for Attributes in use
            if attribute['$ID_NAME'] in attributes:
                name    = attribute['$ID_NAME']
                unlocks = attributes[name]['Unlock']

                attribute['Type'] = 'CLASS' if row['SkillCategory'] == 'All' else 'SKILL'

                if attribute['MaxLevel'] < 0:
                    attribute['MaxLevel'] = attributes[name]['MaxLevel']

                for job in attribute['Unlock'].keys():
                    if job not in unlocks:
                        continue

                    attribute['Unlock'][job] = unlocks[job]
                
                attribute['BaseCost']   = attributes[name]['BaseCost']
                attribute['CostFactor'] = attributes[name]['CostFactor']
                attribute['LevelCost']  = attributes[name]['LevelCost']

            cache.data['attributes'][attribute['$ID_NAME']] = attribute