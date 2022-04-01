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
from constants.ability import ATTRIBUTE_COST

LOG = logging.getLogger('Parse.Attributes')
LOG.setLevel(logging.INFO)

def parse_account_attributes(cache: Cache):
    LOG.info('Parsing Account Attributes from account_ability.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'account_ability.ies')

    if not exists(ies_path):
        LOG.warning('File not found: account_ability.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            attribute = {}

            attribute['$ID']      = row['ClassID']
            attribute['$ID_NAME'] = row['ClassName']
            attribute['Name']     = cache.translate(row['Name'])
            attribute['Icon']     = cache.get_icon(row['Icon'])

            attribute['Type']     = 'ACCOUNT'
            attribute['MaxLevel'] = int(row['MaxLevel'])

            attribute['Stat']  = row['BattlePropertyName'][:-3]
            attribute['Value'] = int(row['PointByLevel'])

            attribute['CostType'] = 'ACCOUNT'

            cache.data['attributes'][attribute['$ID_NAME']] = attribute

def parse_attributes(cache: Cache):
    LOG.info('Parsing Attributes from ability.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies_ability.ipf', 'ability.ies')

    if not exists(ies_path):
        LOG.warning('File not found: ability.ies')
        return

    attributes = __get_valid_attributes(cache)

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            attribute = {}

            attribute['$ID']         = row['ClassID']
            attribute['$ID_NAME']    = row['ClassName']
            attribute['Name']        = cache.translate(row['Name'])
            attribute['Icon']        = cache.get_icon(row['Icon'])
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

                    attribute['CostType'] = ATTRIBUTE_COST[row['ScrCalcPrice']]

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
