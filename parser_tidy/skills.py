# -*- coding: utf-8 -*-
"""
IES Parser for Skills.

Created on Thu Sep 23 08:55:17 2021

@author: Temperantia
@credit: rjgtav, Temperantia, Nodius
"""

import csv
import io
import logging
import os
from os.path import exists, join

from sympy import Float, Integer, jscode, symbols

import constants.damage as Damage
import constants.ies as IES
import luautil
from cache import TOSParseCache as Cache

X = symbols('x') # Skill Level Variable

LOG = logging.getLogger('Parse.Skills')
LOG.setLevel(logging.INFO)

def parse_common(cache: Cache):
    pass # TODO: Assister and Ride Pet

def parse_relic(cache: Cache):
    pass # TODO: Relic Release

def parse_skills(cache: Cache):
    LUA_RUNTIME = luautil.LUA_RUNTIME

    for file_name in IES.SKILL:
        LOG.info('Parsing Skills from %s ...', file_name)

        ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', file_name)

        if not exists(ies_path):
            LOG.warning('File not found: %s', file_name)
            continue

        with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
            for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
                if row['ClassName'] not in cache.data['skills']:
                    continue

                skill = cache.data['skills'][row['ClassName']]

                skill['$ID']         = row['ClassID']
                skill['Name']        = cache.translate(row['Name'])
                skill['Icon']        = cache.parse_entity_icon(row['Icon'])
                skill['Description'] = cache.translate(row['Caption'])
                skill['Details']     = cache.translate(row['Caption2'])

                skill['TypeDamage']  = Damage.of(row) if row['ValueType'] == 'Attack' else ['BUFF']
                skill['AttackSpeed'] = row['AffectedByAttackSpeedRate'] == 'YES'
                skill['Weapons']     = row['ReqStance']
                skill['Riding']      = row['EnableCompanion'] in ['YES', 'BOTH']

                skill['ItemCost']     = int(row['SpendItemBaseCount'])
                skill['BaseSP']       = float(row['BasicSP'])          # HOTFIX: Level 0
                skill['BaseCooldown'] = int(row['BasicCoolDown'])      # Level 0

                if skill['Type'] == 'CLASS' and row['CoolDown'] != 'SCR_GET_SKL_COOLDOWN':
                    base_cd = LUA_RUNTIME[row['CoolDown']](row | {'Level': 1})
                    leveled = LUA_RUNTIME[row['CoolDown']](row | {'Level': 2})

                    # The scaling of cooldown reduction is currently linear across all skill levels
                    cd_formula = base_cd * (2 - X) + leveled * (X - 1) # Simplified Linear Interpolation
                
                else:
                    cd_formula = Integer(skill['BaseCooldown']) # No cooldown reduction based on level if not a class skill

                # HOTFIX: Praise is the only skill with SP cost scaling with skill level
                sp_formula = skill['BaseSP'] * (1.1 - X  * 0.1) if row['SpendSP'] == 'SCR_GET_SpendSP_Praise' else Float(skill['BaseSP'])

                skill['SPCost']   = jscode(sp_formula)
                skill['Cooldown'] = jscode(cd_formula)
                skill['Overheat'] = row['SklUseOverHeat']
                
                skill['SkillFactor']         = float(row['SklFactor'])
                skill['SkillFactorPerLevel'] = float(row['SklFactorByLevel'])
                skill['Target']              = row['Target']

def parse_skill_tree(cache: Cache):
    LOG.info('Parsing Class Skills from skilltree.ies ...')

    ies_path = join(cache.PATH_INPUT_DATA, 'ies.ipf', 'skilltree.ies')

    if not exists(ies_path):
        LOG.warning('File not found: skilltree.ies')
        return
    
    with open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            skill = {}

            skill['$ID_NAME'] = row['SkillName']

            if row['SkillName'].startswith('Common_'):       # Force Attack, Cancel Attack, Release
                if row['SkillName'] in cache.data['skills']: # Prevent Duplication
                    continue

                skill['Type'] = 'COMMON'

            else:
                job = row['ClassName'].rsplit('_', 1)[0]

                if job not in cache.data['jobs']:
                    LOG.warning('Class Missing: %s', job)
                    continue

                class_skill = {}

                class_skill['Class']       = job
                class_skill['UnlockLevel'] = row['UnlockClassLevel']
                class_skill['MaxLevel']    = row['MaxLevel']

                cache.data['class_skills'][skill['$ID_NAME']] = class_skill

                skill['Type'] = 'CLASS'

            cache.data['skills'][skill['$ID_NAME']] = skill

