# -*- coding: utf-8 -*-
"""
The main script for IES parsers.

Created on Thu Sep 23 11:17:20 2021

@author: Temperantia
@credit: Temperantia, Nodius
"""

import csv
import json
import logging
import sys
from os.path import join

import asset
import attributes
import buff
import effects
import items
import items_static
import jobs
import luautil
import maps
import misc
import monsters
import parse_xac
import sets
import skills
import translation
from cache import TOSParseCache as Cache

SUPPORTED_REGIONS = ['itos', 'ktos', 'ktest', 'jtos', 'twtos']
TRANSLATE_REGIONS = ['itos', 'jtos', 'twtos']

def print_version(file_name: str, version: dict):
    with open(file_name, 'w') as file:
        csv.writer(file).writerows([[region, version[region]] for region in version])

def read_version(file_name: str):
    with open(file_name, 'r') as file:
        return {row[0]: row[1] for row in csv.reader(file)}

if __name__ == '__main__':
    try:
        region = sys.argv[1].lower()

        if region not in SUPPORTED_REGIONS:
            logging.warning('Region has not been supported yet')
            quit()
        
    except:
        logging.warning('Missing Argument: Region')
        quit()
    
    cache = Cache()

    current = read_version('parser_version.csv')
    latest  = read_version(join('..', 'downloader', 'revision.csv'))

    if latest[region] == current[region] and '-f' not in sys.argv:
        logging.warning('The parsed data is already update to date.')
        quit()
        
    cache.build(region)

    parse_xac.parse_xac(cache)

    luautil.init(cache)

    if region in TRANSLATE_REGIONS:
        translation.parse_translations(cache)
    
    asset.parse(cache)

    jobs.parse(cache)

    effects.parse(cache)

    skills.parse_skill_tree (cache) # Parse Class Skills
    sets  .parse_legend_sets(cache) # Parse Legend Sets and Skills
    items .parse_cosplay    (cache) # Parse Costume Skills
    skills.parse_relic      (cache) # Parse Relic Release
    skills.parse_common     (cache) # Parse Common Skills
    skills.parse_skills     (cache) # Parse Cached Skills

    attributes.parse(cache)
    attributes.parse_links(cache)   
    attributes.parse_clean(cache)

    buff.parse(cache)

    items.parse_items                (cache) # Parse Items
    items.parse_grade_ratios         (cache) # Parse Grade Ratios
    items.parse_equipment            (cache) # Parse Equipment
    items.parse_gems                 (cache) # Parse Gems
    items.parse_cubes                (cache) # Parse Cubes
    items.parse_collections          (cache) # Parse Collections
    items.parse_recipes              (cache) # Parse Recipes
    items.parse_books                (cache) # Parse Books

    sets.parse_equipment_sets(cache) # Parse Equipment Sets
    
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
        json.dump({'version': "%s_001001.ipf" % (latest)}, file)