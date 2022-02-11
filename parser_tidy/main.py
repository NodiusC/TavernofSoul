# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 11:17:20 2021

@author: Temperantia
"""

import asset
import attributes
import buff
import items
import jobs
import json
import logging
import luautil
import maps
import misc
import monsters
import os
import parse_xac
import skills
import skill_bytool
import sys
import translation
import vaivora

from cache import TOSParseCache as Cache
from items_static import insert_static
from os.path import join

def revision_txt_write(revision_txt, revision):
    revision = str(revision)
    
    with open(revision_txt, 'w') as file:
        file.write(revision)

def revision_txt_read(revision_txt):
    if os.path.isfile(revision_txt):
        with open(revision_txt, 'r') as file:
            return file.readline()
    else:
        return 0

if __name__ == '__main__':
    try:
        region = sys.argv[1].lower()

        if region not in ['itos', 'ktos', 'ktest', 'jtos']:
            logging.warning('Region has not been supported yet')
            quit()
        
    except:
        logging.warning('Missing Argument: Region')
        quit()
    
    cache = Cache()

    current_version = revision_txt_read('parser_version_{}.txt'.format(region.lower()))
    
    version = revision_txt_read(join('..', 'downloader', 'revision_{}.txt'.format(region)))

    if version == current_version and '-f' not in sys.argv:
        logging.warning('IPF is already update to date')
        quit()
        
    cache.build(region)

    parse_xac.parse_xac(cache)

    luautil.init(cache)

    no_translation = ['ktos', 'ktest']

    if (region not in no_translation):
        translation.makeDictionary(cache)
    
    asset.parse(cache)
    jobs.parse(cache)
    skill_bytool.parse(cache)
    skills.parse(cache)
    attributes.parse(cache)
    attributes.parse_links(cache)   
    attributes.parse_clean(cache)
    skills.parse_clean(cache)
    buff.parse(cache)
    items.parse(cache)

    if (region not in no_translation):
        vaivora.parse(cache)
        vaivora.parse_lv4(cache)
    
    insert_static(cache)
    
    items.parse_goddess_equipment(cache)
    
    monsters.parse(cache)
    
    maps.parse(cache)
    maps.parse_maps_images(cache) #run map_image.py with py2.7 before running this
    maps.parse_links(cache)
    misc.parse_achievements(cache)

    cache.export_all()

    revision_txt_write('parser_version_{}.txt'.format(region.lower()), version)

    v = {'version' : "{}_001001.ipf".format(version)}
    
    with open(join(cache.BASE_PATH_OUTPUT, 'version.json'), "w") as f:
        json.dump(v,f)