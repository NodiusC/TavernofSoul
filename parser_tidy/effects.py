import glob
import logging
from os.path import join, normpath, sep

from lxml import etree as XML

import luautil
from cache import TOSParseCache as Cache

LOG = logging.getLogger('Parse.SkillByTool')
LOG.setLevel(logging.INFO)

def parse(cache: Cache):
    LUA = luautil.LUA

    for xml_path in glob.glob(join(cache.PATH_INPUT_DATA, 'skill_bytool.ipf', '*.xml')):
        LOG.info('Parsing Skill Effects from %s ...', normpath(xml_path).split(sep)[-1])

        with open(xml_path, 'r', encoding = 'utf-8', errors = 'replace') as xml_file:
            xml = XML.parse(xml_file, recover = True)

            for entry in xml.iter('Skill'):
                skill = {}

                skill['Effects'] = []

                for results in entry.iter('ResultList'):
                    for tool_scp in results.iter('ToolScp'):
                        if tool_scp.get('Scp') == 'S_R_TGTBUFF':
                            skill['Effects'].append(tool_scp[0].get('Str') + ';' + str(float(tool_scp[3].get('Num')) / 1000.0) + ';' + str(tool_scp[5].get('Num')))

                for etc in entry.iter('EtcList'):
                    for scp in etc.iter('Scp'):
                        if scp.get('Scp') == 'SKL_BUFF':
                            if scp[3].get('UseFunc') == 1:
                                duration = str(float(LUA.execute(scp[3].get('FuncTxt'))) / 1000.0)
                            else:
                                duration = str(float(scp[3].get('Num')) / 1000.0)
                            
                            if scp[5].get('UseFunc') == 1:
                                chance = str(float(LUA.execute(scp[5].get('FuncTxt'))) / 1000.0)
                            else:
                                chance = str(float(scp[5].get('Num')) / 1000.0)

                            skill['Effects'].append(scp[0].get('Str') + ';' + duration + ';' + chance)

                if len(skill['Effects']) > 0:
                    skill['$ID_NAME'] = entry.get('Name')
                    
                    cache.data['skill_effects'][skill['$ID_NAME']] = skill