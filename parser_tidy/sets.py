"""
Created on Sun Feb 13 01:46:25 2022

@author: Nodius
@credit: Temperantia, Nodius
"""

import csv
import logging
from os.path import exists, join

from cache import TOSParseCache as Cache

LOG = logging.getLogger('Parse.Sets')
LOG.setLevel(logging.INFO)

def parse_equipment_sets(cache: Cache):
    LOG.info('Parsing Equipment Sets from setitem.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'setitem.ies')

    if not exists(ies_path):
        LOG.warning('File not found: setitem.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            equipment_set = {}
            
            equipment_set['$ID']      = str(row['ClassID'])
            equipment_set['$ID_NAME'] = row['ClassName']
            equipment_set['Name']     = cache.translate(row['Name'])
            equipment_set['SetItems'] = []
            equipment_set['Bonus']    = {}

            for nth in range(1, 8):
                # Parse Bonus
                equipment_set['Bonus'][str(nth)] = cache.translate(row['EffectDesc_%s' % (nth)]) if row['EffectDesc_%s' % (nth)] != '' else None

                # Parse Set Items
                item = row['ItemName_%s' % (nth)]

                if item == '' or item not in cache.data['items']:
                    continue

                equipment_set['SetItems'].append(item)

            cache.data['equipment_sets'][equipment_set['$ID_NAME']] = equipment_set

def parse_legend_sets(cache: Cache):
    LOG.info('Parsing Legend Sets from legend_setitem.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'legend_setitem.ies')

    if not exists(ies_path):
        LOG.warning('File not found: legend_setitem.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            legend_set = {}

            legend_set['$ID']      = str(row['ClassID'])
            legend_set['$ID_NAME'] = row['ClassName']
            legend_set['Name']     = cache.translate(row['Name'])
            legend_set['Set']      = row['LegendGroup'].split('/')
            legend_set['Pieces']   = row['MaxOptionCount']

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
                    legend_set['Bonus'][piece]['Effect'] = cache.translate(row['EffectDesc_%s' % (nth)])

                if row['SetItemSkill_%s' % (nth)] != '':
                    legend_set['Bonus'][piece]['Skill']  = row['SetItemSkill_%s' % (nth)]

                    skill = {}

                    skill['$ID_NAME'] = legend_set['Bonus'][piece]['Skill']
                    skill['Type']     = 'LEGEND_SET'

                    cache.data['skills'][skill['$ID_NAME']] = skill