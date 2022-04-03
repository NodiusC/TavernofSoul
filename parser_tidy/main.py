# -*- coding: utf-8 -*-
"""
The main script for IES parsers.

Created on Thu Sep 23 11:17:20 2021

@author: Temperantia
@credit: Temperantia, Nodius
"""

import sys
from csv import reader, writer
from json import dump as export
from logging import getLogger
from os.path import join

import asset
import attributes
import buff
import effects
import items
import items_static
import classes
import luautil
import maps
import misc
import monsters
import parse_xac
import sets
import skills
import translation
from cache import TOSParseCache as Cache

LOG = getLogger('Parse')

SUPPORTED_REGIONS = ['itos', 'ktos', 'ktest', 'jtos', 'twtos']
TRANSLATE_REGIONS = ['itos', 'jtos', 'twtos']

def print_version(file_name: str, version: dict):
    with open(file_name, 'w') as file:
        writer(file).writerows([[region, version[region]] for region in version])

def read_version(file_name: str):
    with open(file_name, 'r') as file:
        return {row[0]: row[1] for row in reader(file)}

if __name__ == '__main__':
    try:
        region = sys.argv[1].lower()

        if region not in SUPPORTED_REGIONS:
            LOG.warning('Region has not been supported yet')
            quit()
        
    except:
        LOG.warning('Missing Argument: Region')
        quit()
    
    cache = Cache()

    current = read_version('parser_version.csv')
    latest  = read_version(join('..', 'downloader', 'revision.csv'))

    if latest[region] == current[region] and '-f' not in sys.argv:
        LOG.warning('The parsed data is already update to date.')
        quit()
        
    cache.build(region)

    root      = cache.PATH_INPUT_DATA
    data      = cache.data
    translate = cache.translate
    find_icon = cache.find_icon

    parse_xac.parse_xac(cache)

    luautil.init(cache)

    if region in TRANSLATE_REGIONS:
        translation.parse_translations(cache)
    
    asset.parse(cache)

    classes.parse_classes(cache)

    effects.parse(cache)

    skills.parse_skill_tree (root, data)                       # Parse Class Skills
    sets  .parse_legend_sets(root, data, translate) # Parse Legend Sets and Skills
    skills.parse_cosplay    (root, data)                       # Parse Costume Skills
    skills.parse_relic      (root, data, translate, find_icon) # Parse Relic Release
    skills.parse_common     (root, data, translate, find_icon) # Parse Common Skills
    skills.parse_skills     (root, data, translate, find_icon) # Parse Cached Skills

    attributes.parse_attributes     (root, data, translate, find_icon) # Parse Attributes
    attributes.parse_team_attributes(root, data, translate, find_icon) # Parse Account Attributes

    buff.parse(cache)

    items.parse_items         (root, data, translate, find_icon) # Parse Items
    items.parse_grade_ratios  (root, data)                       # Parse Grade Ratios
    items.parse_equipment     (root, data, translate, find_icon) # Parse Equipment
    sets .parse_equipment_sets(root, data, translate)            # Parse Equipment Sets
    items.parse_gems          (root, data, translate, find_icon) # Parse Gems
    items.parse_cubes         (root, data)                       # Parse Cubes
    items.parse_collections   (root, data)                       # Parse Collections
    items.parse_recipes       (root, data, translate, find_icon) # Parse Recipes
    items.parse_books         (root, data, translate)            # Parse Books
    
    items_static.insert_static(cache)
    
    items.parse_goddess_equipment(cache)
    
    monsters.parse(cache)
    
    maps.parse(cache)
    maps.parse_maps_images(cache) #run map_image.py with py2.7 before running this
    maps.parse_links(cache)
    misc.parse_achievements(cache)

    cache.export_all()

    current[region] = latest[region]

    print_version('parser_version.csv', latest)
    
    with open(join(cache.BASE_PATH_OUTPUT, 'version.json'), 'w') as file:
        export({'version': "%s_001001.ipf" % (latest)}, file)