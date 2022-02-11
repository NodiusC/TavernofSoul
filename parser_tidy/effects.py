import glob
import logging
import luautil
import xml.etree.ElementTree as ET

from cache import TOSParseCache as Cache
from codecs import open
from os.path import join, normpath, sep

LOG = logging.getLogger('Parse.SkillByTool')
LOG.setLevel(logging.INFO)

def parse(cache: Cache):
    for xml_path in glob.glob(join(cache.PATH_INPUT_DATA, 'skill_bytool.ipf', '*.xml')):
        LOG.info('Parsing Skill Effects from %s ...', normpath(xml_path).split(sep)[-1])

        with open(xml_path, 'r', encoding = 'utf-8', errors = 'replace') as xml_file:
            xml = ET.parse(xml_file)

            for entry in xml.iter('Skill'):
                skill = {}

                skill['Effects'] = []

                for results in entry.iter('ResultList'):
                    for tool_scp in results.iter('ToolScp'):
                        if tool_scp.get('Scp') == 'S_R_TGTBUFF':
                            skill['Effects'].append(tool_scp[1].get('Str') + ';' + str(float(tool_scp[4].get('Num') / 1000.0)) + ';' + str(tool_scp[6].get('Num')))

                lua = luautil.lua

                for etc in entry.iter('EtcList'):
                    for scp in etc.iter('Scp'):
                        if scp.get('Scp') == 'SKL_BUFF':
                            if scp[4].get('UseFunc') == 1:
                                duration = str(float(lua.execute(scp[4].get('FuncTxt'))) / 1000.0)
                            else:
                                duration = str(float(scp[4].get('Num')) / 1000.0)
                            
                            if scp[6].get('UseFunc') == 1:
                                chance = str(float(lua.execute(scp[6].get('FuncTxt'))) / 1000.0)
                            else:
                                chance = str(float(scp[6].get('Num')) / 1000.0)

                            skill['Effects'].append(scp[1].get('Str') + ';' + duration + ';' + chance)

                if len(skill['Effects']) > 0:
                    skill['$ID_NAME'] = entry.get('Name')
                    
                    cache.data['skill_effects'][skill['$ID_NAME']] = skill