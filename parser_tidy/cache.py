# -*- coding: utf-8 -*-
"""
Handles the cached data parsed from IES files.
To be exported as JSON then inserted into MySQL.

Created on Mon Sep 20 09:20:20 2021

@author: Temperantia
@credit: Temperantia, Nodius
"""

import json
from logging import getLogger
from os.path import exists, join

LOG = getLogger('Parse')

class TOSParseCache():
    REGION                        = None
    BASE_PATH_INPUT               = None
    BASE_PATH_OUTPUT              = None
    STATIC_ROOT                   = None
    PATH_BUILD_ASSETS_ICONS       = None
    PATH_BUILD_ASSETS_IMAGES_MAPS = None
    PATH_INPUT_DATA               = None
    PATH_INPUT_DATA_LUA           = None
    TRANSLATION_PATH              = None

    REGIONS = {
        'itos' : 'English',
        'jtos' : 'Japanese',
        'twtos': 'Taiwanese'
    }
    
    data_build = ['assets_icons', 'maps', 'maps_by_name', 'maps_by_position']
        
    data = {
       'dictionary'        : {},
       'assets_icons'      : {},
       'items'             : {},
       'cube_contents'     : {},
       'equipment_sets'    : {},
       'legend_sets'       : {},
       'arcane'            : {},
       'classes'           : {},
       'attributes'        : {},
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
       'achievements'      : {}
    }
    
    def build(self, region: str):
        self.REGION                          = region.lower()

        self.BASE_PATH_INPUT                 = join('..', 'TavernofSoul', 'JSON_%s' % (self.REGION))
        self.BASE_PATH_OUTPUT                = join('..', 'TavernofSoul', 'JSON_%s' % (self.REGION))
        self.STATIC_ROOT                     = join('..', 'TavernofSoul', 'staticfiles_itos')

        self.PATH_BUILD_ASSETS_ICONS       = join(self.STATIC_ROOT, 'icons')
        self.PATH_BUILD_ASSETS_IMAGES_MAPS = join(self.STATIC_ROOT, 'maps')
        
        self.PATH_INPUT_DATA     = join('..', '%s_unpack' % (self.REGION))
        self.PATH_INPUT_DATA_LUA = join('..', '%s_unpack' % (self.REGION))

        self.TRANSLATION_PATH = join('..', 'Translation', self.REGIONS[self.REGION]) if self.REGION in self.REGIONS else '.'
        
        for i in self.data_build:
            self.data[i] = self.import_json(join(self.BASE_PATH_INPUT, '%s.json' % (i)))
    
    def export(self, file_name: str):
        self.print_json(self.data[file_name], '%s.json' % (file_name))
        
    def export_all(self):
        for file_name in self.data:
            self.export(file_name)
    
    def find_icon(self, icon: str) -> str:
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
            LOG.warning('The icon for \'%s\' is missing', icon)
            return icon
    
    def get_npc(self, name: str):
        if name in self.data['monsters']:
            return self.data['monsters'][name], 'mon'
        elif name in self.data['npcs']:
            return self.data['npcs'][name], 'npc'
        else:
            return None
        
    def import_json(self, file_name: str):
        if not exists(file_name):
            LOG.warning('File not found: %s', file_name)
            return {}

        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except:
            LOG.warning('An error occurred while importing file \'%s\'', file_name)
            return {}
    
    def print_json(self, obj, file_name: str):
        with open(join(self.BASE_PATH_INPUT, file_name), 'w') as file:
            json.dump(obj, file)
    
    def reverse_dictionary(self, dictionary: dict):
        a = {}

        for i in dictionary.keys():
            a [dictionary[i]] =  i
        
        return a
    
    def translate(self, text: str) -> str:
        if self.TRANSLATION_PATH == None:
            return self.data['dictionary'][text]

        text = text.replace('"', '')

        if (self.data['dictionary'] == {}):
            LOG.debug('The dictionary is empty')
            return text
        
        if not self.data['dictionary']:
            return text
        
        if text != '' and text not in self.data['dictionary']:
            LOG.debug('The translation for key \'%s\' is missing', text)
            return text

        if text == '':
            return ''
        
        return self.data['dictionary'][text]