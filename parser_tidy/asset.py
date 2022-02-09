# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 13:47:05 2021

@author: CPPG02619
"""

import imageutil
import logging
import os
import shutil
import xml.etree.ElementTree as ET

from cache import TOSParseCache as Cache
from os.path import exists, join

IMAGE_SIZE = {  # Top, Left, Width, Height
    'bosscard2'        : (330, 440),
    'sub_card3'        : (330, 440),
    'npccard'          : (330, 440),
    'goddesscard'      : (330, 440),
    'item_tooltip_icon': (256, 256),
    '256_equip_icons'  : (256, 256),
    '256_costume_icons': (256, 256),
    'acc_item'         : (256, 256),
    'hair_accesory'    : (256, 256),
    'item'             : (256, 256),
    'payment'          : (256, 256)
}

WHITELIST_BASESKINSET = [
    'bosscard2',
    'minimap_icons',
    'sub_card3',
    'wearing_weapon',
    'npccard',
    'goddesscard',
    'worldmap_image',
]

WHITELIST_RGB = [
    'bosscard2',
    'sub_card3',
    'npccard',
    'goddesscard',
    'worldmap_image',
]

def parse(c = None):
    if c == None:
        logging.warn("c is none")
        c = Cache()
        c.build()

    try:
        os.mkdir(c.PATH_BUILD_ASSETS_ICONS)
    except:
        pass

    logging.debug('--- Parsing Assets ---')

    parse_icons('baseskinset.xml',c)
    parse_icons('classicon.xml'  ,c)
    parse_icons('itemicon.xml'   ,c)
    parse_icons('mongem.xml'     ,c)
    parse_icons('monillust.xml'  ,c)
    parse_icons('skillicon.xml'  ,c)

def parse_icons(file_name, c):
    logging.debug('Parsing File: {}'.format(file_name))

    data_path = join(c.PATH_INPUT_DATA, 'ui.ipf', 'baseskinset', file_name)
    
    if not exists(data_path):
        logging.warn("{} does not exist".format(data_path))
        return
    
    data = ET.parse(data_path).getroot()
    data = [(image, imagelist) for imagelist in data for image in imagelist]

    for work in data:
        parse_icons_step(file_name, work, c)

def parse_icons_step(file_name, work, c):     
    image          = work[0]
    image_category = work[1].get('category')

    if image.get('file') is None or image.get('name') is None:
        return
    
    if file_name == 'baseskinset.xml' and image_category not in WHITELIST_BASESKINSET:
        return
    
    file_name       = join(c.PATH_INPUT_DATA, 'ui.ipf', 'baseskinset', file_name.lower())
    image_extension = '.jpg' if image_category in WHITELIST_RGB else '.png'
    image_file      = image.get('file').split('\\')[-1]

    image_name = image.get('name')
    image_rect = tuple(int(x) for x in image.get('imgrect').split()) if len(image.get('imgrect')) else None  # Top, Left, Width, Height

    # Copy icon to web assets folder
    copy_from = os.path.join(c.PATH_INPUT_DATA, 'ui.ipf', *image.get('file').lower().split('\\')[:-1])
    copy_from = os.path.join(copy_from, image_file)
    copy_to   = os.path.join(c.PATH_BUILD_ASSETS_ICONS, (image_name + image_extension).lower())

    if not os.path.isfile(copy_from):
        # logging.warning('The asset file \'{}\' cannot be found'.format(copy_from))
        # Not to Future Self:
        # If you find missing files due to wrong casing, go to the Hotfix at unpacker.py and force lowercase
        c.data['assets_icons'][image_name.lower()] = image_name.lower()
        return

    if (not os.path.exists(c.PATH_BUILD_ASSETS_ICONS)):
        os.mkdir (c.PATH_BUILD_ASSETS_ICONS)

    shutil.copy(copy_from, copy_to)

    # Crop, Resize, Optimize and convert to JPG/PNG
    image_mode = 'RGB' if image_extension == '.jpg' else 'RGBA'
    image_size = IMAGE_SIZE[image_category] if image_category in IMAGE_SIZE else (image_rect[2], image_rect[3])
    image_size = (256, 256) if file_name == 'classicon.xml' else image_size
    image_size = (256, 256) if file_name == 'skillicon.xml' else image_size

    imageutil.optimize(copy_to, image_mode, image_rect, image_size)

    # Store mapping for later use
    c.data['assets_icons'][image_name.lower()] = image_name.lower()