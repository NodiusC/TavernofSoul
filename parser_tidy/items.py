# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 11:18:38 2021

@author: Temperantia
"""

import csv
import io
import logging
import re
import luautil
import os
import parse_xac
import xml.etree.ElementTree as ET

from cache import TOSParseCache as Cache
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

        cache.cubes_by_stringarg = {}
        cache.equipment_sets     = {}

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

    parse_card_battle(cache)
    
    parse_cubes(cache)
    parse_links_collections(cache)
    
    parse_gems(cache)
    parse_gems_bonus(cache)
    
    parse_links_skills(cache)
    parse_links_recipes(cache)
    
    parse_books_dialog(cache)

def parse_items(cache: Cache, file_name: str):
    LOG.info('Parsing Items from %s...', file_name)

    try:
        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)
    except:
        LOG.warning('File not found: %s', file_name)
        return
   
    ies_file   = io.open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')
    
    for row in ies_reader:
        item_type = row['GroupName'].upper() if 'GroupName' in row else None 
        item_type = row['Category'].upper() if 'Category' in row and row['Category'] != '' else item_type

        obj = {}

        obj['$ID']                   = str(row['ClassID'])
        obj['$ID_NAME']              = row['ClassName']
        obj['Description']           = cache.translate(row['Desc']) if 'Desc' in row else None
        obj['Icon']                  = cache.parse_entity_icon(row['Icon'])
        obj['Name']                  = cache.translate(row['Name']) if 'Name' in row else None
        obj['Grade']                 = row['ItemGrade'] if 'ItemGrade' in row and row['ItemGrade'] != '' else 1
        obj['Price']                 = row['SellPrice']
        obj['TimeCoolDown']          = float(int(row['ItemCoolDown']) / 1000) if 'ItemCoolDown' in row else None
        obj['TimeLifeTime']          = float(int(row['LifeTime'])) if 'LifeTime' in row else None
        obj['Tradability']           = '%s%s%s%s' % (
            'T' if row['MarketTrade'] == 'YES' else 'F', # Market
            'T' if row['UserTrade']   == 'YES' else 'F', # Players
            'T' if row['ShopTrade']   == 'YES' else 'F', # Shop
            'T' if row['TeamTrade']   == 'YES' else 'F', # Team Storage
        )
        obj['Type']                  = item_type
        obj['Weight']                = float(row['Weight']) if 'Weight' in row else ''

        obj['Link_Collections']      = []
        obj['Link_Cubes']            = []
        obj['Link_Maps']             = []
        obj['Link_Maps_Exploration'] = []
        obj['Link_Monsters']         = []
        obj['Link_RecipeTarget']     = []
        obj['Link_RecipeMaterial']   = []
        
        if item_type == 'CARD':
            obj['IconTooltip'] = cache.parse_entity_icon(row['TooltipImage'])
            obj['TypeCard']    = row['CardGroupName']

        if item_type == 'CUBE':
            cache.data['cube_contents'][row['StringArg']] = {'Cube': row['ClassName'], 'Contents': {}}

        # HOTFIX: 2021 Savinose Dysnai
        if item_type in ['ARMOR', 'WEAPON'] and re.match('^2021_NewYear_Disnai_.+_box$', row['ClassName']):
            obj['Type'] = 'PREMIUM'
        
        # HOTFIX: Event Weapon Boxes
        if item_type == 'WEAPON' and re.match('^(?:(?!2021).)*_?(?:box|SelectBox)_?.*$', row['ClassName']):
            obj['Type'] = 'EVENT'
        
        # HOTFIX: [Event] Enchant Jewel Box
        if item_type == 'CONSUME':
            obj['Type'] = 'EVENT'
        
        cache.data['items'][obj['$ID_NAME']] = obj
    
    ies_file.close()

def parse_equipment(cache: Cache, file_name: str):
    LOG.info('Parsing Equipment from %s ...', file_name)

    try:
        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)
    except:
        LOG.warning('File not found: %s', file_name)
        return
    
    ies_file   = io.open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')
    
    LUA_RUNTIME = luautil.LUA_RUNTIME

    for row in ies_reader:
        if str(row['ClassName']) not in cache.data['items']:
            continue
        
        item_grade          = cache.data['grade_ratios'][int(row['ItemGrade'])]
        item_type_equipment = row['ClassType']

        obj = cache.data['items'][str(row['ClassName'])]
        
        obj['Type'] = 'EQUIPMENT'

        # Calculate all properties using in-game formulas
        tooltip_script = row['RefreshScp']

        if 'MarketCategory' in row:
            tooltip_script = 'SCR_REFRESH_ACC'     if not tooltip_script and 'Accessory_' in row['MarketCategory'] else tooltip_script
            tooltip_script = 'SCR_REFRESH_ARMOR'   if not tooltip_script and 'Armor_'     in row['MarketCategory'] else tooltip_script
            tooltip_script = 'SCR_REFRESH_HAIRACC' if not tooltip_script and 'HairAcc_'   in row['MarketCategory'] else tooltip_script
            tooltip_script = 'SCR_REFRESH_WEAPON'  if not tooltip_script and ('Weapon_' in row['MarketCategory'] or 'ChangeEquip_' in row['MarketCategory']) else tooltip_script

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
        
        obj['Unidentified']       = int(row['NeedAppraisal']) == 1
        obj['UnidentifiedRandom'] = int(row['NeedRandomOption']) == 1

        obj['Link_Set'] = None

        # HOTFIX: if it's a Rapier, use THRUST as the TypeAttack
        # if obj['TypeEquipment'] == TOSEquipmentType.RAPIER:
        #     obj['TypeAttack'] = TOSAttackType.MELEE_THRUST

        # HOTFIX: Agny Necklace
        if 'ADD_FIRE' in row['BasicTooltipProp'].split(','):
            row['ADD_FIRE'] = floor(obj['Level'] * (int(item_grade['BasicRatio']) / 100.0))

        # Anvil
        reinf = 'GET_REINFORCE_131014_PRICE' if 'GET_REINFORCE_PRICE' not in LUA_RUNTIME and 'GET_REINFORCE_131014_PRICE' in LUA_RUNTIME else 'GET_REINFORCE_PRICE'
        
        if (obj['Grade'] != 6) and reinf!= None: #goddess!
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
    
    ies_file.close()

def parse_goddess_reinforcement(cache: Cache):
    files = cache.EQUIPMENT_REINFORCE_IES

    global goddess_atk_list

    for file_name in files:
        try:
            ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)
        except:
            LOG.warning('File not found: %s', file_name)
            continue
        
        ies_file   = io.open(ies_path, 'r', encoding = 'utf-8')
        ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')

        goddess_atk_list[files[file_name]] = next(ies_reader)

        ies_file.close()

def parse_grade_ratios(cache: Cache):
    LOG.info('Parsing Grade Ratios from item_grade.ies')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'item_grade.ies')

    if not exists(ies_path):
        LOG.warning('File not found: item_grade.ies')
        return

    ies_file   = io.open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')

    grade_ratios = {}

    for row in ies_reader:
        grade_ratios[int(row['Grade'])] = row

    cache.data['grade_ratios'] = grade_ratios

    ies_file.close()

def parse_equipment_sets(cache: Cache):
    LOG.info('Parsing Equipment Sets from setitem.ies')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'setitem.ies')

    if not exists(ies_path):
        LOG.warning('File not found: setitem.ies')
        return
    
    ies_file   = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')

    for row in ies_reader:
        obj = {}

        obj['$ID']      = str(row['ClassID'])
        obj['$ID_NAME'] = row['ClassName']
        obj['Name']     = cache.translate(row['Name']) if 'Name' in row else None

        # Parse Bonus
        obj['Bonus2'] = cache.translate(row['EffectDesc_2']) if row['EffectDesc_2'] != '' else None
        obj['Bonus3'] = cache.translate(row['EffectDesc_3']) if row['EffectDesc_3'] != '' else None
        obj['Bonus4'] = cache.translate(row['EffectDesc_4']) if row['EffectDesc_4'] != '' else None
        obj['Bonus5'] = cache.translate(row['EffectDesc_5']) if row['EffectDesc_5'] != '' else None
        obj['Bonus6'] = cache.translate(row['EffectDesc_6']) if row['EffectDesc_6'] != '' else None
        obj['Bonus7'] = cache.translate(row['EffectDesc_7']) if row['EffectDesc_7'] != '' else None

        obj['Set_Items'] = []

        # Parse Set Items
        for i in range(1, 8):
            item_name = row['ItemName_' + str(i)]

            if item_name == '' or item_name not in cache.data['items']:
                continue

            obj['Set_Items'].append(item_name)

        cache.data['equipment_sets'][obj['$ID_NAME']] = obj

    ies_file.close()

def parse_card_battle(cache: Cache):
    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'cardbattle.ies')

    if not exists(ies_path):
        LOG.warning('File not found: cardbattle.ies')
        return
    
    ies_file   = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')

    for row in ies_reader:
        obj = cache.data['items'][row['ClassName']]

        obj['Stat_Height'] = int(row['Height'])
        obj['Stat_Legs']   = int(row['LegCount'])
        obj['Stat_Weight'] = int(row['BodyWeight'])

    ies_file.close()

def parse_cubes(cache: Cache):
    LOG.info('Parsing Cubes from reward_ratio_open_list.ies')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'reward_ratio_open_list.ies')

    if not exists(ies_path):
        LOG.warning('File not found: reward_ratio_open_list.ies')
        return
    
    ies_file   = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter = ',', quotechar = '"')

    for row in ies_reader:
        cache.data['cube_contents'][row['Group']]['Contents'][row['ItemName']] = row['Ratio']
    
    ies_file.close()

def parse_links_collections(constants):
    log = logging.getLogger('Parse.Collections')
    log.setLevel(logging.INFO)
    log.info('Parsing items for collections...')
    ies_path = join(constants.PATH_INPUT_DATA, 'ies.ipf', 'collection.ies')
    if(not exists(ies_path)):
       return
    ies_file = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter=',', quotechar='"')

    for row in ies_reader:
        if row['ClassName'] not in constants.data['items']:
            continue

        collection = constants.data['items'][row['ClassName']]
        collection['Type']         = 'COLLECTION'
        if not 'Link_Items' in collection.keys():
            collection['Link_Items'] = []
            collection['Bonus'] = []
        # Parse items
        for i in range(1, 10):
            item_name = row['ItemName_' + str(i)]

            if item_name == '':
                continue

            collection['Link_Items'].append(constants.data['items'][item_name]['$ID_NAME'])

        # Parse bonus
        bonus = row['PropList'].split('/') + row['AccPropList'].split('/')

        for i in bonus:
            if i == '':
                bonus.remove(i)
        if (len(bonus) != 1):
            for i in range(0, len(bonus), 2):
                collection['Bonus'].append([
                    parse_links_items_bonus_stat(bonus[i]),   # Property
                    int(bonus[i + 1])                         # Value
                ])
    ies_file.close()
    return constants

def parse_links_items_bonus_stat(stat):
    return {
        'CON_BM': 'CON',
        'DEX_BM': 'DEX',
        'INT_BM': 'INT',
        'MNA_BM': 'SPR',
        'STR_BM': 'STR',

        'CRTATK_BM': 'Critical Attack',
        'CRTMATK_BM': 'Critical Magic Attack',
        'CRTHR_BM': 'Critical Rate',
        'CRTDR_BM': 'Critical Defense',

        'MHP_BM': 'Maximum HP',
        'MSP_BM': 'Maximum SP',
        'RHP_BM': 'HP Recovery',
        'RSP_BM': 'SP Recovery',

        'DEF_BM': 'Defense',
        'MDEF_BM': 'Magic Defense',
        'MATK_BM': 'Magic Attack',
        'PATK_BM': 'Physical Attack',

        'DR_BM': 'Evasion',
        'HR_BM': 'Accuracy',
        'MHR_BM': 'Magic Amplification',  # ???

        'ResDark_BM': 'Dark Property Resistance',
        'ResEarth_BM': 'Earth Property Resistance',
        'ResHoly_BM': 'Holy Property Resistance',

        'MaxSta_BM': 'Stamina',
        'MaxAccountWarehouseCount': 'Team Storage Slots',
        'MaxWeight_Bonus': 'Weight Limit',
        'MaxWeight_BM': 'Weight Limit'
    }[stat]


def parse_gems(constants):
    log = logging.getLogger('Parse.Gems')
    log.setLevel(logging.INFO)
    log.info('Parsing gems...')

    ies_path = join(constants.PATH_INPUT_DATA, 'ies.ipf', 'item_gem.ies')
    if(not exists(ies_path)):
       return
    ies_file = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter=',', quotechar='"')

    for row in ies_reader:
        obj = constants.data['items'][row['ClassName']]
        obj['BonusBoots'] = []
        obj['BonusGloves'] = []
        obj['BonusSubWeapon'] = []
        obj['BonusTopAndBottom'] = []
        obj['BonusWeapon'] = []
        obj['TypeGem'] = row['EquipXpGroup']
    ies_file.close()
    return constants

def parse_gems_bonus(constants):
    log = logging.getLogger('Parse.Gem.Bonus')
    log.setLevel(logging.INFO)
    log.info('Parsing gems bonus...')

    xml_path = join(constants.PATH_INPUT_DATA, 'xml.ipf', 'socket_property.xml')
    if(not exists(xml_path)):
       return
    xml = ET.parse(xml_path).getroot()

    SLOTS = ['TopLeg', 'HandOrFoot', 'MainOrSubWeapon']

    for item in xml:
        try:
            gem = constants.data['items'][item.get('Name')]
        except:
            logging.warning('gem not found {}'.format(item.get('Name')))
            continue

        for level in item:
            if level.get('Level') == '0':
                continue

            for slot in SLOTS:
                bonus = level.get('PropList_' + slot)
                penalty = level.get('PropList_' + slot + '_Penalty')

                for slot in (slot.split('Or') if 'Or' in slot else [slot]): # support for Re:Build 2-in-1 slots
                    for prop in [bonus, penalty]:
                        if prop is not None and prop != 'None':
                            if gem['TypeGem'] == 'Gem_Skill':
                                gem['Bonus' + parse_gems_slot(slot)].append({
                                    'Stat': constants.translate(prop).replace('OptDesc/', '')
                                })
                            elif gem['TypeGem'] == 'Gem':
                                prop_slot = prop.split('/')

                                stat ='ADD_' + prop_slot[0]
                                stat = prop_slot[0] if stat is None else stat

                                gem['Bonus' + parse_gems_slot(slot)].append({
                                    'Stat': stat,
                                    'Value': int(prop_slot[1])
                                })
            # constants.data['items'][gem['$ID']] = gem


def parse_gems_slot(key):
    return {
        'Foot': 'Boots',
        'Hand': 'Gloves',
        'Main': 'Weapon',
        'SubWeapon': 'SubWeapon',
        'TopLeg': 'TopAndBottom',
        'Weapon': 'Weapon',
    }[key]

def parse_links_skills(constants):
    log = logging.getLogger('Parse.Gem.Links')
    log.setLevel(logging.INFO)
    log.info('Parsing skills for gems...')

    for gem in constants.data['items'].values():
        if gem['Type'] != 'GEM':
            continue
        skill = gem['$ID_NAME'][len('Gem_'):]
        if (skill not in constants.data['skills_by_name']):
            logging.debug('skills missing : %s', skill)
            continue
        skill = constants.data['skills_by_name'][skill]['$ID']
        gem['Link_Skill'] = skill
        constants.data['items'][gem['$ID_NAME']] = gem
        


def parse_links_recipes(constants):
    log = logging.getLogger('Parse.Recipe.Links')
    log.setLevel(logging.INFO)
    log.info('Parsing items for recipes...')

    ies_path = join(constants.PATH_INPUT_DATA, 'ies.ipf', 'recipe.ies')
    if(not exists(ies_path)):
       return
    ies_file = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter=',', quotechar='"')
    for row in ies_reader:
        recipe = constants.data['items'][row['ClassName']]
        if row['TargetItem'] in constants.data['items']:
            recipe['Link_Target'] = constants.data['items'][row['TargetItem']]['$ID_NAME']
        else:
            log.warning('recipe target not found {}'.format( row['TargetItem']))
            continue
        recipe['Name'] = 'Recipe - Unknown'
        recipe['Type'] = 'RECIPES'
        if recipe['Link_Target'] is not None:
            recipe['Name'] = 'Recipe - ' + constants.data['items'][row['TargetItem']]['Name']

        # Parse ingredients
        for i in range(1, 6):
            if row['Item_' + str(i) + '_1'] == '':
                continue

            obj = {}
            if row['Item_' + str(i) + '_1'] not in constants.data['items'].keys():
                logging.warn('missing item {} for recipe {}'.format(row['Item_' + str(i) + '_1'], recipe['Name']))
                continue
            
            obj['Item'] = constants.data['items'][row['Item_' + str(i) + '_1']]['$ID_NAME']
            obj['Quantity'] = int(row['Item_' + str(i) + '_1_Cnt'])
            
            if 'Link_Materials' not in recipe.keys():
                recipe['Link_Materials'] = []
                
            recipe['Link_Materials'].append(obj)

    ies_file.close()

def parse_gem_bernice(constants):
    file = 'item_gem_relic.ies'
    logging.debug('Parsing bernice gems (ep13)...')
    
    ies_path = join(constants.PATH_INPUT_DATA, 'ies.ipf',file)
    ies_file = open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter=',', quotechar='"')
    rows = []
    for row in ies_reader:
        rows.append(row)
    ies_file.close()
    return constants


def parse_books_dialog(constants):
    logging.debug('Parsing books dialog...')

    ies_path = join(constants.PATH_INPUT_DATA, 'ies_client.ipf', 'dialogtext.ies')
    if(not exists(ies_path)):
       return
    ies_file = io.open(ies_path, 'r', encoding = 'utf-8')
    ies_reader = csv.DictReader(ies_file, delimiter=',', quotechar='"')
    b = []
    for row in ies_reader:
        if row['ClassName'] not in constants.data['items']:
            continue
        book = constants.data['items'][row['ClassName']]
        if 'Text' not in book:
            book['Text'] = None
        
        book['Text'] = constants.translate(row['Text'])
        b.append(book)
    
    ies_file.close()

def parse_goddess_EQ(c):
    LUA_RUNTIME = luautil.LUA_RUNTIME
    LUA_SOURCE = luautil.LUA_SOURCE
    func_list = {'setting_lv470_material_acc' : 470 ,
                 'setting_lv470_material_armor' : 470,
                 'setting_lv460_material' : 460,
                 }
    #mat_list_by_lv[460][1][seasonCoin]
    #mat_list_by_lv[lv]['armor'][1][seasonCoin] = 263
    mat  = {
            460: { i : {} for i in range(1, 31) },
            470: {
                'acc' : {i : {} for i in range(1, 31) },
                'armor': {i : {} for i in range(1, 31) }
                }
        }
    for func in func_list:
        lv = func_list[func]
        if func not in LUA_RUNTIME:
            continue
        LUA_RUNTIME[func](mat)
    a = mat[460] 
    mat[460]  = {'armor' : a}
    c.data['goddess_reinf_mat'] = mat
    
    ies_list = {'item_goddess_reinforce.ies' : 460, 
                'item_goddess_reinforce_470.ies' : 470}
    objs = {}
    for ies in ies_list:
        file_name = ies.lower()
        try:
            ies_path= join(c.PATH_INPUT_DATA, 'ies.ipf', file_name)
        except:
            continue
        ies_file = io.open(ies_path, 'r', encoding='utf-8')
        ies_reader = csv.DictReader(ies_file, delimiter=',', quotechar='"')
        obj  = []
        for row in ies_reader:
            obj.append(row)
        objs[ies_list[ies]] = obj
        c.data['goddess_reinf'][ies_list[ies]] = obj
    
    
    
