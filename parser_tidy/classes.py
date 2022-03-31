"""
IES Parser for Classes.

@author: Temperantia
@credit: Temperantia, Nodius
"""

import csv
import logging
from os.path import exists, join

from cache import TOSParseCache as Cache

LOG = logging.getLogger('Parse.Classes')
LOG.setLevel(logging.INFO)

def parse_classes(cache: Cache):
    LOG.info('Parsing Classes from job.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'job.ies')

    if not exists(ies_path):
        LOG.warning('File not found: job.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            job = {}

            job['$ID']          = row['ClassID']
            job['$ID_NAME']     = row['ClassName']
            job['Name']         = cache.translate(row['Name'])
            job['InternalName'] = row['EngName']
            job['Icon']         = cache.get_icon(row['Icon'])
            job['Description']  = cache.translate(row['Caption1'])
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

            cache.data['classes'][job['$ID_NAME']] = job