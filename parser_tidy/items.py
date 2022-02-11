# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 11:18:38 2021

@author: Temperantia
"""

import csv
import logging
import luautil
import parse_xac
import re
import xml.etree.ElementTree as ET

from cache import TOSParseCache as Cache
from constants import COLLECTION_STATS, GEM_STATS
from math import floor
from os.path import exists, join

LOG = logging.getLogger('Parse.Items')
LOG.setLevel(logging.INFO)

EQUIPMENT_STAT_COLUMNS = []

goddess_atk_list       = {}

def parse(cache: Cache = None, from_scratch: bool = True):
    if cache == None:
        cache = Cache()

        cache.build('jtos')
    
    luautil.init(cache)
    
    if (from_scratch):
        cache.data['items'] = {}

        for file in cache.ITEM_IES:
            parse_items(cache, file)

    a = luautil.LUA_RUNTIME['GET_COMMON_PROP_LIST']()

    global EQUIPMENT_STAT_COLUMNS
    EQUIPMENT_STAT_COLUMNS =[a[i] for i in a]
    
    parse_grade_ratios(cache)
    
    parse_goddess_reinforcement(cache)
    
    for i in cache.EQUIPMENT_IES:
        parse_equipment(cache, i)
    
    parse_equipment_sets(cache)
    
    for file in cache.GEM_IES:
        parse_gems(cache, file)
    
    parse_cubes(cache)
    parse_collections(cache)
    parse_recipes(cache)
    parse_books(cache)

    parse_card_battle(cache)

def parse_books(cache: Cache):
    LOG.info('Parsing Books from dialogtext.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies_client.ipf', 'dialogtext.ies')

    if not exists(ies_path):
        LOG.warning('File not found: dialogtext.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue

            # Parse Book Text
            cache.data['items'][row['ClassName']]['Text'] = cache.translate(row['Text'])

def parse_card_battle(cache: Cache):
    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'cardbattle.ies')

    if not exists(ies_path):
        LOG.warning('File not found: cardbattle.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue

            card = cache.data['items'][row['ClassName']]

            card['Stat_Height'] = int(row['Height'])
            card['Stat_Legs']   = int(row['LegCount'])
            card['Stat_Weight'] = int(row['BodyWeight'])

def parse_collections(cache: Cache):
    LOG.info('Parsing Collections from collection.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'collection.ies')

    if not exists(ies_path):
        LOG.warning('File not found: collection.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue

            collection = cache.data['items'][row['ClassName']]

            if 'Collectables' not in collection:
                collection['Collectables'] = []
            
            # Parse Collectible Items
            for i in range(1, 10):
                item = row['ItemName_' + str(i)]

                if item == '':
                    continue
                
                if item not in cache.data['items']:
                    LOG.warning('Collectible Item Missing: %s', item)
                    continue

                collection['Collectables'].append(item)
            
            if 'Bonus' not in collection:
                collection['Bonus'] = {}

            # Parse Collection Completion Bonus
            for bonus in re.findall('/?(\S+?)/(\S+?)/?', row['PropList'] + '/' + row['AccPropList']):
                collection['Bonus'][COLLECTION_STATS[bonus[0]]] = int(bonus[1])

def parse_cubes(cache: Cache):
    LOG.info('Parsing Cubes from reward_ratio_open_list.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'reward_ratio_open_list.ies')

    if not exists(ies_path):
        LOG.warning('File not found: reward_ratio_open_list.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            item = row['ItemName']

            if item == '':
                continue

            if item not in cache.data['items']:
                LOG.warning('Cube Item Missing: %s', item)
                continue

            if row['Group'] not in cache.data['cube_contents']:
                cache.data['cube_contents'][row['Group']] = []

            content = {}

            content['Item']   = item
            content['Chance'] = row['Ratio']

            cache.data['cube_contents'][row['Group']].append(content)

def parse_equipment(cache: Cache, file_name: str):
    LOG.info('Parsing Equipment from %s ...', file_name)

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

    if not exists(ies_path):
        LOG.warning('File not found: %s', file_name)
        return
    
    LUA_RUNTIME = luautil.LUA_RUNTIME

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue
            
            item_grade          = cache.data['grade_ratios'][int(row['ItemGrade'])]
            item_type_equipment = row['ClassType']

            obj = cache.data['items'][row['ClassName']]
            
            obj['Type'] = 'EQUIPMENT'

            # Calculate all properties using in-game formulas
            tooltip_script = row['RefreshScp']

            if 'MarketCategory' in row:
                tooltip_script = 'SCR_REFRESH_ACC'     if not tooltip_script and 'Accessory_' in row['MarketCategory'] else tooltip_script
                tooltip_script = 'SCR_REFRESH_ARMOR'   if not tooltip_script and 'Armor_'     in row['MarketCategory'] else tooltip_script
                tooltip_script = 'SCR_REFRESH_HAIRACC' if not tooltip_script and 'HairAcc_'   in row['MarketCategory'] else tooltip_script
                tooltip_script = 'SCR_REFRESH_WEAPON'  if not tooltip_script and ('Weapon_'   in row['MarketCategory'] or 'ChangeEquip_' in row['MarketCategory']) else tooltip_script

            if tooltip_script:
                try:
                    LUA_RUNTIME[tooltip_script](row)
                except :
                    pass

            # Add additional fields
            obj['AnvilATK']      = []
            obj['AnvilDEF']      = []
            obj['AnvilPrice']    = []
            obj['Bonus']         = []
            obj['Durability']    = -1                    if int(row['MaxDur']) <= 0  else int(row['MaxDur']) / 100
            obj['Grade']         = int(row['ItemGrade']) if row['ItemGrade']   != '' else 1
            obj['Level']         = int(row['ItemLv'])    if int(row['ItemLv']) >  0  else int(row['UseLv'])
            obj['Material']      = row['Material']
            obj['Potential']     = int(row['MaxPR'])
            obj['RequiredClass'] = '%s%s%s%s%s' % (
                'T' if any(j in row['UseJob'] for j in ['All', 'Char1']) else 'F', # Swordsman
                'T' if any(j in row['UseJob'] for j in ['All', 'Char2']) else 'F', # Wizard
                'T' if any(j in row['UseJob'] for j in ['All', 'Char3']) else 'F', # Archer
                'T' if any(j in row['UseJob'] for j in ['All', 'Char4']) else 'F', # Cleric
                'T' if any(j in row['UseJob'] for j in ['All', 'Char5']) else 'F', # Scout
            )
            obj['RequiredLevel'] = int(row['UseLv'])
            obj['Sockets']       = int(row['BaseSocket'])
            obj['SocketsLimit']  = int(row['MaxSocket_COUNT'])
            obj['Stars']         = int(row['ItemStar'])

            try:
                obj['Stat_ATTACK_MAGICAL'] = int(row['MATK']) 
            except:
                obj['Stat_ATTACK_MAGICAL'] = 0

            try:
                obj['Stat_ATTACK_PHYSICAL_MIN'] = int(row['MINATK']) 
            except:
                obj['Stat_ATTACK_PHYSICAL_MIN'] = 0

            try:
                obj['Stat_ATTACK_PHYSICAL_MAX'] = int(row['MAXATK']) if 'MAXATK' in row and row['MAXATK'] != None else 0
            except:
                obj['Stat_ATTACK_PHYSICAL_MAX'] = 0

            try:
                obj['Stat_DEFENSE_MAGICAL'] = int(row['MDEF']) if 'MDEF' in row and row['MDEF'] != None else 0
            except:
                obj['Stat_DEFENSE_MAGICAL'] = 0

            try:
                obj['Stat_DEFENSE_PHYSICAL'] = int(row['DEF']) if 'DEF' in row and row['DEF'] != None else 0
            except:
                obj['Stat_DEFENSE_PHYSICAL'] = 0
        
            if obj['Grade'] == 6 and int(row['UseLv']) in goddess_atk_list and tooltip_script == 'SCR_REFRESH_ACC':
                atk = goddess_atk_list[int(row['UseLv'])]['BasicAccAtk']

                obj['Stat_ATTACK_MAGICAL']      = atk
                obj['Stat_ATTACK_PHYSICAL_MIN'] = atk
                obj['Stat_ATTACK_PHYSICAL_MAX'] = atk

            obj['TypeAttack']    = row['AttackType']
            obj['TypeEquipment'] = item_type_equipment.upper()

            # Hair Accessory 
            if 'ReqToolTip' in row:
                if row['ReqToolTip'][:-1] == '헤어 코스튬':
                    obj['TypeEquipment'] = 'HAIR_ACC_' + row['ReqToolTip'][-1:]
            
            obj['Unidentified']       = int(row['NeedAppraisal'])    == 1
            obj['UnidentifiedRandom'] = int(row['NeedRandomOption']) == 1

            # HOTFIX: Agny Necklace
            if 'ADD_FIRE' in row['BasicTooltipProp'].split(','):
                row['ADD_FIRE'] = floor(obj['Level'] * (int(item_grade['BasicRatio']) / 100.0))

            # Anvil
            reinf = 'GET_REINFORCE_131014_PRICE' if 'GET_REINFORCE_PRICE' not in LUA_RUNTIME and 'GET_REINFORCE_131014_PRICE' in LUA_RUNTIME else 'GET_REINFORCE_PRICE'
            
            # Goddess Grade
            if (obj['Grade'] != 6) and reinf != None:
                if any(prop in row['BasicTooltipProp'] for prop in ['ATK', 'DEF', 'MATK', 'MDEF']):
                    for lv in range(40):
                        row['Reinforce_2'] = lv

                        if any(prop in row['BasicTooltipProp'] for prop in ['DEF', 'MDEF']):
                            obj['AnvilDEF'].append(LUA_RUNTIME['GET_REINFORCE_ADD_VALUE'](None, row, 0, 1))
                            obj['AnvilPrice'].append(LUA_RUNTIME[reinf](row, {}, None))
                        
                        if any(prop in row['BasicTooltipProp'] for prop in ['ATK', 'MATK']):
                            obj['AnvilATK'].append(LUA_RUNTIME['GET_REINFORCE_ADD_VALUE_ATK'](row, 0, 1, None))
                            obj['AnvilPrice'].append(LUA_RUNTIME[reinf](row, {}, None))
                
        
                obj['AnvilPrice'] = [int(value) for value in obj['AnvilPrice'] if value > 0]
                obj['AnvilATK']   = [int(value) for value in obj['AnvilATK'] if value > 0] if len(obj['AnvilPrice']) > 0 else None
                obj['AnvilDEF']   = [int(value) for value in obj['AnvilDEF'] if value > 0] if len(obj['AnvilPrice']) > 0 else None
            
            lua = luautil.lua

            obj['TranscendPrice'] = []

            for lv in range(10):
                row['Transcend'] = 0
                obj['TranscendPrice'].append(LUA_RUNTIME['GET_TRANSCEND_MATERIAL_COUNT'](row, lv))

            # Goddess Grade is special and beyond your understanding
            if (obj['Grade'] == 6):
                obj['TranscendPrice'].append(lua.execute('return get_TC_goddess')(int(row['UseLv']), row['ClassType'], 0, 10))
            
            try:
                obj['TranscendPrice'] = [floor(value) for value in obj['TranscendPrice'] if value > 0]
            except:
                # Goddess Grade is again special and beyond your mortal understanding
                a = [dict(table)['Premium_item_transcendence_Stone'] for table in obj['TranscendPrice'][1:]]
                obj['TranscendPrice'] = [0] + a + [20]
            
            # Bonus
            for stat in EQUIPMENT_STAT_COLUMNS:
                if stat in row:
                    if row[stat] == None:
                        row[stat] = 0
                    
                    value = floor(float(row[stat]))

                    if value != 0:
                        obj['Bonus'].append([stat, value])

            # More Bonus
            if 'OptDesc' in row and len(row['OptDesc']) > 0:
                for bonus in cache.translate(row['OptDesc']).split('{nl}'):
                    bonus = bonus.strip()
                    bonus = bonus[bonus.index('-'):] if '-' in bonus else bonus

                    obj['Bonus'].append(['UNKNOWN', bonus.replace('- ', '').strip()]) # Stat, Value
            
            obj['model'] = parse_xac.eq_model_name(row, cache)

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
            equipment_set['Name']     = cache.translate(row['Name']) if 'Name' in row else None
            equipment_set['SetItems'] = []
            equipment_set['Bonus']    = {}

            for i in range(1, 8):
                n = str(i)

                # Parse Bonus
                equipment_set['Bonus'][n] = cache.translate(row['EffectDesc_' + n]) if row['EffectDesc_' + n] != '' else None

                # Parse Set Items
                item = row['ItemName_' + n]

                if item == '' or item not in cache.data['items']:
                    continue

                equipment_set['SetItems'].append(item)

            cache.data['equipment_sets'][equipment_set['$ID_NAME']] = equipment_set

def parse_gems(cache: Cache, file_name: str):
    LOG.info('Parsing Gems from %s ...', file_name)

    xml_path = join(cache.PATH_INPUT_DATA, 'xml.ipf', 'socket_property.xml')

    if exists(xml_path):
        xml = ET.parse(xml_path).getroot()
    else:
        LOG.warning('File not found: socket_property.xml')
        xml = ET.Element('SocketProperty')
    
    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

    if not exists(ies_path):
        LOG.warning('File not found: %s', file_name)
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue

            gem = cache.data['items'][row['ClassName']]

            gem['TypeGem'] = row['EquipXpGroup'].upper() if gem['Type'] == 'GEM' else gem['Type']
            gem['Type']    = 'GEM'

            if gem['TypeGem'] == 'GEM_RELIC':
                gem['RelicEffect'] = row['RelicGemOption']

                # TODO: SFR from LUA ('get_tooltip_' + ['RelicEffect'] + '_arg' + argc)

            elif gem['TypeGem'] == 'GEM_HIGH_COLOR':
                gem['StatGrowth'] = row['StringArg']

            elif gem['TypeGem'] == 'GEM_SKILL':
                skill = gem['$ID_NAME'][4:]

                if skill not in cache.data['skills']:
                    LOG.warning('Skill Missing: %s', skill)
                    continue

                gem['GemSkill'] = skill

            else:
                item = xml.find('./Item[@Name=\'' + gem['$ID_NAME'] + '\']')

                if item is None:
                    LOG.warning('Gem Levels Missing: %s', gem['$ID_NAME'])
                    continue

                base = item.find('./Level[@Level=\'0\']')

                if base is None:
                    continue

                gain = GEM_STATS[re.match('/?(\S+?)/(\S+?)/?', base.get('PropList_MainOrSubWeapon'))        .group(1)]
                lose = GEM_STATS[re.match('/?(\S+?)/(\S+?)/?', base.get('PropList_MainOrSubWeapon_Penalty')).group(1)]

                stats = {}

                stats[gain] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                stats[lose] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                for prop in item:
                    try:
                        level = int(prop.get('Level')) - 1
                    except:
                        continue

                    if level < 0:
                        continue

                    stats[gain][level] = prop.get('PropList_MainOrSubWeapon')        [len(gain + '/'):]
                    stats[lose][level] = prop.get('PropList_MainOrSubWeapon_Penalty')[len(lose + '/'):]

                gem['Stats'] = stats

def parse_goddess_equipment(cache: Cache):
    LUA_RUNTIME = luautil.LUA_RUNTIME

    functions = {
        'setting_lv460_material'      : 460,
        'setting_lv470_material_armor': 470,
        'setting_lv470_material_acc'  : 470
    }

    materials = {
        460: {
            i: {} for i in range(1, 31)
        },
        470: {
            'acc': {
                i: {} for i in range(1, 31)
            },
            'armor': {
                i: {} for i in range(1, 31)
            }
        }
    }

    for f in functions:
        if f not in LUA_RUNTIME:
            continue

        LUA_RUNTIME[f](materials)
    
    a = materials[460] 

    materials[460]  = {'armor' : a}

    cache.data['goddess_reinf_mat'] = materials
    
    ies_list = {
        'item_goddess_reinforce.ies'    : 460, 
        'item_goddess_reinforce_470.ies': 470
    }

    for file_name in ies_list:
        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            return

        obj = []

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                obj.append(row)

        cache.data['goddess_reinf'][ies_list[file_name]] = obj

def parse_goddess_reinforcement(cache: Cache):
    files = cache.EQUIPMENT_REINFORCE_IES

    global goddess_atk_list

    for file_name in files:
        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            goddess_atk_list[files[file_name]] = next(csv.DictReader(ies_file, delimiter = ',', quotechar = '"'))

def parse_grade_ratios(cache: Cache):
    LOG.info('Parsing Grade Ratios from item_grade.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'item_grade.ies')

    if not exists(ies_path):
        LOG.warning('File not found: item_grade.ies')
        return

    grade_ratios = {}

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            grade_ratios[int(row['Grade'])] = row

    cache.data['grade_ratios'] = grade_ratios

def parse_items(cache: Cache, file_name: str):
    LOG.info('Parsing Items from %s ...', file_name)

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

    if not exists(ies_path):
        LOG.warning('File not found: %s', file_name)
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            item_type = row['GroupName'].upper() if 'GroupName' in row else None 
            item_type = row['Category'].upper() if 'Category' in row and row['Category'] != '' else item_type

            item = {}

            item['$ID']                   = str(row['ClassID'])
            item['$ID_NAME']              = row['ClassName']
            item['Name']                  = cache.translate(row['Name']) if 'Name' in row else None
            item['Type']                  = item_type
            item['InternalType']          = item_type
            item['Grade']                 = row['ItemGrade'] if 'ItemGrade' in row and row['ItemGrade'] != '' else 1
            item['Description']           = cache.translate(row['Desc']) if 'Desc' in row else None
            item['Icon']                  = cache.parse_entity_icon(row['Icon'])
            item['Weight']                = float(row['Weight']) if 'Weight' in row else ''
            item['TimeCoolDown']          = float(int(row['ItemCoolDown']) / 1000) if 'ItemCoolDown' in row else None
            item['TimeLifeTime']          = float(int(row['LifeTime'])) if 'LifeTime' in row else None
            item['Tradability']           = '%s%s%s%s' % (
                'T' if row['MarketTrade'] == 'YES' else 'F', # Market
                'T' if row['UserTrade']   == 'YES' else 'F', # Players
                'T' if row['ShopTrade']   == 'YES' else 'F', # Shop
                'T' if row['TeamTrade']   == 'YES' else 'F', # Team Storage
            )
            item['Price']                 = row['Price']
            item['SellPrice']             = row['SellPrice']

            item['Link_Maps']             = []
            item['Link_Maps_Exploration'] = []
            item['Link_Monsters']         = []
            
            if item_type == 'CARD':
                item['IconTooltip'] = cache.parse_entity_icon(row['TooltipImage'])
                item['TypeCard']    = row['CardGroupName'].upper() if 'CardGroupName' in row else 'MASTER_CARD_ALBUM' # HOTFIX: Master Card Albums

            if item_type == 'CUBE':
                item['TypeCube'] = row['StringArg']

            # HOTFIX: 2021 Savinose Dysnai
            if item_type in ['ARMOR', 'WEAPON'] and re.match('^2021_NewYear_Disnai_.+_box$', row['ClassName']):
                item['Type'] = 'PREMIUM'
            
            # HOTFIX: Event Weapon Boxes
            if item_type == 'WEAPON' and re.match('^(?:(?!2021).)*_?(?:box|SelectBox)_?.*$', row['ClassName']):
                item['Type'] = 'EVENT'
            
            # HOTFIX: [Event] Enchant Jewel Box
            if item_type == 'CONSUME':
                item['Type'] = 'EVENT'
            
            cache.data['items'][item['$ID_NAME']] = item

def parse_recipes(cache: Cache):
    LOG.info('Parsing Recipes from recipe.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'recipe.ies')

    if not exists(ies_path):
        LOG.warning('File not found: recipe.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue

            recipe = cache.data['items'][row['ClassName']]

            if row['TargetItem'] not in cache.data['items']:
                LOG.warning('Recipe Product Missing: %s', row['TargetItem'])
                continue

            recipe['Name'] = 'Recipe - ' + cache.data['items'][row['TargetItem']]['Name']

            product = {}
            
            product['Item']     = row['TargetItem']
            product['Quantity'] = int(row['TargetItemCnt'])

            recipe['Product'] = product

            if 'Materials' not in recipe:
                recipe['Materials'] = []

            for i in range(1, 6):
                item = row['Item_' + str(i) + '_1']

                if item == '':
                    continue
                
                if item not in cache.data['items']:
                    LOG.warning('Recipe Material for %s Missing: %s', row['TargetItem'], item)
                    continue

                material = {}
                
                material['Item']     = item
                material['Quantity'] = int(row['Item_' + str(i) + '_1_Cnt'])
                    
                recipe['Materials'].append(material)