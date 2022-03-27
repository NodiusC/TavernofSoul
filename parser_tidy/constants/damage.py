"""
Created on Sun Feb 13 17:19:27 2022

@author: Nodius
@credit: Temperantia, Nodius
"""

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

def of(row: dict) -> list:
    damage = []

    if row['ClassType'] in ATTACK:
        damage.append(ATTACK[row['ClassType']])

    if row['AttackType'] in TYPE:
        damage.append(TYPE[row['AttackType']])

    if row['Attribute'] in ELEMENT:
        damage.append(ELEMENT[row['Attribute']])

    return damage