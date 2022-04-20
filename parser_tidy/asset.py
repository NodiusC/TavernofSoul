# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 13:47:05 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

from logging import getLogger
from os.path import exists, isfile, join
from shutil import copy

from lxml.html import HtmlElement as HTMLElement, parse as parse_xml
from PIL.Image import ANTIALIAS, open as open_image

from cache import TOSParseCache as Cache
from constants.xml import ICON

LOG = getLogger('Parse.Assets')

class Asset():
    __ASSETS = {}

    def __call__(self, name: str) -> str:
        return self.get(name)

    def __init__(self, cache: Cache):
        root        = cache.PATH_INPUT_DATA
        destination = cache.PATH_BUILD_ASSETS_ICONS

        for file_name in ICON:
            LOG.info('Parsing Assets from %s ...', file_name)

            xml_path = join(root, 'ui.ipf', 'baseskinset', file_name)

            if not exists(xml_path):
                LOG.warning('FILE \'%s\' NOT FOUND', file_name)
                continue

            soup: HTMLElement = parse_xml(xml_path).getroot()

            for category in ICON[file_name]:
                image_list: HTMLElement

                selection = '[category~="%s"]' % category if category != '*' else ''

                for image_list in soup.cssselect('imagelist%s' % selection):
                    entry: HTMLElement

                    for entry in image_list.iter('image'):
                        if not entry.get('name') or not entry.get('file'):
                            continue

                        name: str = entry.get('name')
                        file: str = entry.get('file')
                        rect      = tuple(map(int, str(entry.get('imgrect')).split()))
                        size      = (rect[2], rect[3])

                        if size < (256, 256):
                            size = (256, 256)

                        source_path = join(root, 'ui.ipf', file)

                        if isfile(source_path):
                            image_path = join(destination, '%s.png' % name)

                            copy(source_path, image_path)

                            image = open_image(image_path)
                            image = image.convert('RGBA') if image.mode != 'RGBA' else image
                            image = image.crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3])) if image.size != size else image
                            image = image.resize(size, ANTIALIAS) if image.size < size else image

                            image.save(image_path, 'PNG', optimize = True, quality = 80)

                        else:
                            LOG.warning('FILE \'%s\' NOT FOUND', file)

                        self.__ASSETS[name] = '%s.png' % name

    def get(self, name: str) -> str:
        return self.__ASSETS[name] if name in self.__ASSETS else None