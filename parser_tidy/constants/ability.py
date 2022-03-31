"""
Created on Fri Apr 1 03:26:47 2022

@author: Nodius
@credit: Temperantia, Nodius
"""

ATTRIBUTE_COST = {
    'ABIL_REINFORCE_PRICE'           : 'ENHANCE',
    'HIDDENABIL_PRICE_COND_REINFORCE': 'ENHANCE_ARTS',
    'ABIL_BASE_PRICE'                : 'BASIC',
    'ABIL_ABOVE_NORMAL_PRICE'        : 'ADVANCED',
    'ABIL_COMMON_PRICE_1LV'          : 'COMMON_001',
    'ABIL_COMMON_PRICE_100LV'        : 'COMMON_100',
    'ABIL_COMMON_PRICE_150LV'        : 'COMMON_150',
    'ABIL_COMMON_PRICE_200LV'        : 'COMMON_200',
    'ABIL_COMMON_PRICE_250LV'        : 'COMMON_250',
    'ABIL_COMMON_PRICE_300LV'        : 'COMMON_300',
    'ABIL_COMMON_PRICE_350LV'        : 'COMMON_350',
    'ABIL_COMMON_PRICE_400LV'        : 'COMMON_400',
    'HIDDENABIL_PRICE_COND_JOBLEVEL' : 'ARTS',
    'ABIL_MASTERY_PRICE'             : '2H_SPEAR_MASTERY_PENETRATION',
    'ABIL_NECROMANCER8_PRICE'        : 'CREATE_SHOGGOTH_ENLARGEMENT',
    'ABIL_TOTALDEADPARTS_PRICE'      : 'NECROMANCER_CORPSE_FRAGMENT_CAPACITY',
    'ABIL_SORCERER2_PRICE'           : 'SORCERER_SP_RECOVERY',
    'ABIL_WARLOCK14_PRICE'           : 'INVOCATION_DEMON_SPIRIT',
    'ABIL_6RANK_NORMAL_PRICE'        : 'CENTURION'
}

ATTACK = {
    'Melee'     : 'MELEE',
    'Missile'   : 'MISSILE',
    'Magic'     : 'MAGIC',
    'Responsive': 'WEAPON_BASED',
    'TrueDamage': 'TRUE_DAMAGE'
}

ELEMENT = {
    'Fire'     : 'FIRE',
    'Lightning': 'LIGHTNING',
    'Ice'      : 'ICE',
    'Earth'    : 'EARTH',
    'Holy'     : 'HOLY',
    'Dark'     : 'DARK',
    'Soul'     : 'PSYCHOKINESIS',
    'Poison'   : 'POISON'
}

TYPE = {
    'Slash' : 'SLASH',
    'Aries' : 'PIERCE',
    'Strike': 'STRIKE',
    'Arrow' : 'ARROW',
    'Gun'   : 'BULLET',
    'Cannon': 'CANNON'
}

def parse_damage_properties(row: dict) -> list:
    damage = []

    if row['ClassType'] in ATTACK:
        damage.append(ATTACK[row['ClassType']])

    if row['AttackType'] in TYPE:
        damage.append(TYPE[row['AttackType']])

    if row['Attribute'] in ELEMENT:
        damage.append(ELEMENT[row['Attribute']])

    return damage