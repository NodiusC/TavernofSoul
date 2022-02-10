# -*- coding: utf-8 -*-

'''
Created on Mon Sep 20 09:20:20 2021

@author: Temperantia

Cache of all parse for exportation as JSON files to be inserted into MySQL
'''

import json
import logging
import os

from os.path import exists, join

def is_ascii(item):
    try:
        item.decode('ascii')

    except UnicodeDecodeError:
        return False
    
    return True

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
    CONVERTER_PATH                = join("XAC", 'XAC2DAE.jar')
    
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
        'item_quest.ies',
        'item_Reputation.ies',
        'item_PersonalHousing.ies',
        'item_GuildHousing.ies',
        'item_colorspray.ies',
        'recipe.ies',
    ]
    
    data_build = ['assets_icons', 'maps', 'maps_by_name', 'maps_by_position']
        
    data = {
       'dictionary'            : {},
       'items'                 : {},
       'cube_contents'         : {},
       'equipment_sets'        : {},
       'equipment_sets_by_name': {},
       'assets_icons'          : {},
       'jobs'                  : {},
       'jobs_by_name'          : {},
       'attributes'            : {},
       'attributes_by_name'    : {},
       'skills'                : {},
       'skills_by_name'        : {},
       'monsters'              : {},
       'monsters_by_name'      : {},
       'item_monster'          : [],
       'npcs'                  : {},
       'npcs_by_name'          : {},
       'maps'                  : {},
       'maps_by_name'          : {},
       'maps_by_position'      : {},
       'map_item'              : [],
       'map_npc'               : [],
       'map_item_spawn'        : [],
       'skill_mon'             : {},
       'grade_ratios'          : {},
       'buff'                  : {},
       'achievements'          : {},
       'charxp'                : {},
       'petxp'                 : {},
       'assisterxp'            : {},
       'goddess_reinf_mat'     : {},
       'goddess_reinf'         : {}
    }
    
    def build(self, region):
        self.REGION                          = region.lower()
        self.BASE_PATH_INPUT                 = join("..", "TavernofSoul", "JSON_{}".format(self.REGION))
        self.BASE_PATH_OUTPUT                = join("..", "TavernofSoul", "JSON_{}".format(self.REGION))
        self.STATIC_ROOT                     = join("..", "TavernofSoul", "staticfiles_itos")
        self.PATH_BUILD_ASSETS_ICONS         = join(self.STATIC_ROOT, "icons")
        self.PATH_BUILD_ASSETS_IMAGES_MAPS   = join(self.STATIC_ROOT, "maps")
        self.PATH_BUILD_ASSETS_MODELS        = join(self.STATIC_ROOT, "models")
        
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
        
        self.PATH_INPUT_DATA                 = join('..', '{}_unpack'.format(self.REGION))
        self.PATH_INPUT_DATA_LUA             = join('..', '{}_unpack'.format(self.REGION))

        if self.REGION == 'itos':
            self.TRANSLATION_PATH                = join ("..","Translation", 'English')
        elif self.REGION == 'jtos':
            self.TRANSLATION_PATH                = join ("..","Translation", 'Japanese')
        else:
            self.TRANSLATION_PATH                = "."
        
        for i in self.data_build:
            self.data[i] = self.import_json(join(self.BASE_PATH_INPUT, "%s.json"%(i)))
    
    def export(self, file):
        self.print_json(self.data[file], "{}.json".format(file))
        
    def export_all(self):
        for i in self.data:
            self.export(i)
    
    def get_monster(self, skill):
        returned_mon_id = []

        for mon in self.data['monsters']:
            mon = self.data['monsters'][mon]

            if 'SkillType' not in mon:
                logging.warning("skill type not in mon {}".format(mon['$ID']))
                continue

            if mon['SkillType'].lower() == skill.lower():
                returned_mon_id.append(mon['$ID'])

        if returned_mon_id == []:
            skill = 'mon_'+skill

        for mon in self.data['monsters']:
            mon = self.data['monsters'][mon]

            if 'SkillType' not in mon:
                logging.warning("skill type not in mon {}".format(mon['$ID']))
                continue

            if mon['SkillType'].lower() == skill.lower():
                returned_mon_id.append(mon['$ID'])    

        return returned_mon_id
    
    def get_npc(self, name):
        if name in self.data['monsters_by_name']:
            return self.data['monsters_by_name'][name], 'mon'
        elif name in self.data['npcs_by_name']:
            return self.data['npcs_by_name'][name], 'npc'
        else:
            return None
        
    def import_json(file):
        if not exists(file):
            logging.warn("Not Exit: {}".format(file))
            return {}

        try:
            with open(file, "r") as f:
                data = json.load(f)
        except:
            logging.error("error in importing file {}".format(file))
            return {}
        
        return data
    
    def parse_entity_icon(self,icon):
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
            logging.warning('The icon for \'%s\' is missing', icon) # There's nothing we can do about this
            return icon
    
    def print_json(self, item, file):
        file_input = join(self.BASE_PATH_INPUT, file)

        with open(file_input, "w") as f:
            json.dump(item, f)
    
    def reverse_dictionary(self, dicts):
        a = {}

        for i in dicts.keys():
            a [dicts[i]] =  i
        
        return a
    
    def translate(self, key):
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
    RESPONSIVE     = "Responsive"
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
            TOSAttackType.RESPONSIVE    : "Responsive",
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