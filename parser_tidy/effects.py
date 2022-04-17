from fnmatch import fnmatch
from logging import getLogger
from os import walk
from os.path import join

from lxml.html import HtmlElement as HTMLElement, parse as parse_xml

import luautil

LOG = getLogger('Parse.SkillByTool')

def parse(root: str, data: dict):
    SELECT_S_R_TGTBUFF = 'ResultList > ToolScp[Scp~="S_R_TGTBUFF"]'
    SELECT_SKL_BUFF    = 'EtcList > Scp[Scp~="SKL_BUFF"]'

    LUA = luautil.LUA

    effect_data = data['skill_effects']

    for path, _, files in walk(join(root, 'skill_bytool.ipf')):
        for xml_path in [file for file in files if fnmatch(file, '*.xml')]:
            LOG.info('Parsing Skill Effects from %s ...', xml_path)

            soup: HTMLElement = parse_xml(join(path, xml_path)).getroot()

            entry: HTMLElement

            for entry in soup.iter('skill'):
                skill = {}

                skill['Effects'] = []

                for tool_scp in entry.cssselect(SELECT_S_R_TGTBUFF):
                    skill['Effects'].append(';'.join([tool_scp[0].get('str'), str(float(tool_scp[3].get('num')) / 1000.0), str(tool_scp[5].get('num'))]))

                for scp in entry.cssselect(SELECT_SKL_BUFF):
                    if scp[3].get('usefunc') == 1:
                        duration = str(float(LUA.execute(scp[3].get('funcTxt'))) / 1000.0)
                    else:
                        duration = str(float(scp[3].get('num')) / 1000.0)
                    
                    if scp[5].get('usefunc') == 1:
                        chance = str(float(LUA.execute(scp[5].get('functxt'))) / 1000.0)
                    else:
                        chance = str(float(scp[5].get('num')) / 1000.0)

                    skill['Effects'].append(';'.join([scp[0].get('str'), duration, chance]))

                if len(skill['Effects']) > 0:
                    skill['$ID_NAME'] = entry.get('name')
                    
                    effect_data[skill['$ID_NAME']] = skill