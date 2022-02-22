"""
Created on Sat Feb 12 20:24:52 2022

@author: Nodius
@credit: Nodius, Temperantia
"""

ADD_DAMAGE = [
    'ADD_FIRE',
    'ADD_ICE',
    'ADD_LIGHTNING',
    'ADD_EARTH',
    'ADD_HOLY',
    'ADD_DARK',
    'ADD_SOUL',
    'ADD_POISON'
]

ADD_DAMAGE_RESISTANCE = [
    'RES_FIRE',
    'RES_LIGHTNING',
    'RES_ICE',
    'RES_EARTH',
    'RES_HOLY',
    'RES_DARK',
    'RES_SOUL',
    'RES_POISON',
]

COLLECTION = {
    'STR_BM': 'STR',
    'DEX_BM': 'DEX',
    'CON_BM': 'CON',
    'INT_BM': 'INT',
    'MNA_BM': 'MNA',

    'PATK_BM'   : 'PATK',
    'CRTATK_BM' : 'CRTATK',
    'MATK_BM'   : 'ADD_MATK',
    'CRTMATK_BM': 'CRTMATK',

    'DEF_BM' : 'DEF',
    'MDEF_BM': 'MDEF',

    'CRTHR_BM': 'CRTHR',
    'CRTDR_BM': 'CRTDR',
    'HR_BM'   : 'ADD_HR',
    'DR_BM'   : 'ADD_DR',

    'MHP_BM'   : 'MHP',
    'MSP_BM'   : 'MSP',
    'RHP_BM'   : 'RHP',
    'RSP_BM'   : 'RSP',
    'MaxSta_BM': 'MSTA',

    'ResEarth_BM': 'RES_EARTH',
    'ResHoly_BM' : 'RES_HOLY',
    'ResDark_BM' : 'RES_DARK',
    
    'MaxWeight_BM'            : 'WEIGHT', # Inventory Weight Limit
    'MaxAccountWarehouseCount': 'STORAGE' # Team Storage Slot
}

EQUIPMENT = [
    'ALLSTAT',             # All Stats
    'STR',                 # Strength
    'DEX',                 # Dexterity
    'CON',                 # Constitution
    'INT',                 # Intelligence
    'MNA',                 # Spirit

    'ADD_MAXATK',          # Maximum Attack
    'ADD_MINATK',          # Minimum Attack
    'PATK',                # Physical Attack
    'CRTATK',              # Critical Physical Attack
    'ADD_MATK',            # Magic Attack
    'CRTMATK',             # Critical Magic Attack
    'ADD_DEF',             # Physical Defense
    'ADD_MDEF',            # Magic Defense

    'CRTHR',               # Critical Rate
    'CRTDR',               # Critical Resistance
    'ADD_HR',              # Accuracy
    'ADD_DR',              # Evasion
    'BLK_BREAK',           # Block Penetration
    'BLK',                 # Block
    'BlockRate',           # Final Block Rate

    'MHP',                 # HP
    'MSP',                 # SP
    'MSTA',                # Stamina
    'RHP',                 # HP Recovery
    'RSP',                 # SP Recovery
    'RSTA',                # Stamina Recovery
    'SR',                  # AoE Attack Ratio
    'SDR',                 # AoE Defense Ratio
    'SkillRange',          # Attack Range
    'MSPD',                # Movement Speed

    'Slash',               # Slash Attack
    'Aries',               # Pierce Attack
    'Strike',              # Strike Attack

    'Magic_Fire_Atk',      # Fire Property Magic Attack
    'Magic_Lightning_Atk', # Lightning Property Magic Attack
    'Magic_Ice_Atk',       # Ice Property Magic Attack
    'Magic_Earth_Atk',     # Earth Property Magic Attack
    'Magic_Holy_Atk',      # Holy Property Magic Attack
    'Magic_Dark_Atk',      # Dark Property Magic Attack
    'Magic_Soul_Atk',      # Psychokinesis Property Magic Attack
    'Magic_Melee_Atk',     # None Property Magic Attack

    'ADD_BOSS_ATK',        # Attack Against Bosses
    'ADD_LARGESIZE',       # Attack Against Large Targets
    'ADD_MIDDLESIZE',      # Attack Against Medium Targets
    'ADD_SMALLSIZE',       # Attack Against Small Targets

    'ADD_CLOTH',           # Attack Against Cloth-Armored Targets
    'ADD_LEATHER',         # Attack Against Leather-Armored Targets
    'ADD_IRON',            # Attack Against Plate-Armored Targets
    'ADD_GHOST',           # Attack Against Ghost-Armored Targets

    'ADD_FORESTER',        # Attack Against Plants
    'ADD_WIDLING',         # Attack Against Beasts
    'ADD_VELIAS',          # Attack Against Demons
    'ADD_PARAMUNE',        # Attack Against Mutants
    'ADD_KLAIDA',          # Attack Against Insects

    'Add_Damage_Atk',      # Additional Damage
    'ADD_FIRE',            # Additional Damage (Legacy)
    'ADD_ICE',             # Additional Damage (Legacy)
    'ADD_LIGHTNING',       # Additional Damage (Legacy)
    'ADD_EARTH',           # Additional Damage (Legacy)
    'ADD_HOLY',            # Additional Damage (Legacy)
    'ADD_DARK',            # Additional Damage (Legacy)
    'ADD_SOUL',            # Additional Damage (Legacy)
    'ADD_POISON',          # Additional Damage (Legacy)

    'SlashDEF',            # Slash Resistance
    'AriesDEF',            # Pierce Resistance
    'StrikeDEF',           # Strike Resistance

    'MiddleSize_Def',      # Offset For Medium Targets

    'Cloth_Def',           # Offset For Cloth-Armored Targets
    'Leather_Def',         # Offset For Leather-Armored Targets
    'Iron_Def',            # Offset For Plate-Armored Targets

    'ResAdd_Damage',       # Additional Damage Resistance
    'RES_FIRE',            # Additional Damage Resistance (Legacy)
    'RES_LIGHTNING',       # Additional Damage Resistance (Legacy)
    'RES_ICE',             # Additional Damage Resistance (Legacy)
    'RES_EARTH',           # Additional Damage Resistance (Legacy)
    'RES_HOLY',            # Additional Damage Resistance (Legacy)
    'RES_DARK',            # Additional Damage Resistance (Legacy)
    'RES_SOUL',            # Additional Damage Resistance (Legacy)
    'RES_POISON'           # Additional Damage Resistance (Legacy)
]