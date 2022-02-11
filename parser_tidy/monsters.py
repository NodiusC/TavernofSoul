# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 20:11:07 2021

@author: Intel
"""

import csv
import logging
import luautil
import re

from os.path import exists, join
from cache import TOSParseCache as Cache

LOG = logging.getLogger('Parse.Monsters')
LOG.setLevel(logging.INFO)

class TOSMonsterRace():
    BEAST   = 0
    DEMON   = 1
    INSECT  = 2
    ITEM    = 3
    MUTANT  = 4
    PLANT   = 5
    VELNAIS = 6

    @staticmethod
    def value_of(string):
        try:
            return {
                'WIDLING' : 'BEAST',
                'VELNIAS' : 'DEMON',
                'KLAIDA'  : 'INSECT',
                'ITEM'    : 'ITEM',
                'PARAMUNE': 'MUTANT',
                'FORESTER': 'PLANT',
                'VELNAIS' : 'VELNAIS',
                ''        : ''

            }[string.upper()]
        except:
            return string.upper()

monster_constants     = {}
statbase_monster      = {} # The content of the variable appears unused
statbase_monster_type = {} # The content of the variable appears unused
statbase_monster_race = {} # The content of the variable appears unused

def parse(cache: Cache = None):
    if cache == None:
        cache = Cache()

        cache.build('jtos')
    
    luautil.init(cache)

    parse_statbase(cache, 'monster_const.ies',         monster_constants)
    parse_statbase(cache, 'statbase_monster.ies',      statbase_monster)      # The content of the variable appears unused
    parse_statbase(cache, 'statbase_monster_type.ies', statbase_monster_type) # The content of the variable appears unused
    parse_statbase(cache, 'statbase_monster_race.ies', statbase_monster_race) # The content of the variable appears unused

    parse_skills(cache)

    for file in cache.MONSTER_IES:
        parse_monsters(cache, file)

    parse_drops(cache)

def parse_drops(cache: Cache):
    for monster in cache.data['monsters'].values():
        file_name = monster['$ID_NAME'] + '.ies'

        LOG.info('Parsing Drops from %s', file_name)

        ies_path = join(cache.PATH_INPUT_DATA, 'ies_drop.ipf', file_name)

        if not exists(ies_path):
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                if row['ItemClassName'] == '':
                    continue
                
                if row['ItemClassName'] not in cache.data['items']:
                    LOG.warning('Item Drop Missing: %s', row['ItemClassName'])
                    continue

                drop = {}

                drop['Item']      = row['ItemClassName']
                drop['Monster']   = monster['$ID_NAME']
                drop['Chance']    = float(int(row['DropRatio']) / 100.0)
                drop['MinSilver'] = int(row['Money_Min'])
                drop['MaxSilver'] = int(row['Money_Max'])

                cache.data['monster_drops'].append(drop)

def parse_monsters(cache: Cache, file_name: str):
    LOG.info('Parsing Characters from %s ...', file_name)

    LUA_RUNTIME = luautil.LUA_RUNTIME

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

    if not exists(ies_path):
        LOG.warning('File not found: %s', file_name)
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            # HOTFIX: These properties need to be calculated before the remaining ones
            row['Lv'] = int(row['Level']) if int(row['Level']) > 1 else 1

            # Inject Constants (Twice)
            for _ in range(2):
                for k, v in monster_constants[1].items():
                    if (k != 'ClassID' and k != 'Lv'):
                        if v in LUA_RUNTIME and LUA_RUNTIME[v] is not None:
                            row[k] = LUA_RUNTIME[v](row)
                        else:
                            if k not in row:
                                row[k] = v

            monster = {}

            monster['$ID']         = int(row['ClassID'])
            monster['$ID_NAME']    = row['ClassName']
            monster['Description'] = cache.translate(row['Desc'])
            monster['Name']        = cache.translate(row['Name'])
            monster['Type']        = row['GroupName']
            monster['Icon']    = cache.parse_entity_icon(row['Icon']) if row['Icon'] != 'ui_CreateMonster' else None
            monster['SkillType']   = row['SkillType']

            if monster['Type'] == 'NPC':
                monster['Icon'] = cache.parse_entity_icon(row['MinimapIcon']) if row['MinimapIcon'] else monster['Icon']

                cache.data['npcs'][monster['$ID_NAME']] = monster

            else:
                monster['Race']    = TOSMonsterRace.value_of(row['RaceType'])
                monster['Element'] = row['Attribute']
                monster['Armor']   = row['ArmorMaterial'] if row['ArmorMaterial'] != 'Iron' else 'Plate'
                monster['Size']    = row['Size'] if row['Size'] else None

                monster['Rank']     = row['MonRank']
                monster['Level']    = int(row['Lv'])
                monster['EXP']      = int(LUA_RUNTIME['SCR_GET_MON_EXP'](row))    if monster['Level'] < 999 else 0
                monster['EXPClass'] = int(LUA_RUNTIME['SCR_GET_MON_JOBEXP'](row)) if monster['Level'] < 999 else 0

                monster['Stat_CON'] = int(row['CON'])
                monster['Stat_DEX'] = int(row['DEX'])
                monster['Stat_INT'] = int(row['INT'])
                monster['Stat_SPR'] = int(row['MNA'])
                monster['Stat_STR'] = int(row['STR'])

                monster['Stat_HP'] = int(row['MHP'])
                monster['Stat_SP'] = int(row['MSP'])

                monster['Stat_ATTACK_PHYSICAL_MIN'] = int(row['MINPATK'])
                monster['Stat_ATTACK_PHYSICAL_MAX'] = int(row['MAXPATK'])
                monster['Stat_ATTACK_MAGICAL_MIN']  = int(row['MINMATK'])
                monster['Stat_ATTACK_MAGICAL_MAX']  = int(row['MAXMATK'])
                monster['Stat_CriticalDamage']      = int(LUA_RUNTIME['SCR_Get_MON_CRTATK'](row))

                monster['Stat_DEFENSE_PHYSICAL'] = int(row['DEF'])
                monster['Stat_DEFENSE_MAGICAL']  = int(row['MDEF'])

                monster['Stat_CriticalRate']     = int(LUA_RUNTIME['SCR_Get_MON_CRTHR'](row))
                monster['Stat_CriticalDefense']  = int(LUA_RUNTIME['SCR_Get_MON_CRTDR'](row))
                monster['Stat_Accuracy']         = int(LUA_RUNTIME['SCR_Get_MON_HR'](row))
                monster['Stat_Evasion']          = int(LUA_RUNTIME['SCR_Get_MON_DR'](row))
                monster['Stat_BlockPenetration'] = int(LUA_RUNTIME['SCR_Get_MON_BLK_BREAK'](row))
                monster['Stat_BlockRate']        = int(LUA_RUNTIME['SCR_Get_MON_BLK'](row))
                
                monster['Link_Items'] = []
                monster['Link_Maps']  = []

                cache.data['monsters'][monster['$ID_NAME']] = monster

def parse_skills(cache: Cache):
    LOG.info('Parsing Monster Skills from skill_mon.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'skill_mon.ies')

    if not exists(ies_path):
        LOG.warning('File not found: skill_mon.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            skill = {}

            skill['$ID']       = row['ClassID']
            skill['$ID_NAME']  = row['ClassName']
            skill['Name']      = cache.translate(row['Name'])
            skill['Attribute'] = row['Attribute']
            skill['SFR']       = row['SklFactor']     if 'SklFactor' in row else 0
            skill['HitCount']  = row['SklHitCount']
            skill['AAR']       = row['SklSR']
            skill['Cooldown']  = row['BasicCoolDown'] if 'BasicCoolDown' in row else 0

            if skill['$ID_NAME'] in cache.data['xml_skills']:
                skill['TargetBuffs'] = cache.data['xml_skills'][skill['$ID_NAME']]['TargetBuffs']

            type_skill = re.match('(?:Mon_)?(\S+)(?:_(?:Attack|Skill)_?\d?)', skill['$ID_NAME'])

            if type_skill is None:
                LOG.warning('%s does not share a naming pattern and cannot be matched through Skill Type', skill['$ID_NAME'])
                type_skill = skill['$ID_NAME']
            else:
                type_skill = type_skill.group(1)

            if type_skill not in cache.data['monster_skills']:
                cache.data['monster_skills'][type_skill] = []

            cache.data['monster_skills'][type_skill].append(skill)

def parse_statbase(cache: Cache, file_name: str, destination: dict):
    LOG.info('Parsing Stat Base from %s ...', file_name)

    ies_path   = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)
    ies_file   = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')

    for row in ies_reader:
        destination[int(row['ClassID'])] = row

    ies_file.close()