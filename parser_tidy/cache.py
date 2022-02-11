# -*- coding: utf-8 -*-

"""
Created on Mon Sep 20 09:20:20 2021

@author: Temperantia

Cache of all parse for exportation as JSON files to be inserted into MySQL
"""

import json
import logging
import os

from os.path import exists, join

class TOSParseCache():
    REGION                        = None
    BASE_PATH_INPUT               = None
    BASE_PATH_OUTPUT              = None
    STATIC_ROOT                   = None
    PATH_BUILD_ASSETS_ICONS       = None
    PATH_BUILD_ASSETS_IMAGES_MAPS = None
    PATH_BUILD_ASSETS_MODELS      = None
    PATH_INPUT_DATA               = None
    PATH_INPUT_DATA_LUA           = None
    TRANSLATION_PATH              = None
    CONVERTER_PATH                = join('XAC', 'XAC2DAE.jar')

    REGIONS = {
        'itos': 'English',
        'jtos': 'Japanese'
    }
    
    EQUIPMENT_IES = [
        'item_equip.ies',
        'item_Equip_EP12.ies',
        'item_Equip_EP13.ies',
        'item_event_equip.ies'
    ]

    EQUIPMENT_REINFORCE_IES = {
        'item_goddess_reinforce.ies'    : 460,
        'item_goddess_reinforce_470.ies': 470
    }

    GEM_IES = [
        'item_gem.ies',
        'item_gem_bernice.ies',
        'item_gem_relic.ies'
    ]

    ITEM_IES = [
        'item.ies',
        'item_EP12.ies',
        'item_EP13.ies',
        'item_Equip.ies',
        'item_Equip_EP12.ies',
        'item_Equip_EP13.ies',
        'item_event_Equip.ies', 
        'item_gem.ies',
        'item_gem_bernice.ies',
        'item_gem_relic.ies',
        'item_HiddenAbility.ies',
        'item_premium.ies',
        'item_event.ies', 
        'item_Quest.ies',
        'item_Reputation.ies',
        'item_PersonalHousing.ies',
        'item_GuildHousing.ies',
        'item_colorspray.ies',
        'recipe.ies',
    ]

    MONSTER_IES = [
        'monster.ies',
        'Monster_solo_dungeon.ies',
        'Monster_BountyHunt.ies',
        'monster_guild.ies',
        'monster_event.ies',
        'monster_npc.ies',
        'monster_pet.ies',
        'monster_pcsummon.ies',
        'monster_mgame.ies'
    ]
    
    data_build = ['assets_icons', 'maps', 'maps_by_name', 'maps_by_position']
        
    data = {
       'dictionary'        : {},
       'assets_icons'      : {},
       'items'             : {},
       'cube_contents'     : {},
       'equipment_sets'    : {},
       'jobs'              : {},
       'jobs_by_name'      : {},
       'attributes'        : {},
       'attributes_by_name': {},
       'skills'            : {},
       'skill_effects'     : {},
       'monsters'          : {},
       'monster_skills'    : {},
       'monster_drops'     : [],
       'npcs'              : {},
       'maps'              : {},
       'maps_by_name'      : {},
       'maps_by_position'  : {},
       'map_item'          : [],
       'map_npc'           : [],
       'map_item_spawn'    : [],
       'grade_ratios'      : {},
       'buff'              : {},
       'achievements'      : {},
       'charxp'            : {},
       'petxp'             : {},
       'assisterxp'        : {},
       'goddess_reinf_mat' : {},
       'goddess_reinf'     : {}
    }
    
    def build(self, region: str):
        self.REGION                          = region.lower()

        self.BASE_PATH_INPUT                 = join('..', 'TavernofSoul', 'JSON_%s' % (self.REGION))
        self.BASE_PATH_OUTPUT                = join('..', 'TavernofSoul', 'JSON_%s' % (self.REGION))
        self.STATIC_ROOT                     = join('..', 'TavernofSoul', 'staticfiles_itos')

        self.PATH_BUILD_ASSETS_ICONS         = join(self.STATIC_ROOT, 'icons')
        self.PATH_BUILD_ASSETS_IMAGES_MAPS   = join(self.STATIC_ROOT, 'maps')
        self.PATH_BUILD_ASSETS_MODELS        = join(self.STATIC_ROOT, 'models')
        
        try:
            os.mkdir(self.PATH_BUILD_ASSETS_ICONS) 
        except:
            pass

        try:
            os.mkdir(self.PATH_BUILD_ASSETS_IMAGES_MAPS)
        except:
            pass

        try:
            os.mkdir(self.PATH_BUILD_ASSETS_MODELS) 
        except:
            pass
        
        self.PATH_INPUT_DATA     = join('..', '%s_unpack' % (self.REGION))
        self.PATH_INPUT_DATA_LUA = join('..', '%s_unpack' % (self.REGION))

        self.TRANSLATION_PATH    = join('..', 'Translation', self.REGIONS[self.REGION]) if self.REGION in self.REGIONS else '.'
        
        for i in self.data_build:
            self.data[i] = self.import_json(join(self.BASE_PATH_INPUT, '%s.json' % (i)))
    
    def export(self, file_name: str):
        self.print_json(self.data[file_name], '%s.json' % (file_name))
        
    def export_all(self):
        for file_name in self.data:
            self.export(file_name)
    
    def get_npc(self, name: str):
        if name in self.data['monsters']:
            return self.data['monsters'][name], 'mon'
        elif name in self.data['npcs']:
            return self.data['npcs'][name], 'npc'
        else:
            return None
        
    def import_json(self, file_name):
        if not exists(file_name):
            logging.warning('File not found: %s', file_name)
            return {}

        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except:
            logging.warning('An error occurred while importing file \'%s\'', file_name)
            return {}
    
    def parse_entity_icon(self, icon: str):
        if icon == '':
            return None
        
        icon = icon.lower()

        icon_found = None
    
        if icon in self.data['assets_icons']:
            icon_found = icon
        elif 'icon_' + icon in self.data['assets_icons']:
            icon_found = 'icon_' + icon
        elif icon +'_f' in self.data['assets_icons']:
            icon_found = icon + '_f'
        elif icon + '_m' in self.data['assets_icons']:
            icon_found = icon + '_m'
    
        if icon_found is not None:
            return self.data['assets_icons'][icon_found]
        else:
            logging.warning('The icon for \'%s\' is missing', icon)
            return icon
    
    def print_json(self, obj, file_name: str):
        with open(join(self.BASE_PATH_INPUT, file_name), 'w') as file:
            json.dump(obj, file)
    
    def reverse_dictionary(self, dictionary: dict):
        a = {}

        for i in dictionary.keys():
            a [dictionary[i]] =  i
        
        return a
    
    def translate(self, key: str):
        if self.TRANSLATION_PATH == None:
            return self.data['dictionary'][key]

        key = key.replace('"', '')

        if (self.data['dictionary'] == {}):
            logging.debug('The dictionary is empty')
            return key
        
        if not self.data['dictionary']:
            return key
        
        if key != '' and key not in self.data['dictionary']:
            logging.debug('The translation for key \'%s\' is missing', key)
            return key

        if key == '':
            return ''
        
        return self.data['dictionary'][key]

