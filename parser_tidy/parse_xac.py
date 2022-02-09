# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 09:49:44 2022

@author: CPPG02619
"""

import csv
import logging
import subprocess

from cache import TOSParseCache as Cache
from os import mkdir
from os.path import exists, join, split

def parse_xac(c = None):
    if c == None:
        c = Cache()
        c.build('itos')
    
    xac = {}

    ies_path = join(c.PATH_INPUT_DATA, 'ies_client.ipf', 'xac.ies')

    with open(ies_path, 'r', encoding="utf-8") as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            xac[row['ClassName'].lower()] = row
    
    c.data['xac'] = xac

def get_model_name_prefix(i):
    better = {
            'WAR' : 'warrior',
            'CLR' : 'cleric',
            'WIZ' : 'wizard',
            'ARC' : 'archer',
    }
    
    i = i.split("_")

    if len(i) < 3:
        return ''
    
    add_on = "{}_{}".format(better[i[1]], i[2].lower())

    return add_on

def getModelPrefixAdv(i):
    if i['UseJob'] == 'All':
        job = 'warrior'
    else:
        return ""
    
    if i['UseGender'] == 'Female':
        gender = 'f'
    else:
        gender = 'm'
    
    return "{}_{}".format(job, gender)

def eq_model_name(item, c):
    #item = c.data['items']['0511004019'] # Please use ClassName if updated
    xac = c.data['xac']
    if 'Icon' not in item:
        return ''
    model_name = item['FileName']
    prefix = get_model_name_prefix(item['ModelType'])
    if prefix:
        name  = prefix+"_"+ model_name
    else:
        name = getModelPrefixAdv(item) + '_' +model_name
        
    if name.lower() in xac:
        """
        if (xac2dae(c, name.lower())):
            return name
        else:
            return ''
        """
        return name
    else:
        return ''


        
def pc_model_name(item,c):
    xac = c.data['xac']
    model_name = item['ClassName']
    if model_name in xac:
        item['model'] = model_name
    else:
        item['model'] = ''
        
from shutil import move, copytree, rmtree

def xac2dae(c, filename):
    converter   = c.CONVERTER_PATH
    filenamexac = filename + '.xac'

    dst         = join(c.PATH_BUILD_ASSETS_MODELS, filename)
    try:
        mkdir(dst)
    except:
        pass

    if (exists(join(dst,filename+'.dae'))):
        return
    
    path        = join(c.PATH_INPUT_DATA, 'some_folder', filenamexac)
    outputfile  = path+'.dae'
    subprocess.call(['java', '-jar', converter, path],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    dds         = join(c.PATH_INPUT_DATA, 'some_folder', filename + '.dds')
    if '.ipf' in split(split(dds)[0])[-1]:
        subprocess.call(['cp', dds,dst])
    else:
        dds = split(dds)[0]
        subprocess.call(['cp', '-r', dds,dst], )

    try:
        move(outputfile, join(dst, filename+'.dae') )
        return True
    except:
        logging.warning("error parsing xac -  {}".format(filenamexac))
        subprocess.call(['rm', '-r', dst])
        return False
    