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

import constants.ies as IES
import luautil
from cache import TOSParseCache as Cache
from constants.ability import parse_damage_properties as parse_properties

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
                skill['Icon']        = cache.get_icon(row['Icon'])
                skill['Description'] = cache.translate(row['Caption'])
                skill['Details']     = cache.translate(row['Caption2'])

                skill['TypeDamage']  = parse_properties(row) if row['ValueType'] == 'Attack' else ['BUFF']
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

def parse_skills_stances(globals):
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
    for skill in globals.data['skills'].values():
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
                        'Icon': globals.parse_entity_icon(stance['Icon']),
                        'Name': stance['ClassName']
                    })
                else:
                    found = False
                    for stance_sub in stances_sub_weapon:
                        if stance_sub['Icon'] == globals.parse_entity_icon(stance['Icon']):
                            found = True
                            break

                    if not found:
                        stances_sub_weapon.append({
                            'Icon': globals.parse_entity_icon(stance['Icon']),
                            'Name': stance['ClassName']
                        })
        else:
            stances_main_weapon.append({
                'Icon': globals.parse_entity_icon('weapon_All'),
                'Name': 'All'
            })

        if skill['RequiredStanceCompanion'] in ['BOTH', 'YES']:
            stances_main_weapon.append({
                'Icon': globals.parse_entity_icon('weapon_companion'),
                'Name': 'Companion'
            })

        skill['RequiredStance'] = [
            stance for stance in (stances_main_weapon + stances_sub_weapon)
            if stance['Icon'] is not None
        ]

def parse_skills_script(globals):
    """
    parse skills skill factor caption ratio etc which use lua script
    """

    LUA_RUNTIME = luautil.LUA_RUNTIME
    LUA_SOURCE = luautil.LUA_SOURCE

    for g in globals.data['skills'].values():
        sfrs = []
        g['other'] = []
        CaptionRatios = []
        if (g['Effect_SkillFactor']):
            for lv in range(0,g['MaxLevel']+10,1):
                g['Level'] = lv
                sfr = LUA_RUNTIME[g['Effect_SkillFactor']](g)
                if sfr == -1:
                    sfr = 0
                sfrs.append(sfr)
            g['sfr'] = sfrs

        if g['Effect_CaptionRatio']:
            if ( g['Effect_CaptionRatio'] == 'SCR_GET_SwellHands_Ratio'):
                g['other'].append("Effect_CaptionRatio ((maxpatk + minpatk)/2) * (0.02 + skill.Level * 0.002)")
                continue
            if ( g['Effect_CaptionRatio'] == 'SCR_GET_OverReinforce_Ratio'):
                g['other'].append("Effect_CaptionRatio ((maxpatk + minpatk)/2) * (0.015 + skill.Level * 0.004)")
                continue
            for lv in range(0,g['MaxLevel']+10,1):
                g['Level'] = lv
                CaptionRatio = LUA_RUNTIME[g['Effect_CaptionRatio']](g)
                if CaptionRatio == -1:
                    CaptionRatio = 0
                CaptionRatios.append(CaptionRatio)
            g['CaptionRatio'] = CaptionRatios

        CaptionRatios = []
        if g['Effect_CaptionRatio2']:
            if ( g['Effect_CaptionRatio2'] == 'SCR_GET_Sanctuary_Ratio2'):
                g['other'].append("Effect_CaptionRatio2 mdefRate = MDEF * (0.1 * skill.Level)")
                continue
            if ( g['Effect_CaptionRatio2'] == 'SCR_GET_Ayin_sof_Ratio2'):
                g['other'].append("Effect_CaptionRatio2 Hp recovery")
                continue
            for lv in range(0,g['MaxLevel']+10,1):
                g['Level'] = lv
                CaptionRatio = LUA_RUNTIME[g['Effect_CaptionRatio2']](g)
                if CaptionRatio == -1:
                    CaptionRatio = 0
                CaptionRatios.append(CaptionRatio)
            g['CaptionRatio2'] = CaptionRatios

        CaptionRatios = []
        if g['Effect_CaptionRatio3']:
            for lv in range(0,g['MaxLevel']+10,1):
                g['Level'] = lv
                CaptionRatio = LUA_RUNTIME[g['Effect_CaptionRatio3']](g)
                if CaptionRatio == -1:
                    CaptionRatio = 0
                CaptionRatios.append(CaptionRatio)
            g['CaptionRatio3'] = CaptionRatios

def parse_clean(constants):
    skills_to_remove = []
    # Find which skills are no longer active
    for skill in globals.data['skills'].values():
        if skill['Link_Job'] is None:
            skills_to_remove.append(skill)

    # Remove all inactive skills
    for skill in skills_to_remove:
        del constants.data['skills'][str(skill['$ID_NAME'])]

        skill_id = skill['$ID']

        for attribute in globals.data['attributes'].values():
            attr = globals.data['attributes_by_name'][attribute['$ID_NAME']]
            attribute['Link_Skills'] = [link for link in attribute['Link_Skills'] if link != skill_id]
            attr['Link_Skills'] = [link for link in attr['Link_Skills'] if link != skill_id]
        for job in globals.data['jobs'].values():
            job2= globals.data['jobs_by_name'][job['$ID_NAME']]
            job['Link_Skills'] = [link for link in job['Link_Skills'] if link != skill_id]
            job2['Link_Skills'] = [link for link in job2['Link_Skills'] if link != skill_id]
