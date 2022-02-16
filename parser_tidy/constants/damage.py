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

def of(class_type: str, attack_type: str, attribute: str) -> list:
    damage = []

    if class_type in ATTACK:
        damage.append(ATTACK[class_type])

    if attack_type in TYPE:
        damage.append(TYPE[attack_type])

    if attribute in ELEMENT:
        damage.append(ELEMENT[attribute])

    return damage