def parse_skills_stances(constants):
    logging.debug('Parsing skills stances...')

    stance_list = []
    ies_path = join(constants.PATH_INPUT_DATA, 'ies.ipf', 'stance.ies')
    if(not exists(ies_path)):
       return
    # Parse stances
    with io.open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            stance_list.append(row)

    # Add stances to skills
    # from addon.ipf\skilltree\skilltree.lua :: MAKE_STANCE_ICON
    for skill in constants.data['skills'].values():
        stances_main_weapon = []
        stances_sub_weapon = []

        if skill['RequiredStance']:
            for stance in stance_list:
             

               
                if skill['RequiredStance'] == 'TwoHandBow' and stance['ClassName'] == 'Bow':
                    continue
                if 'Artefact' in stance['Name']:
                    continue

                if stance['UseSubWeapon'] == 'NO':
                    stances_main_weapon.append({
                        'Icon': constants.parse_entity_icon(stance['Icon']),
                        'Name': stance['ClassName']
                    })
                else:
                    found = False
                    for stance_sub in stances_sub_weapon:
                        if stance_sub['Icon'] == constants.parse_entity_icon(stance['Icon']):
                            found = True
                            break

                    if not found:
                        stances_sub_weapon.append({
                            'Icon': constants.parse_entity_icon(stance['Icon']),
                            'Name': stance['ClassName']
                        })
        else:
            stances_main_weapon.append({
                'Icon': constants.parse_entity_icon('weapon_All'),
                'Name': 'All'
            })

        if skill['RequiredStanceCompanion'] in ['BOTH', 'YES']:
            stances_main_weapon.append({
                'Icon': constants.parse_entity_icon('weapon_companion'),
                'Name': 'Companion'
            })

        skill['RequiredStance'] = [
            stance for stance in (stances_main_weapon + stances_sub_weapon)
            if stance['Icon'] is not None
        ]

def run_lua(skill, key_special, key_dict):
    LUA_RUNTIME = luautil.LUA_RUNTIME
    LUA_SOURCE = luautil.LUA_SOURCE
    var = []
    if (skill[key_special]):
        if (skill['MaxLevel']==-1):
            skill[key_dict] = []
            return
        try:
            for lv in range(0,skill['MaxLevel']+10,1):
                skill['Level'] = lv
                row = LUA_RUNTIME[skill[key_special]](skill) 
                if row == -1:
                    row = 0
                var.append(row)
            skill[key_dict] = var
        except:
            skill[key_dict] = []


def parse_skills_script(constants):
    """
    parse skills skill factor caption ratio etc which use lua script
    """
    key_dict = [
        'sfr', 'CaptionRatio', 'CaptionRatio2', 'CaptionRatio3',
        'CaptionTime', 'SkillSR', 'SpendItemCount' ,
        'SpendPoison', 'SpendSP' , 'CoolDown'
    ]
    key_special = [
        'Effect_SkillFactor', 'Effect_CaptionRatio','Effect_CaptionRatio2', 'Effect_CaptionRatio3',
        'Effect_CaptionTime', 'Effect_SkillSR', 'Effect_SpendItemCount', 'Effect_SpendPoison',
        'Effect_SpendSP', 'CoolDown'
    ]

    for g in constants.data['skills'].values():
        for i in range(len(key_dict)):
            run_lua(g,key_special[i], key_dict[i])

def parse_clean(constants):
    skills_to_remove = []
    # Find which skills are no longer active
    for skill in constants.data['skills'].values():
        if skill['Link_Job'] is None:
            skills_to_remove.append(skill)

    # Remove all inactive skills
    for skill in skills_to_remove:
        del constants.data['skills'][str(skill['$ID_NAME'])]

        skill_id = skill['$ID']

        for attribute in constants.data['attributes'].values():
            attr = constants.data['attributes_by_name'][attribute['$ID_NAME']]
            attribute['Link_Skills'] = [link for link in attribute['Link_Skills'] if link != skill_id]
            attr['Link_Skills'] = [link for link in attr['Link_Skills'] if link != skill_id]
        for job in constants.data['jobs'].values():
            job2= constants.data['jobs_by_name'][job['$ID_NAME']]
            job['Link_Skills'] = [link for link in job['Link_Skills'] if link != skill_id]
            job2['Link_Skills'] = [link for link in job2['Link_Skills'] if link != skill_id]
    
  