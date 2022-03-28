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
    LOG.info('Parsing Attributes from ability.ies ...')

    attributes = __get_valid_attributes(cache)

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

            attribute['Equipment']  = row['IsEquipItemAbil'] == 'YES'
            attribute['Arts']       = row['Hidden'] == '1'
            attribute['Toggleable'] = row['AlwaysActive'] == 'NO'

            # Default Attributes do not have additional data and are obtained at Level 1 maxed by default at no cost
            if attribute['Default']:
                __populate(attribute, 'CLASS', 1, row['Job'].split(';'), 'Default Attribute', 0)
            else:
                __populate(attribute, 'UNUSED', -1, row['Job'].split(';'), '', -1)

            # Parse additional data only for Attributes in use
            if attribute['$ID_NAME'] in attributes:
                name    = attribute['$ID_NAME']
                unlocks = attributes[name]['Unlock']

                attribute['Type'] = 'CLASS' if row['SkillCategory'] == 'All' else 'SKILL'

                attribute['MaxLevel'] = attributes[name]['MaxLevel']

                for job in attribute['Unlock'].keys():
                    if job not in unlocks:
                        continue

                    attribute['Unlock'][job] = unlocks[job]

                attribute['CostType'] = attributes[name]['CostType']

                if row['ActiveGroup'] != '':
                    if row['ActiveGroup'] not in cache.data['attribute_groups']:
                        cache.data['attribute_groups'][row['ActiveGroup']] = []

                    cache.data['attribute_groups'][row['ActiveGroup']].append(name)

            cache.data['attributes'][attribute['$ID_NAME']] = attribute

__COST_TYPE = {
    'ABIL_REINFORCE_PRICE'           : 'ENHANCE',
    'HIDDENABIL_PRICE_COND_REINFORCE': 'ENHANCE_ARTS',
    'ABIL_BASE_PRICE'                : 'BASIC',
    'ABIL_ABOVE_NORMAL_PRICE'        : 'ADVANCED',
    'ABIL_COMMON_PRICE_1LV'          : 'COMMON_001',
    'ABIL_COMMON_PRICE_100LV'        : 'COMMON_100',
    'ABIL_COMMON_PRICE_150LV'        : 'COMMON_150',
    'ABIL_COMMON_PRICE_200LV'        : 'COMMON_200',
    'ABIL_COMMON_PRICE_250LV'        : 'COMMON_250',
    'ABIL_COMMON_PRICE_300LV'        : 'COMMON_300',
    'ABIL_COMMON_PRICE_350LV'        : 'COMMON_350',
    'ABIL_COMMON_PRICE_400LV'        : 'COMMON_400',
    'HIDDENABIL_PRICE_COND_JOBLEVEL' : 'ARTS',
    'ABIL_MASTERY_PRICE'             : '2H_SPEAR_MASTERY_PENETRATION',
    'ABIL_NECROMANCER8_PRICE'        : 'CREATE_SHOGGOTH_ENLARGEMENT',
    'ABIL_TOTALDEADPARTS_PRICE'      : 'NECROMANCER_CORPSE_FRAGMENT_CAPACITY',
    'ABIL_SORCERER2_PRICE'           : 'SORCERER_SP_RECOVERY',
    'ABIL_WARLOCK14_PRICE'           : 'INVOCATION_DEMON_SPIRIT',
    'ABIL_6RANK_NORMAL_PRICE'        : 'CENTURION'
}

def __get_valid_attributes(cache: Cache):
    attributes = {}
    
    for job in cache.data['classes']:
        attribute_file = 'ability_%s.ies' % job['InternalName']

        ies_path = join(cache.PATH_INPUT_DATA, 'ies_ability.ipf', attribute_file)

        if not exists(ies_path):
            LOG.warning('File not found: %s' % attribute_file)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            LOG.info('Validating Attributes with %s ...', attribute_file)

            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                if row['ClassName'] in attributes:
                    attribute = attributes[row['ClassName']]

                else:
                    attribute = {}

                    attribute['MaxLevel'] = int(row['MaxLevel'])

                    attribute['Unlock'] = {}

                    # HOTFIX: The functions yield the same outcome
                    if row['ScrCalcPrice'] == 'ABIL_COMMON_PRICE' or (row['ScrCalcPrice'] == 'ABIL_REINFORCE_PRICE' and attribute['MaxLevel'] < 11):
                        row['ScrCalcPrice'] = 'ABIL_BASE_PRICE'

                    attribute['CostType'] = __COST_TYPE[row['ScrCalcPrice']]

                attribute['Unlock'][job['$ID_NAME']] = cache.translate(row['UnlockDesc'])
                    
                attributes[row['ClassName']] = attribute

    return attributes

def __populate(attribute: dict, attribute_type: str, max_lv: int, jobs: list, unlock: str, cost: int):
    attribute['Type']     = attribute_type
    attribute['MaxLevel'] = max_lv

    attribute['Unlock'] = dict.fromkeys(jobs, unlock)
    
    attribute['BaseCost']   = cost
    attribute['CostFactor'] = cost
    attribute['LevelCost']  = cost