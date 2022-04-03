"""
IES Parser for Classes.

@author: Temperantia
@credit: Temperantia, Nodius
"""

from csv import DictReader as IESReader
from logging import getLogger
from os.path import exists, join
from typing import Callable

LOG = getLogger('Parse.Classes')

def parse_classes(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    LOG.info('Parsing Classes from job.ies ...')

    ies_path = join(root, 'ies.ipf', 'job.ies')

    if not exists(ies_path):
        LOG.warning('File not found: job.ies')
        return
    
    class_data = data['classes']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            job = {}

            job['$ID']          = row['ClassID']
            job['$ID_NAME']     = row['ClassName']
            job['Name']         = translate(row['Name'])
            job['InternalName'] = row['EngName']
            job['Icon']         = find_icon(row['Icon'])
            job['Description']  = translate(row['Caption1'])
            job['Tree']         = row['CtrlType']

            job['Starter']  = row['Rank'] == '1'
            job['Hidden']   = row['HiddenJob'] == 'YES'
            job['Disabled'] = row['EnableJob'] == 'NO'

            job['Stat_CON'] = int(row['CON'])
            job['Stat_STR'] = int(row['STR'])
            job['Stat_INT'] = int(row['INT'])
            job['Stat_DEX'] = int(row['DEX'])
            job['Stat_SPR'] = int(row['MNA'])

            job['Costume'] = row['DefaultCostume']

            class_data[job['$ID_NAME']] = job