class TOSElement():
    FIRE      = 'Fire'
    ICE       = 'Ice'
    LIGHTNING = 'Lightning'
    EARTH     = 'Earth'
    HOLY      = 'Holy'
    DARK      = 'Dark'
    SOUL      = 'Soul'
    POISON    = 'Poison'
    NONE      = 'None'
    MELEE     = 'None'

    @staticmethod
    def to_string(value):
        if value == None:
            return 'None'
        
        return {
            TOSElement.FIRE     : 'Fire',
            TOSElement.ICE      : 'Ice',
            TOSElement.LIGHTNING: 'Lightning',
            TOSElement.EARTH    : 'Earth',
            TOSElement.HOLY     : 'Holy',
            TOSElement.DARK     : 'Dark',
            TOSElement.SOUL     : 'Soul',
            TOSElement.POISON   : 'Poison',
            TOSElement.NONE     : 'None',
            TOSElement.MELEE    : 'None'

        }[value]

    @staticmethod
    def value_of(string):
        if string == None:
            return 'NONE'
        
        return {
            'FIRE'     : TOSElement.FIRE,
            'ICE'      : TOSElement.ICE,
            'LIGHTNING': TOSElement.LIGHTNING,
            'LIGHTING' : TOSElement.LIGHTNING,
            'EARTH'    : TOSElement.EARTH,
            'HOLY'     : TOSElement.HOLY,
            'DARK'     : TOSElement.DARK,
            'SOUL'     : TOSElement.SOUL,
            'POISON'   : TOSElement.POISON,
            'NONE'     : TOSElement.NONE,
            'MELEE'    : TOSElement.MELEE,
            ''         : None
        
        }[string.upper()]

