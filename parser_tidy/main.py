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
    
    c = Cache()

    current_version = revision_txt_read('parser_version_{}.txt'.format(region.lower()))
    
    version = revision_txt_read(join('..', 'downloader', 'revision_{}.txt'.format(region)))

    if version == current_version and '-f' not in sys.argv:
        logging.warning('IPF is already update to date')
        quit()
        
    c.build(region)

    parse_xac.parse_xac(c)

    luautil.init(c)

    no_translation = ['ktos', 'ktest']

    if (region not in no_translation):
        translation.makeDictionary(c)
    
    asset.parse(c)
    jobs.parse(c)
    skill_bytool.parse(c)
    skills.parse(c)
    attributes.parse(c)
    attributes.parse_links(c)   
    attributes.parse_clean(c)
    skills.parse_clean(c)
    buff.parse(c)
    items.parse(c)

    if (region not in no_translation):
        vaivora.parse(c)
        vaivora.parse_lv4(c)
    
    insert_static(c)
    
    items.parse_goddess_EQ(c)
    
    monsters.parse(c)
    monsters.parse_links(c)
    monsters.parse_skill_mon(c)
    
    maps.parse(c)
    maps.parse_maps_images(c) #run map_image.py with py2.7 before running this
    maps.parse_links(c)
    misc.parse_achievements(c)

    c.export_all()

    revision_txt_write('parser_version_{}.txt'.format(region.lower()), version)

    v = {'version' : "{}_001001.ipf".format(version)}
    
    with open(join(c.BASE_PATH_OUTPUT, 'version.json'), "w") as f:
        json.dump(v,f)