# -*- coding: utf-8 -*-
"""
IES Parser for Attributes.

Created on Thu Sep 23 08:05:03 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

from csv import DictReader as IESReader
from logging import getLogger
from os.path import exists, join

from constants.ability import ATTRIBUTE_COST
from assets import Asset
from translations import Translator

LOG = getLogger('Parse.Attributes')

def parse_attributes(root: str, cache: dict, translate: Translator, assetdata: Asset):
    LOG.info('Parsing Attributes from ability.ies ...')

    directory = join(root, 'ies_ability.ipf')
    ies_path  = join(directory, 'ability.ies')

    if not exists(ies_path):
        LOG.warning('File not found: ability.ies')
        return
    
    attribute_data = cache['attributes']

    attributes = __get_valid_attributes(directory, cache['classes'], translate)

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            attribute = {}

            attribute['$ID']         = row['ClassID']
            attribute['$ID_NAME']    = row['ClassName']
            attribute['Name']        = translate(row['Name'])
            attribute['Icon']        = assetdata(row['Icon'])
            attribute['Description'] = translate(row['Desc'])

            attribute['Default']    = 'DEFAULT_ABIL' in row['Keyword']

            attribute['Equipment']  = row['IsEquipItemAbil'] == 'YES'
            attribute['Arts']       = row['Hidden'] == '1'
            attribute['Toggleable'] = row['AlwaysActive'] == 'NO'

            # Default Attributes do not have additional data and are obtained at Level 1 maxed by default at no cost
            if attribute['Default']:
                __set_acquisition(attribute, 'CLASS', 1, row['Job'].split(';'), 'Default Attribute', 'DEFAULT_ATTRIBUTE')
            else:
                __set_acquisition(attribute, 'UNUSED', -1, row['Job'].split(';'), '', 'UNUSED')

            # Parse additional data for Attributes in use only
            if attribute['$ID_NAME'] in attributes:
                name    = attribute['$ID_NAME']

                attribute['Type']     = 'CLASS' if row['SkillCategory'] == 'All' else 'SKILL'
                attribute['MaxLevel'] = attributes[name]['MaxLevel']

                attribute['Grouping'] = row['ActiveGroup']

                attribute['Unlock'].update(attributes[name]['Unlock'])

                attribute['CostType'] = attributes[name]['CostType']

            attribute_data[attribute['$ID_NAME']] = attribute

def parse_team_attributes(root: str, cache: dict, translate: Translator, assetdata: Asset):
    # SELECT_DESCRIPTION = 'dic_data[FilenameWithKey*="AccountAbilityOptionText{Option}{addvalue}_Data_0"]'

    LOG.info('Parsing Account Attributes from account_ability.ies ...')

    ies_path = join(root, 'ies.ipf', 'account_ability.ies')

    if not exists(ies_path):
        LOG.warning('File not found: account_ability.ies')
        return
    
    attribute_data = cache['attributes']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            attribute = {}

            attribute['$ID']      = row['ClassID']
            attribute['$ID_NAME'] = row['ClassName']
            attribute['Name']     = translate(row['Name'])
            attribute['Icon']     = assetdata(row['Icon'])

            attribute['Type']     = 'ACCOUNT'
            attribute['MaxLevel'] = int(row['MaxLevel'])

            attribute['Stat']  = row['BattlePropertyName'][:-3]
            attribute['Value'] = int(row['PointByLevel'])

            attribute['CostType'] = 'ACCOUNT'

            attribute_data[attribute['$ID_NAME']] = attribute

def __get_valid_attributes(directory: str, classes: dict, translate: Translator) -> dict:
    attributes = {}
    
    for job in classes:
        attribute_file = 'ability_%s.ies' % job['InternalName']

        ies_path = join(directory, attribute_file)

        if not exists(ies_path):
            LOG.warning('File not found: %s' % attribute_file)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            LOG.info('Validating Attributes with %s ...', attribute_file)

            for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
                if row['ClassName'] in attributes:
                    attribute = attributes[row['ClassName']]
                else:
                    attribute = {}

                    attribute['MaxLevel'] = int(row['MaxLevel'])
                    attribute['Unlock']   = {}

                    cost_function = row['ScrCalcPrice']

                    # HOTFIX: These functions yield the same outcome
                    if cost_function == 'ABIL_COMMON_PRICE' or (cost_function == 'ABIL_REINFORCE_PRICE' and attribute['MaxLevel'] < 11):
                        cost_function = 'ABIL_BASE_PRICE'

                    # Check if a new cost function has been implemented
                    if cost_function in ATTRIBUTE_COST:
                        attribute['CostType'] = ATTRIBUTE_COST[cost_function]
                    else:
                        LOG.warning('The function \'%s\' for %s is not known', cost_function, row['ClassName'])
                    
                    attributes[row['ClassName']] = attribute

                # The description for unlock requirements for each individual Class
                attribute['Unlock'][job['$ID_NAME']] = translate(row['UnlockDesc'])

    return attributes

def __set_acquisition(attribute: dict, attribute_type: str, max_level: int, classes: list, unlock_description: str, cost_type: str):
    attribute['Type']     = attribute_type
    attribute['MaxLevel'] = max_level

    attribute['Unlock'] = dict.fromkeys(classes, unlock_description)

    attribute['CostType'] = cost_type