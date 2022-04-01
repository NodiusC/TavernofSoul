# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 08:06:31 2021

@author: Temperantia
"""

import csv
import io
import logging
import os
import re
from os.path import join

import constants.ies as IES
import iesutil
from cache import TOSParseCache as Cache
from lupa import LuaRuntime, LuaError

LUA_OVERRIDE = [
    'function GET_ITEM_LEVEL(item) return 0 end',  # We cant emulate this function as geItemTable is undefined
    'function IsBuffApplied(pc, buff) return "NO" end',
    'function IsServerSection(pc) return 0 end',
    'function GetExProp(entity, name) return entity[name] end',
    'function GetExProp_Str(entity, name) return tostring(entity[name]) end',
    'function GetIESID(item) end',
    'function GetItemOwner(item) return {} end',
    'function GetOwner(monster) end',
    'function GetServerNation() end',
    'function GetServerGroupID() end',
    'function IsPVPServer(itemOwner) end',
    'function IMCRandom(min, max) return 0 end',
    'function ScpArgMsg(a, b, c) return "" end',
    'function SCR_MON_OWNERITEM_ARMOR_CALC(self, defType) return 0 end',
    'function SetExProp(entity, name, value) entity[name] = value end',
    'function pow(a,b) return a ^ b end',
    'function SCR_PVP_ITEM_LV_GRADE_REINFORCE_SET(item, lv, grade, reinforceValue, reinforceRatio)\
        return lv, grade, reinforceValue, reinforceRatio;\
    end',
    'function OVERRIDE_INHERITANCE_PROPERTY(item) return 0 end',
    'function SCR_PVP_ITEM_TRANSCEND_SET(item, transcend)\
        return transcend;\
    end',
    '''
    function IS_WEAPON_TYPE(type)
        if (type ~= "Boots") then
            return false
        end
        if (type ~= "Gloves") then
            return false
        end
        if (type ~= "Pants") then
            return false
        end
        if (type ~= "Shirt") then
            return false
        end
        return true
    end
    ''',
    'function GetZoneName() return nil end',
    'function GetSkillOwner(skill) return skill end',
    'function GetSkill(pc, skillname) return pc end',
    'function  GetAbility(pc, name) return nill end',
    'function IsInTOSHeroMap(pc) return true end',
    'function IsPVPField(pc) return 0 end',
    'function IsServerObj(item) return 0 end',
    '''
    function SCR_GET_SPEND_ITEM_Alchemist_SprinkleHPPotion(pc)
        return GetClassByType('Item', 641219), 641219
    end
    ''',
    '''
    function SCR_GET_SPEND_ITEM_Alchemist_SprinkleSPPotion(pc)
        return GetClassByType('Item', 641233), 641233
    end
    ''',
    'function GetAbilityAddSpendValue(pc, ClassName, CD) return 0 end',
    'function IsRaidField(pc) return 0 end',
    'function GetMyJobHistoryString(pc) return "" end',
    'function GetJobHistoryList(pc) return {} end',
    'function IS_TOS_HERO_ZONE(pc) return "NO" end',
    'function IsJoinColonyWarMap(pc) return 0 end ',
    'function GetBuffByProp(row,keyword, key) return nil end',
    '''
    function SCR_STRING_CUT(inputstr, sep)
        if sep == nil then
          sep = "%s"
        end
        local t={}
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
            table.insert(t, str)
        end
        return t
    end
    '''

]

LUA_RUNTIME = None
LUA_SOURCE  = None

# HOTFIX: Don't throw errors when LUA is getting an unknown key
def attr_getter(obj, name):
    if name in obj:
        if name in ['Blockable', 'HPCount', 'ReinforceArmor', 'TranscendArmor', 'ReinforceWeapon', 'TranscendWeapon']:
            return int(obj[name])
        else:
            return obj[name]

    return 0

def attr_setter(obj, name, value):
    obj[name] = value

LUA = LuaRuntime(attribute_handlers = (attr_getter, attr_setter), unpack_returned_tuples = True)

def init(cache: Cache):
    init_global_constants(cache, 'sharedconst.ies')
    init_global_constants(cache, 'sharedconst_system.ies')
    init_global_data(cache)
    init_global_functions()
    init_runtime(cache)

def init_global_constants(cache: Cache, file_name: str):
    execute = ''

    ies_path = join(cache.PATH_INPUT_DATA_LUA, 'ies.ipf', file_name)

    with io.open(ies_path, 'r', encoding = 'utf-8') as ies_file:
        for row in csv.DictReader(ies_file, delimiter = ',', quotechar = '"'):
            if row['UseInScript'] == 'NO':
                continue

            execute += row['ClassName'] + ' = ' + row['Value'] + '\n'

    LUA.execute(execute)

def init_global_data(cache: Cache):
    ies_ADD = LUA.execute('''
        ies_by_ClassID = {}
        ies_by_ClassName = {}

        function ies_ADD(key, data)
            _by_ClassID = {}
            _by_ClassName = {}

            if ies_by_ClassID[key] ~= nil then
                _by_ClassID = ies_by_ClassID[key]
            end
            if ies_by_ClassName[key] ~= nil then
                _by_ClassName = ies_by_ClassName[key]
            end

            for i, row in python.enumerate(data) do
                _by_ClassID[math.floor(row["ClassID"])] = row
                _by_ClassName[row["ClassName"]] = row
            end

            ies_by_ClassID[key] = _by_ClassID
            ies_by_ClassName[key] = _by_ClassName
        end

        return ies_ADD
    ''')

    ies_ADD('ancient', iesutil.load('Ancient_Info.ies',c))
    ies_ADD('ancient_info', iesutil.load('Ancient_Info.ies',c))
    ies_ADD('item', iesutil.load('item_equip.ies',c))
    ies_ADD('item', iesutil.load('item_Equip_EP12.ies',c))
    ies_ADD('increasecost', iesutil.load('item_IncreaseCost.ies',c))
    ies_ADD('item_grade', iesutil.load('item_grade.ies',c))
    ies_ADD('item_growth', iesutil.load('item_growth.ies',c))
    ies_ADD('monster', iesutil.load('monster.ies',c))
    ies_ADD('monster', iesutil.load('monster_event.ies',c))
    ies_ADD('monster', iesutil.load('Monster_solo_dungeon.ies',c))
    ies_ADD('stat_monster', iesutil.load('statbase_monster.ies',c))
    ies_ADD('stat_monster_race', iesutil.load('statbase_monster_race.ies',c))
    ies_ADD('stat_monster_type', iesutil.load('statbase_monster_type.ies',c))
    ies_ADD('skillrestrict', iesutil.load('skill_restrict.ies',c))
    #skill_restrict.ies

        ies_ADD('item', iesutil.load(i, cache))

    ies_ADD('increasecost',      iesutil.load('item_IncreaseCost.ies',     cache))
    ies_ADD('item_grade',        iesutil.load('item_grade.ies',            cache))
    ies_ADD('item_growth',       iesutil.load('item_growth.ies',           cache))
    ies_ADD('monster',           iesutil.load('monster.ies',               cache))
    ies_ADD('monster',           iesutil.load('monster_event.ies',         cache))
    ies_ADD('monster',           iesutil.load('Monster_solo_dungeon.ies',  cache))
    ies_ADD('stat_monster',      iesutil.load('statbase_monster.ies',      cache))
    ies_ADD('stat_monster_race', iesutil.load('statbase_monster_race.ies', cache))
    ies_ADD('stat_monster_type', iesutil.load('statbase_monster_type.ies', cache))
    ies_ADD('skillrestrict',     iesutil.load('skill_restrict.ies',        cache))

def init_global_functions():
    LUA.execute('''
        app = {
            IsBarrackMode = function() return false end
        }

        exchange = {
            GetExchangeItemInfoByGuid = function(guid) end
        }

        geTime = {
            GetServerSystemTime = function()
                local date = os.date("*t")

                return {
                    wDay = date.day,
                    wMonth = date.month,
                    wYear = date.year
                }
            end
        }

        session = {
            GetEquipItemByGuid = function(guid) end,
            GetEtcItemByGuid = function(guid) end,
            GetInvItemByGuid = function(guid) end,

            link = {
                GetGCLinkObject = function(guid) end
            },

            market = {
                GetCabinetItemByItemObjID = function(itemID) end,
                GetItemByItemID = function(itemID) end
            },

            otherPC = {
                GetItemByGuid = function(guid) end
            },

            pet = {
                GetPetEquipObjByGuid = function(guid) end
            },
            party = {
                GetMyPartyObj = function(guid) end,
                GetPartyMemberList = function(guid) end
            }
        }


        function GetClassByNumProp(ies_key, column, value)
            local data = ies_by_ClassID[string.lower(ies_key)]
            for id, row in pairs(data) do
                if TryGetProp(row, column) == value then
                    return row
                end
            end
        end

        function GetClass(ies_key, name)
            local data = ies_by_ClassName[string.lower(ies_key)]
            return data[name]
        end
        function GetClassByType(ies_key, id)
            local data = ies_by_ClassID[string.lower(ies_key)]
            return data[math.floor(id)]
        end

        function GetClassList(ies_key)
            return ies_by_ClassID[string.lower(ies_key)]
        end
        function GetClassByNameFromList(data, key)
            for id, row in pairs(data) do
                if TryGetProp(row, "ClassName") == key then
                    return row
                end
            end
        end

        function MinMaxCorrection(value, min, max)
            if value < min then
                return min
            elseif value > max then
                return max
            else
                return value
            end
        end

        -- http://lua-users.org/wiki/SplitJoin @PeterPrade
        function StringSplit(text, delimiter)
           local list = {}
           local pos = 1
           if string.find("", delimiter, 1) then -- this would result in endless loops
              error("delimiter matches empty string!")
           end
           while 1 do
              local first, last = string.find(text, delimiter, pos)
              if first then -- found?
                 table.insert(list, string.sub(text, pos, first-1))
                 pos = last+1
              else
                 table.insert(list, string.sub(text, pos))
                 break
              end
           end
           return list
        end



        function SyncFloor(number)
            return math.floor(number)
        end

        -- https://stackoverflow.com/a/664557 some LUA table helper functions
        function table.set(t) -- set of list
          local u = { }
          for _, v in ipairs(t) do u[v] = true end
          return u
        end
        function table.find(t, value)
          for k, v in pairs(t) do
            if v == value then
              return k
            end
          end
          return nil
        end

        function TryGetProp(item, prop, default)
            if item == nil then
                return default
            end

            local value = item[prop]

            if tonumber(value) ~= nil then
                return tonumber(value)
            end

            if value ~= nil then
                return value
            else
                return default
            end
        end


    ''' + '\n'.join(LUA_OVERRIDE))

def init_runtime(cache: Cache):
    global LUA_RUNTIME, LUA_SOURCE

    LUA_RUNTIME = {}
    LUA_SOURCE  = {}

    for root, dirs, file_list in os.walk(cache.PATH_INPUT_DATA):
        for file_name in file_list:
            if file_name.upper().endswith('.LUA'):

                file_path    = join(root, file_name)
                lua_function = []

                with open(file_path, 'r',errors = 'ignore', encoding = 'utf-8') as file:
                    try:
                        # Remove multiline comments https://stackoverflow.com/a/40454391
                        file_content = file.readlines()
                        file_content = ''.join(file_content)
                        file_content = re.sub(r'--\[(=*)\[(.|\n)*?\]\1\]', '', file_content)

                        # Load LUA functions
                        for line in file_content.split('\n'):
                            line = line.strip()

                            if line.startswith("\ufeff") or line.startswith("--"):
                                continue

                            line = line.replace('\xef\xbb\xbf', '') # Remove UTF8-BOM
                            line = line.replace('\{', '\\\\{')      # Fix regex escaping
                            line = line.replace('\}', '\\\\}')      # Fix regex escaping

                            line = re.sub(r'\[\"(\w*?)\"\]', r"['\1']", line)                           # Replace double quote with single quote
                            line = re.sub(r'local \w+ = require[ (]["\']\w+["\'][ )]*', '', line)       # Remove require statements
                            line = re.sub(r'function (\w+):(\w+)\((.*)\)', r'function \1.\2(\3)', line) # Replace function a:b with function a.b

                            if len(line) == 0:
                                continue

                            if bool(re.match(r'(local\s+)?function\s+[\w.:]+\(.*?\)', line)):
                                try:
                                    lua_function_load(lua_function)

                                except LuaError as error:
                                    continue

                                lua_function = []

                            lua_function.append(line)

                        lua_function_load(lua_function)

                    except LuaError as error:
                        logging.warn('Failed to load %s, error: %s...', file_path, error)
                        err.append(lua_function)
                        continue

def destroy():
    global LUA, LUA_OVERRIDE, LUA_RUNTIME, LUA_SOURCE

    LUA          = None
    LUA_OVERRIDE = None
    LUA_RUNTIME  = None
    LUA_SOURCE   = None

def lua_function_load(function_source):
    if len(function_source) == 0:
        return

    function_execute = [line for line in function_source if not line.startswith('--')]
    function_execute = '\n'.join(function_execute) + '\n'

    if function_source[0].startswith('function '):
        function_name = lua_function_name(function_source[0])

        # Ignore any function that was overridden
        if not any(function_name in s for s in LUA_OVERRIDE):
            LUA.execute(function_execute)

            LUA_SOURCE[function_name] = '\n'.join(function_source)
            LUA_RUNTIME[function_name] = lua_function_reference(function_name)

    else:
        LUA.execute(function_execute)

def lua_function_name(function):
    return function[function.index('function ') + len('function '):function.index('(')].strip()

def lua_function_reference(function_name):
    # In order to return a named LUA function, we need to add a return statement in the end
    # read more: https://github.com/scoder/lupa/issues/22
    return LUA.execute('return ' + function_name)

def lua_function_source(function):
    result = []

    for line in function.splitlines():
        line = line.strip()

        # Remove empty lines
        if len(line) == 0:
            continue

        # Remove comment-only lines
        if line.startswith('--'):
            continue

        result.append(line)

    return result

def lua_function_source_format(function_source):
    level = 0
    result = []

    TOKEN_LEVEL_INCREASE = ['else', 'for', 'function', 'if']
    TOKEN_LEVEL_DECREASE = ['end', 'else']

    for line in function_source:

        # insert extra empty lines (to increase readability)
        if line.find('if') == 0:
            result.append('')

        # << indentation
        if any(line.find(s) == 0 for s in TOKEN_LEVEL_DECREASE):
            level = level - 1

        result.append((level * 4) * ' ' + line)

        # >> indentation
        if any(line.find(s) == 0 for s in TOKEN_LEVEL_INCREASE):
            level = level + 1

        # insert extra empty lines (to increase readability)
        if line.find('end') == 0:
            result.append('')

    return result

def lua_function_source_to_javascript(function_source):
    result = []

    for line in lua_function_source_format(function_source):
        if line.strip().startswith('--'):
            continue

        if '^' in line:
            parts = line.split('^')
            for i in range(len(parts)):
                if i == len(parts) - 1:
                    break

                part_left = lua_function_source_to_javascript_argument(parts[i], -1)
                part_right = lua_function_source_to_javascript_argument(parts[i + 1], 1)

                line = line.replace('^', '')
                line = line.replace(part_left, 'Math.pow(' + part_left)
                line = line.replace(part_right, ', ' + part_right + ')')

        line = line + ' {' if line.find('function ') == 0 else line
        line = line.replace('~=', '!=')
        line = line.replace('local ', 'var ')
        line = line.replace('math.', 'Math.')
        line = line.replace(':', '.')

        line = re.sub(r'--(.+)', '', line)
        line = re.sub(r'#(\w+)', r'\1.length', line)
        line = re.sub(r'\band\b', ' && ', line)
        line = re.sub(r'\bor\b', ' || ', line)
        line = re.sub(r'\bend\b', '}', line)
        line = re.sub(r'\belse\b', '} else {', line)
        line = re.sub(r'\belseif\b', '} else if', line)
        line = re.sub(r'\bnil\b', 'null', line)
        line = re.sub(r'{((?:"\w+"[,\s]*)+)}', r'[\1]', line)                                                      # Arrays
        line = re.sub(r'^(\s*)([^\s]+?),\s*([^\s]+?)\s*=\s*([^\s]+?),\s*([^\s]+?)$', r'\1\2 = \4; \3 = \5;', line) # Multiple Variable Association

        result.append(line)

    result = '\n'.join(result)

    result = re.sub(r'for ([^,]+?)=([^,]+?),([^,]+?),([^,]+?)do', r'for (var \1 = \2; \1 <= \3; \1 += \4) {', result, flags = re.DOTALL)
    result = re.sub(r'for ([^,]+?)=([^,]+?),([^,]+?)do', r'for (var \1 = \2; \1 <= \3; \1 ++) {', result, flags = re.DOTALL)
    result = re.sub(r'if (.+?) then', r'if (\1) {', result, flags = re.DOTALL)
    result = result.splitlines()

    return result

def lua_function_source_to_javascript_argument(text, direction):
    i = 0

    parenthesis       = 0
    parenthesis_open  = '(' if direction == 1 else ')'
    parenthesis_close = ')' if direction == 1 else '('

    text = text[::-1] if direction == -1 else text
    text = text + ' '  # HOTFIX: To never stop at a particular character

    for i in range(len(text)):
        char = text[i]

        if char in (' ', '\n', parenthesis_close) and i > 0 and parenthesis == 0:
            break

        if char == parenthesis_open:
            parenthesis = parenthesis + 1

        if char == parenthesis_close:
            parenthesis = parenthesis - 1

    return text[:i][::-1] if direction == -1 else text[:i]
