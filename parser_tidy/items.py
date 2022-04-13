# -*- coding: utf-8 -*-
"""
IES Parser for Items.

Created on Mon Sep 20 11:18:38 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

from csv import DictReader as IESReader
from logging import getLogger
from os.path import exists, join
from re import findall, match, split
from typing import Callable

from lxml.html import parse as parse_xml, Element as xml_element

import constants.ies as IES
import luautil
from constants.item import (
    ADD_DAMAGE_STATS            as ADD_ATK_STATS,
    ADD_DAMAGE_RESISTANCE_STATS as ADD_RES_STATS,
    COLLECTION_STATS,
    EQUIPMENT_STATS,
    TRADABILITY,
    VISION_TO_CLASS
)

LOG = getLogger('Parse.Items')

def parse_aether_gems(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    GEM_IES         = IES.GEM_AETHER

    LOG.info('Parsing Aether Gems from %s ...', GEM_IES)
        
    ies_path = join(root, 'ies.ipf', GEM_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', GEM_IES)
        return

    item_data = data['items']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            gem = __create_item(row, translate, find_icon)

            gem['Type']    = 'GEM'
            gem['TypeGem'] = 'GEM_AETHER'
            gem['Stat']    = row['StringArg']

            item_data[gem['$ID_NAME']] = gem

def parse_books(root: str, data: dict, translate: Callable[[str], str]):
    BOOK_IES = IES.BOOK_TEXT

    LOG.info('Parsing Books from %s ...', BOOK_IES)

    ies_path = join(root, 'ies_client.ipf', BOOK_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', BOOK_IES)
        return
    
    item_data = data['items']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in item_data:
                continue

            # Parse Book Text
            item_data[row['ClassName']]['Text'] = translate(row['Text'])

def parse_collections(root: str, data: dict):
    COLLECTION_IES = IES.COLLECTION

    LOG.info('Parsing Collections from %s ...', COLLECTION_IES)

    ies_path = join(root, 'ies.ipf', COLLECTION_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', COLLECTION_IES)
        return
    
    item_data = data['items']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['ClassName'] not in item_data:
                continue

            collection = item_data[row['ClassName']]

            if 'Collectables' not in collection:
                collection['Collectables'] = []
            
            # Parse Collectible Items
            for i in range(1, 10):
                item = row['ItemName_%s' % i]

                if item == '':
                    continue
                
                if item not in item_data:
                    LOG.warning('Collectible Item Missing: %s', item)
                    continue

                collection['Collectables'].append(item)
            
            if 'Bonus' not in collection:
                collection['Bonus'] = {}

            # Parse Collection Completion Bonus
            stats = [stat for stat in split('/+', '%s/%s' % (row['PropList'], row['AccPropList'])) if stat]

            for stat, value in zip(stats[::2], stats[1::2]):
                collection['Bonus'][COLLECTION_STATS[stat]] = int(value)

def parse_cubes(root: str, data: dict):
    CUBE_IES = IES.CUBE

    LOG.info('Parsing Cubes from %s ...', CUBE_IES)

    ies_path = join(root, 'ies.ipf', CUBE_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', CUBE_IES)
        return

    item_data = data['items']
    cube_data = data['cube_contents']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            item = row['ItemName']

            if item == '':
                continue

            if item not in item_data:
                LOG.warning('Cube Item Missing: %s', item)
                continue

            if row['Group'] not in cube_data:
                cube_data[row['Group']] = []

            content = {}

            content['Item']   = item
            content['Chance'] = row['Ratio']

            cube_data[row['Group']].append(content)

def parse_equipment(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    TREES       = ['Char1', 'Char2', 'Char3', 'Char4', 'Char5']
    LUA_RUNTIME = luautil.LUA_RUNTIME

    item_data   = data['items']
    arcane_data = data['arcane']

    for file_name in IES.EQUIPMENT:
        LOG.info('Parsing Equipment from %s ...', file_name)

        ies_path = join(root, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
                equipment = __create_item(row, translate, find_icon)
                
                equipment['Type']          = 'EQUIPMENT'
                equipment['TypeAttack']    = row['AttackType']
                equipment['TypeEquipment'] = row['ClassType'].upper()
                equipment['Level']         = row['ItemLv'] if row['ItemLv'] > 0 else equipment['RequiredLevel']
                equipment['Material']      = row['Material']
                equipment['RequiredTree']  = 'TTTTT' if 'All' in row['UseJob'] else ''.join(['T' if tree in row['UseJob'] else 'F' for tree in TREES])
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

                for stat in EQUIPMENT_STATS:
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
                    equipment['Bonus'].append(('', translate(row['OptDesc'])))

                # Arcanes
                if equipment['TypeEquipment'] == 'ARCANE':
                    arcane_effect = {}

                    arcane_effect['Tier'] = int(row['NumberArg'])

                    if 'AdditionalOption_1' in row and row['AdditionalOption_1'] != '':
                        arcane_effect['Base'] = row['AdditionalOption_1']

                    if 'AdditionalOption_2' in row and row['AdditionalOption_2'] != '':
                        arcane_effect['Final'] = row['AdditionalOption_2']

                    arcane_data[equipment['$ID_NAME']] = arcane_effect

                # Hair Accessories
                if row['ReqToolTip'][:-1] == '헤어 코스튬':
                    equipment['TypeEquipment'] = 'HAIR_ACC_%s' % row['ReqToolTip'][-1:]

                item_data[equipment['$ID_NAME']] = equipment

def parse_gems(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    GEM_IES = IES.GEM_BASIC

    SELECT_ITEM = 'Item[Name~="%s"]'

    LOG.info('Parsing Gems from %s ...', GEM_IES)
        
    ies_path = join(root, 'ies.ipf', GEM_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', GEM_IES)
        return

    xml_path = join(root, 'xml.ipf', 'socket_property.xml')

    if exists(xml_path):
        soup = parse_xml(xml_path).getroot()
    else:
        soup = xml_element('SocketProperty')
    
    item_data  = data['items']
    skill_data = data['skills']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            gem = __create_item(row, translate, find_icon)

            gem['TypeGem'] = data['EquipXpGroup'].upper()

            if gem['TypeGem'] == 'GEM_SKILL':
                skill = gem['$ID_NAME'][4:]

                if skill not in skill_data:
                    LOG.warning('Skill Missing: %s', skill)
                    continue

                skill_data[skill]['Gem'] = gem['$ID_NAME']

            else:
                for item in soup.cssselect(SELECT_ITEM % gem['$ID_NAME']):
                    bonus = {}

                    for prop in item:
                        stats = [stat for stat in split('/+', '%s/%s' % (prop['proplist_mainorsubweapon'], prop['proplist_mainorsubweapon_penalty'])) if stat]

                        for stat, value in zip(stats[::2], stats[1::2]):
                            if stat not in bonus:
                                bonus[stat] = [0] * 11

                            bonus[stat][int(prop.get('level'))] = int(value)

                        gem['Bonuses'] = bonus
                
            item_data[gem['$ID_NAME']] = gem

def parse_goddess_equipment(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
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

    data['goddess_reinf_mat'] = materials
    
    ies_list = {
        'item_goddess_reinforce.ies'    : 460, 
        'item_goddess_reinforce_470.ies': 470
    }

    for file_name in ies_list:
        ies_path = join(root, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        obj = []

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
                obj.append(row)

        data['goddess_reinf'][ies_list[file_name]] = obj

def parse_grade_ratios(root: str, data: dict):
    LOG.info('Parsing Grade Ratios from item_grade.ies ...')

    ies_path = join(root, 'ies.ipf', 'item_grade.ies')

    if not exists(ies_path):
        LOG.warning('File not found: item_grade.ies')
        return

    grade_ratios = {}

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            grade_ratios[int(row['Grade'])] = row

    data['grade_ratios'] = grade_ratios

def parse_items(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    item_data = data['items']

    for file_name in IES.ITEM:
        LOG.info('Parsing Items from %s ...', file_name)

        ies_path = join(root, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
                item = __create_item(row, translate, find_icon)
                
                if item['Type'] == 'CARD':
                    item['IconTooltip'] = find_icon(row['TooltipImage'])
                    item['TypeCard']    = row['CardGroupName'].upper() if 'CardGroupName' in row else 'MASTER_CARD_ALBUM' # HOTFIX: Master Card Albums

                if item['Type'] == 'CUBE':
                    item['TypeCube'] = row['StringArg']

                if item['Type'] == 'DRUG':
                    item['Type'] == 'CONSUMABLE'

                # HOTFIX: 2021 Savinose Dysnai
                if item['Type'] in ['ARMOR', 'WEAPON'] and match('^2021_NewYear_Disnai_.+_box$', row['ClassName']):
                    item['Type'] = 'PREMIUM'
                
                # HOTFIX: Event Weapon Boxes
                if item['Type'] == 'WEAPON' and match('^(?:(?!2021).)*_?(?:box|SelectBox)_?.*$', row['ClassName']):
                    item['Type'] = 'EVENT'
                
                # HOTFIX: [Event] Enchant Jewel Box
                if item['Type'] == 'CONSUME':
                    item['Type'] = 'EVENT'
                
                item_data[item['$ID_NAME']] = item

def parse_recipes(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    RECIPE_IES = IES.RECIPE

    LOG.info('Parsing Recipes from %s ...', RECIPE_IES)

    ies_path = join(root, 'ies.ipf', RECIPE_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', RECIPE_IES)
        return

    item_data = data['items']

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            recipe = __create_item(row, translate, find_icon)

            if row['TargetItem'] not in item_data:
                LOG.warning('Recipe Product Missing: %s', row['TargetItem'])
                continue

            recipe['Name'] = 'Recipe - %s' % item_data[row['TargetItem']]['Name']

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
                
                if item not in item_data:
                    LOG.warning('Recipe Material for %s Missing: %s', row['TargetItem'], item)
                    continue

                material = {}
                
                material['Item']     = item
                material['Quantity'] = int(row['Item_%s_1_Cnt' % i])
                    
                recipe['Materials'].append(material)

            item_data[recipe['$ID_NAME']] = recipe

def parse_relic_gems(root: str, data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]):
    GEM_IES = IES.GEM_RELIC

    SELECT_DESCRIPTION = 'dic_data[FilenameWithKey*="RelicGem_%s_DescText_Data_0"][IsUse="1"]'
    TOOLTIP_SCRIPT     = 'get_tooltip_%s_arg%s'

    LOG.info('Parsing Relic Gems from %s ...', GEM_IES)
        
    ies_path = join(root, 'ies.ipf', GEM_IES)

    if not exists(ies_path):
        LOG.warning('File not found: %s', GEM_IES)
        return

    LUA_RUNTIME = luautil.LUA_RUNTIME

    item_data = data['items']

    soup = parse_xml(join(root, 'language.ipf', 'DicIDTable.xml')).getroot()

    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in IESReader(ies_file, delimiter = ',', quotechar = '"'):
            gem = __create_item(row, translate, find_icon)

            gem['Type']    = 'GEM'
            gem['TypeGem'] = row['GroupName']

            option = row['RelicGemOption']

            if row['GemType'] == 'Gem_Relic_Cyan':
                description = soup.cssselect(SELECT_DESCRIPTION % option)

                if len(description > 0):
                    gem['Description'] = translate(soup.cssselect(SELECT_DESCRIPTION % option)[0].get('kr', ''))

            else:
                gem['Description'] = ''

            gem['Effects'] = {}

            tooltip_script = TOOLTIP_SCRIPT % (option, 1)

            if tooltip_script in LUA_RUNTIME:
                factor, name, _, unit = LUA_RUNTIME[tooltip_script](row)

                gem['Effects'][name] = (factor, unit)

                tooltip_script = TOOLTIP_SCRIPT % (option, 2)

                if row['GemType'] != 'Gem_Relic_Black' and tooltip_script in LUA_RUNTIME:
                    factor, name, _, unit = LUA_RUNTIME[tooltip_script](row)

                    gem['Effects'][name] = (factor, unit)

                    tooltip_script = TOOLTIP_SCRIPT % (option, 3)

                    if tooltip_script in LUA_RUNTIME:
                        factor, name, _, unit = LUA_RUNTIME[tooltip_script](row)

                        gem['Effects'][name] = (factor, unit)

            item_data[gem['$ID_NAME']] = gem

def parse_vision(root: str, data: dict, translate: Callable[[str], str]):
    BOLD_FORMAT   = '{nl} {nl}{@st66d}{s15}'
    SELECT_EFFECT = 'dic_data[FilenameWithKey*="tooltip_%s_Data_0"][IsUse="1"]'

    LOG.info('Parsing Vision Effects ...')

    xml_path = join(root, 'language.ipf', 'DicIDTable.xml')

    if not exists(xml_path):
        LOG.warning('File not found: DicIDTable.xml')
        return

    item_data   = data['items']
    arcane_data = data['arcane']

    soup = parse_xml(xml_path).getroot()

    for arcane in arcane_data:
        equipment = item_data[arcane]

        id    = arcane[:None if arcane['Tier'] == 1 else -4]
        base  = soup.cssselect(SELECT_EFFECT % arcane['Base'])  if 'Base'  in arcane else None
        final = soup.cssselect(SELECT_EFFECT % arcane['Final']) if 'Final' in arcane else None

        if id in VISION_TO_CLASS:
            equipment['VisionClass'] = VISION_TO_CLASS[id]

        if len(base) and base[0].has_key('kr'):
            equipment['Bonus'].append(('VSN_BAS', translate(base.get('kr'))))

        if len(final) and final[0].has_key('kr'):
            equipment['Bonus'].append(('VSN_FIN', translate(final.get('kr').replace(BOLD_FORMAT, ''))))

def __create_item(data: dict, translate: Callable[[str], str], find_icon: Callable[[str], str]) -> dict:
    item = {}

    item['$ID']           = str(data['ClassID'])
    item['$ID_NAME']      = data['ClassName']
    item['Name']          = translate(data['Name']) if 'Name' in data else None
    item['Type']          = data['GroupName'].upper()
    item['InternalType']  = item['Type']
    item['Grade']         = int(data['ItemGrade']) if 'ItemGrade' in data and data['ItemGrade'] != '' else 1
    item['Stars']         = int(data['ItemStar'])
    item['Icon']          = find_icon(data['Icon'])
    item['Description']   = translate(data['Desc']) if 'Desc' in data else None
    item['RequiredLevel'] = int(data['UseLv'])
    item['Weight']        = float(data['Weight'])
    item['Cooldown']      = int(data['ItemCoolDown'])
    item['Expiration']    = float(data['LifeTime'])
    item['Destroyable']   = data['Destroyable'] == 'YES'
    item['Tradability']   = ''.join(['T' if data['%sTrade' % (target)] == 'YES' else 'F' for target in TRADABILITY])
    item['Price']         = data['Price']
    item['SellPrice']     = data['SellPrice']

    item['Link_Maps']             = []
    item['Link_Maps_Exploration'] = []
    item['Link_Monsters']         = []

    return item

def __resolve_addatk(data: dict) -> int:
    value = 0 if data['Add_Damage_Atk'] == '' else int(data['Add_Damage_Atk'])

    for stat in ADD_ATK_STATS:
        if data[stat] == '' or data[stat] == '0':
            continue

        value += int(data[stat])

    return value

def __resolve_addres(data: dict) -> int:
    value = 0 if data['ResAdd_Damage'] == '' else int(data['ResAdd_Damage'])

    for stat in ADD_RES_STATS:
        if data[stat] == '' or data[stat] == '0':
            continue

        value += int(data[stat])
    
    return value

def __resolve_maxsta(data: dict) -> int:
    value = 0 if data['MSTA'] == '' else int(data['MSTA'])

    if data['RSTA'] != '' and data['RSTA'] != '0':
        value += int(data['RSTA'])

    return value

__LEGACY_STAT_SOLVER = {
    'Add_Damage_Atk': __resolve_addatk, # HOTFIX: Additional Property Damage is Additional Damage
    'ResAdd_Damage' : __resolve_addres, # HOTFIX: Additional Property Damage Resistance is Additional Damage Resistance
    'MSTA'          : __resolve_maxsta  # HOTFIX: Stamina Recovery is Maximum Stamina
}