class TOSAttackType():
    MELEE          = 'Physical'
    MELEE_SLASH    = 'Slash'
    MELEE_PIERCING = 'Piercing'
    MELEE_STRIKE   = 'Strike'
    MELEE_THRUST   = 'Thrust'
    MISSILE        = 'Missile'
    MISSILE_BOW    = 'Bow'
    MISSILE_GUN    = 'Gun'
    MISSILE_CANNON = 'Cannon'
    MAGIC          = 'Magic'
    TRUE           = 'True Damage'
    BUFF           = 'Buff'
    RESPONSIVE     = 'Responsive'
    UNKNOWN        = ''

    @staticmethod
    def to_string(value):
        return {
            TOSAttackType.MELEE         : 'Physical',
            TOSAttackType.MELEE_SLASH   : 'Slash',
            TOSAttackType.MELEE_PIERCING: 'Piercing',
            TOSAttackType.MELEE_STRIKE  : 'Strike',
            TOSAttackType.MELEE_THRUST  : 'Thrust',
            TOSAttackType.MISSILE       : 'Missile',
            TOSAttackType.MISSILE_BOW   : 'Bow',
            TOSAttackType.MISSILE_GUN   : 'Gun',
            TOSAttackType.MISSILE_CANNON: 'Cannon',
            TOSAttackType.MAGIC         : 'Magic',
            TOSAttackType.TRUE          : 'True Damage',
            TOSAttackType.BUFF          : 'Buff',
            TOSAttackType.RESPONSIVE    : 'Responsive',
            TOSAttackType.UNKNOWN       : ''
        
        }[value]

    @staticmethod
    def value_of(string):
        return {
            'MELEE'     : TOSAttackType.MELEE,
            'SLASH'     : TOSAttackType.MELEE_SLASH,
            'ARIES'     : TOSAttackType.MELEE_PIERCING,
            'STRIKE'    : TOSAttackType.MELEE_STRIKE,
            'THRUST'    : TOSAttackType.MELEE_THRUST,
            'MISSILE'   : TOSAttackType.MISSILE,
            'ARROW'     : TOSAttackType.MISSILE_BOW,
            'GUN'       : TOSAttackType.MISSILE_GUN,
            'CANNON'    : TOSAttackType.MISSILE_CANNON,
            'MAGIC'     : TOSAttackType.MAGIC,
            'TRUEDAMAGE': TOSAttackType.TRUE,
            'RESPONSIVE': TOSAttackType.RESPONSIVE, #whats this?
            ''          : TOSAttackType.UNKNOWN,
            'HOLY'      : None,  # HotFix: Used by obsolete Skill #40706
        
        }[string.upper()]