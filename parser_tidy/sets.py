"""
Created on Sun Feb 13 01:46:25 2022

@author: Nodius
@credit: Temperantia, Nodius
"""

from csv import DictReader as IESReader
from logging import getLogger
from os.path import exists, join
from typing import Callable

from translation import Translator

LOG = getLogger('Parse.Sets')

def parse_equipment(root: str, cache: dict, translate: Translator):
    LOG.info('Parsing Equipment Sets from setitem.ies ...')

    ies_path = join(root, 'ies.ipf', 'setitem.ies')

    if not exists(ies_path):
        LOG.warning('File not found: setitem.ies')
        return

    set_data  = cache['equipment_sets']
    item_data = cache['items']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            equipment_set = {}
            
            equipment_set['$ID']      = str(row['ClassID'])
            equipment_set['$ID_NAME'] = row['ClassName']
            equipment_set['Name']     = translate(row['Name'])
            equipment_set['SetItems'] = []
            equipment_set['Bonus']    = {}

            for nth in range(1, 8):
                # Parse Bonus
                equipment_set['Bonus'][str(nth)] = translate(row['EffectDesc_%s' % (nth)]) if row['EffectDesc_%s' % (nth)] != '' else None

                # Parse Set Items
                item = row['ItemName_%s' % (nth)]

                if item == '' or item not in item_data:
                    continue

                equipment_set['SetItems'].append(item)

            set_data[equipment_set['$ID_NAME']] = equipment_set

def parse_enchants(root: str, cache: dict, translate: Translator):
    LOG.info('Parsing Legend Sets from legend_setitem.ies ...')

    ies_path = join(root, 'ies.ipf', 'legend_setitem.ies')

    if not exists(ies_path):
        LOG.warning('File not found: legend_setitem.ies')
        return

    set_data   = cache['legend_sets']
    skill_data = cache['skills']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            legend_set = {}

            legend_set['$ID']      = str(row['ClassID'])
            legend_set['$ID_NAME'] = row['ClassName']
            legend_set['Name']     = translate(row['Name'])
            legend_set['Set']      = row['LegendGroup'].split('/')
            legend_set['Pieces']   = int(row['MaxOptionCount'])

            materials = {}

            materials['Item']       = row['NeedMaterial']
            materials['WeaponCost'] = row['NeedMaterial_WeaponCnt']
            materials['ArmorCost']  = row['NeedMaterial_ArmorCnt']

            legend_set['Materials'] = materials
            legend_set['Bonus']     = {}

            for nth in range(1, legend_set['Pieces'] + 1):
                piece = str(nth)

                if row['EffectDesc_%s' % (nth)] == '' and row['SetItemSkill_%s' % (nth)] == '':
                    continue

                legend_set['Bonus'][piece] = {}
                
                if row['EffectDesc_%s' % (nth)] != '':
                    legend_set['Bonus'][piece]['Effect'] = translate(row['EffectDesc_%s' % (nth)])

                if row['SetItemSkill_%s' % (nth)] != '':
                    legend_set['Bonus'][piece]['Skill']  = row['SetItemSkill_%s' % (nth)]

                    skill = {}

                    skill['$ID_NAME'] = legend_set['Bonus'][piece]['Skill']
                    skill['Type']     = 'LEGEND_SET'

                    skill_data[skill['$ID_NAME']] = skill
            
            set_data[legend_set['$ID_NAME']] = legend_set