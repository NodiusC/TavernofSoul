# -*- coding: utf-8 -*-
"""
IES Parser for Items.

Created on Mon Sep 20 11:18:38 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

import csv
import logging
import re
from os.path import exists, join

from lxml import etree as XML

import constants.ies as IES
import constants.stats as Stats
import constants.visions as Visions
import luautil
import parse_xac
from cache import TOSParseCache as Cache

TRADE = ['Shop', 'Market', 'Team', 'User']
TREE  = ['Char1', 'Char2', 'Char3', 'Char4', 'Char5']

VISION_XPATH = './dic_data[contains(@FilenameWithKey, \'tooltip_%s_Data_0\')]'
BOLDED       = '{nl} {nl}{@st66d}{s15}'

LOG = logging.getLogger('Parse.Items')
LOG.setLevel(logging.INFO)

goddess_atk_list = {}

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
                item = row['ItemName_%s' % i]

                if item == '':
                    continue
                
                if item not in cache.data['items']:
                    LOG.warning('Collectible Item Missing: %s', item)
                    continue

                collection['Collectables'].append(item)
            
            if 'Bonus' not in collection:
                collection['Bonus'] = {}

            # Parse Collection Completion Bonus
            for bonus in re.findall('/?(\S+?)/(\S+?)/?', '%s/%s' % (row['PropList'], row['AccPropList'])):
                collection['Bonus'][Stats.COLLECTION[bonus[0]]] = int(bonus[1])

def parse_cosplay(cache: Cache):
    LOG.info('Parsing Costume Transformations from item_skillmake_costume.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'item_skillmake_costume.ies')

    if not exists(ies_path):
        LOG.warning('File not found: item_skillmake_costume.ies')
        return

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in cache.data['items']:
                continue

            transformation = {}

            transformation['Theme'] = row['Theme']
            transformation['Skill'] = row['SkillName']
            transformation['Buff']  = row['BuffName']

            cache.data['items'][row['ClassName']]['Transformation'] = transformation

            skill = {}

            skill['$ID_NAME'] = transformation['Skill']
            skill['Type']     = 'COSTUME'

            cache.data['skills'][skill['$ID_NAME']] = skill

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

def parse_equipment(cache: Cache):
    LUA_RUNTIME = luautil.LUA_RUNTIME

    xml_path = join(cache.PATH_INPUT_DATA, 'language.ipf', 'DicIDTable.xml')

    if exists(xml_path):
        xml = XML.parse(xml_path, XML.XMLParser(recover = True))
    else:
        LOG.warning('File not found: DicIDTable.xml')
        xml = XML.Element('DicIDTable')

    for file_name in IES.EQUIPMENT:
        LOG.info('Parsing Equipment from %s ...', file_name)

        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                equipment = __create_item(cache, row)
                
                equipment['Type']          = 'EQUIPMENT'
                equipment['TypeAttack']    = row['AttackType']
                equipment['TypeEquipment'] = row['ClassType'].upper()
                equipment['Level']         = row['ItemLv'] if row['ItemLv'] > 0 else equipment['RequiredLevel']
                equipment['Material']      = row['Material']
                equipment['RequiredTree']  = 'TTTTT' if 'All' in row['UseJob'] else ''.join(['T' if tree in row['UseJob'] else 'F' for tree in TREE])
                equipment['RequiredClass'] = row['JobOnly']
                equipment['Gender']        = row['UseGender']

                # Generate attack and defense of equipment into data
                if row['RefreshScp'] != '':
                    LUA_RUNTIME[row['RefreshScp']](row)
                
                equipment['MAXPATK'] = int(row['MAXATK']) if 'MAXATK' in row else 0
                equipment['MINPATK'] = int(row['MINATK']) if 'MINATK' in row else 0
                equipment['MATK']    = int(row['MATK'])   if 'MATK'   in row else 0
                equipment['PDEF']    = int(row['DEF'])    if 'DEF'    in row else 0
                equipment['MDEF']    = int(row['MDEF'])   if 'MDEF'   in row else 0

                equipment['Sockets']    = int(row['BaseSocket'])
                equipment['MaxSockets'] = int(row['MaxSocket_COUNT'])
                equipment['Potential']  = int(row['MaxPR'])
                equipment['Durability'] = float(int(row['MaxDur']) / 100) if row['MaxDur'] > 0 else -1

                equipment['Dismantlable'] = row['DecomposeAble'] == 'YES'
                equipment['Extractable']  = row['Extractable']   == 'Yes'

                stats = {}

                for stat in Stats.EQUIPMENT:
                    if stat not in row:
                        continue

                    if stat in __LEGACY_STAT_SOLVER:
                        value = __LEGACY_STAT_SOLVER[stat](row)

                        if value == 0:
                            continue

                    else:
                        if row[stat] == '' or row[stat] == '0':
                            continue
                        
                        value = int(row[stat])

                    stats[stat] = value

                equipment['Bonus'] = list(stats.items())

                # Non-Stat Bonuses
                if row['OptDesc'] != '':
                    equipment['Bonus'].append(('', cache.translate(row['OptDesc'])))
                
                equipment['model'] = parse_xac.eq_model_name(row, cache)

                # Visions
                if equipment['TypeEquipment'] == 'ARCANE':
                    equipment['TypeEquipment'] = 'VISION'

                    if row['NumberArg1'] == '1':
                        equipment['VisionClass'] = Visions.VISION_CLASS[equipment['$ID_NAME']]
                    else:
                        equipment['VisionClass'] = Visions.VISION_CLASS[equipment['$ID_NAME'][:-4]]

                    # Base Effect
                    if 'AdditionalOption_1' in row and row['AdditionalOption_1'] != '':
                        equipment['Bonus'].append(('VSN_BASE', cache.translate(xml.xpath(VISION_XPATH % row['AdditionalOption_1']).get('kr'))))

                    # Final Effect
                    if 'AdditionalOption_2' in row and row['AdditionalOption_2'] != '':
                        equipment['Bonus'].append(('VSN_FINAL', cache.translate(xml.xpath(VISION_XPATH % row['AdditionalOption_2']).get('kr'))).replace(BOLDED, ''))

                # Hair Accessories
                if row['ReqToolTip'][:-1] == '헤어 코스튬':
                    equipment['TypeEquipment'] = 'HAIR_ACC_%s' % row['ReqToolTip'][-1:]

                cache.data['items'][equipment['$ID_NAME']] = equipment

def parse_gems(cache: Cache):
    xml_path = join(cache.PATH_INPUT_DATA, 'xml.ipf', 'socket_property.xml')

    if exists(xml_path):
        xml = XML.parse(xml_path, XML.XMLParser(recover = True))
    else:
        LOG.warning('File not found: socket_property.xml')
        xml = XML.Element('SocketProperty')

    for file_name in IES.GEM:
        LOG.info('Parsing Gems from %s ...', file_name)
        
        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                gem = __create_item(cache, row)

                gem['TypeGem'] = row['EquipXpGroup'].upper() if gem['Type'] == 'GEM' else gem['Type']
                gem['Type']    = 'GEM'

                if gem['TypeGem'] == 'GEM_RELIC':
                    gem['RelicEffect'] = row['RelicGemOption']

                    # TODO: SFR from LUA ('get_tooltip_%s_arg%s' % (['RelicEffect'], argc))

                elif gem['TypeGem'] == 'GEM_HIGH_COLOR':
                    gem['StatGrowth'] = row['StringArg']

                elif gem['TypeGem'] == 'GEM_SKILL':
                    skill = gem['$ID_NAME'][4:]

                    if skill not in cache.data['skills']:
                        LOG.warning('Skill Missing: %s', skill)
                        continue

                    cache.data['skills'][skill]['Gem'] = gem['$ID_NAME']

                else:
                    item = xml.find('./Item[@Name=\'%s\']' % gem['$ID_NAME'])

                    if item is None:
                        LOG.warning('Gem Levels Missing: %s', gem['$ID_NAME'])
                        continue

                    base = item.find('./Level[@Level=\'0\']')

                    if base is None:
                        continue

                    gain = base.get('PropList_MainOrSubWeapon')        .split('/')[0]
                    lose = base.get('PropList_MainOrSubWeapon_Penalty').split('/')[0]

                    slice_gain = len(gain + '/')
                    slice_lose = len(lose + '/')

                    stats = {}

                    stats[gain] = [0] * 10
                    stats[lose] = [0] * 10

                    for prop in item:
                        try:
                            level = int(prop.get('Level')) - 1
                        except:
                            continue

                        if level < 0:
                            continue

                        stats[gain][level] = prop.get('PropList_MainOrSubWeapon')        [slice_gain:]
                        stats[lose][level] = prop.get('PropList_MainOrSubWeapon_Penalty')[slice_lose:]

                    gem['Stats'] = stats
                
                cache.data['items'][gem['$ID_NAME']] = gem

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
            continue

        obj = []

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                obj.append(row)

        cache.data['goddess_reinf'][ies_list[file_name]] = obj

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

def parse_items(cache: Cache):
    for file_name in IES.ITEM:
        LOG.info('Parsing Items from %s ...', file_name)

        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                item = __create_item(cache, row)
                
                if item['Type'] == 'CARD':
                    item['IconTooltip'] = cache.parse_entity_icon(row['TooltipImage'])
                    item['TypeCard']    = row['CardGroupName'].upper() if 'CardGroupName' in row else 'MASTER_CARD_ALBUM' # HOTFIX: Master Card Albums

                if item['Type'] == 'CUBE':
                    item['TypeCube'] = row['StringArg']

                if item['Type'] == 'DRUG':
                    item['Type'] == 'CONSUMABLE'

                # HOTFIX: 2021 Savinose Dysnai
                if item['Type'] in ['ARMOR', 'WEAPON'] and re.match('^2021_NewYear_Disnai_.+_box$', row['ClassName']):
                    item['Type'] = 'PREMIUM'
                
                # HOTFIX: Event Weapon Boxes
                if item['Type'] == 'WEAPON' and re.match('^(?:(?!2021).)*_?(?:box|SelectBox)_?.*$', row['ClassName']):
                    item['Type'] = 'EVENT'
                
                # HOTFIX: [Event] Enchant Jewel Box
                if item['Type'] == 'CONSUME':
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
            recipe = __create_item(cache, row)

            if row['TargetItem'] not in cache.data['items']:
                LOG.warning('Recipe Product Missing: %s', row['TargetItem'])
                continue

            recipe['Name'] = 'Recipe - %s' % cache.data['items'][row['TargetItem']]['Name']

            product = {}
            
            product['Item']     = row['TargetItem']
            product['Quantity'] = int(row['TargetItemCnt'])

            recipe['Product'] = product

            if 'Materials' not in recipe:
                recipe['Materials'] = []

            for i in range(1, 6):
                item = row['Item_%s_1' % i]

                if item == '':
                    continue
                
                if item not in cache.data['items']:
                    LOG.warning('Recipe Material for %s Missing: %s', row['TargetItem'], item)
                    continue

                material = {}
                
                material['Item']     = item
                material['Quantity'] = int(row['Item_%s_1_Cnt' % i])
                    
                recipe['Materials'].append(material)

            cache.data['items'][recipe['$ID_NAME']] = recipe

def __create_item(cache: Cache, data: dict) -> dict:
    item = {}

    item['$ID']           = str(data['ClassID'])
    item['$ID_NAME']      = data['ClassName']
    item['Name']          = cache.translate(data['Name']) if 'Name' in data else None
    item['Type']          = data['GroupName'].upper()
    item['InternalType']  = item['Type']
    item['Grade']         = int(data['ItemGrade']) if 'ItemGrade' in data and data['ItemGrade'] != '' else 1
    item['Stars']         = int(data['ItemStar'])
    item['Description']   = cache.translate(data['Desc']) if 'Desc' in data else None
    item['RequiredLevel'] = int(data['UseLv'])
    item['Icon']          = cache.parse_entity_icon(data['Icon'])
    item['Weight']        = float(data['Weight'])
    item['Cooldown']      = float(int(data['ItemCoolDown']) / 1000)
    item['Expiration']    = float(data['LifeTime'])
    item['Destroyable']   = data['Destroyable'] == 'YES'
    item['Tradability']   = ''.join(['T' if data['%sTrade' % (target)] == 'YES' else 'F' for target in TRADE])
    item['Price']         = data['Price']
    item['SellPrice']     = data['SellPrice']

    item['Link_Maps']             = []
    item['Link_Maps_Exploration'] = []
    item['Link_Monsters']         = []

    return item

def __resolve_addatk(row: dict) -> int:
    value = 0 if row['Add_Damage_Atk'] == '' else int(row['Add_Damage_Atk'])

    for stat in Stats.ADD_DAMAGE:
        if row[stat] == '' or row[stat] == '0':
            continue

        value += int(row[stat])

    return value

def __resolve_addres(row: dict) -> int:
    value = 0 if row['ResAdd_Damage'] == '' else int(row['ResAdd_Damage'])

    for stat in Stats.ADD_DAMAGE_RESISTANCE:
        if row[stat] == '' or row[stat] == '0':
            continue

        value += int(row[stat])
    
    return value

def __resolve_maxsta(row: dict) -> int:
    value = 0 if row['MSTA'] == '' else int(row['MSTA'])

    if row['RSTA'] != '' and row['RSTA'] != '0':
        value += int(row['RSTA'])

    return value

__LEGACY_STAT_SOLVER = {
    'Add_Damage_Atk': __resolve_addatk, # HOTFIX: Additional Property Damage is Additional Damage
    'ResAdd_Damage' : __resolve_addres, # HOTFIX: Additional Property Damage Resistance is Additional Damage Resistance
    'MSTA'          : __resolve_maxsta  # HOTFIX: Stamina Recovery is Maximum Stamina
}