"""
Created on Fri Apr 1 03:20:01 2022

@author: Nodius
@credit: Nodius, Temperantia
"""

ADD_DAMAGE_STATS = [
    'ADD_FIRE',      # Additional Damage (Legacy)
    'ADD_ICE',       # Additional Damage (Legacy)
    'ADD_LIGHTNING', # Additional Damage (Legacy)
    'ADD_EARTH',     # Additional Damage (Legacy)
    'ADD_HOLY',      # Additional Damage (Legacy)
    'ADD_DARK',      # Additional Damage (Legacy)
    'ADD_SOUL',      # Additional Damage (Legacy)
    'ADD_POISON'     # Additional Damage (Legacy)
]

ADD_DAMAGE_RESISTANCE_STATS = [
    'RES_FIRE',      # Additional Damage Resistance (Legacy)
    'RES_LIGHTNING', # Additional Damage Resistance (Legacy)
    'RES_ICE',       # Additional Damage Resistance (Legacy)
    'RES_EARTH',     # Additional Damage Resistance (Legacy)
    'RES_HOLY',      # Additional Damage Resistance (Legacy)
    'RES_DARK',      # Additional Damage Resistance (Legacy)
    'RES_SOUL',      # Additional Damage Resistance (Legacy)
    'RES_POISON'     # Additional Damage Resistance (Legacy)
]

COLLECTION_STATS = {
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

EQUIPMENT_STATS = [
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
    # 'RSTA',              # Stamina Recovery (Legacy)
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

    'SlashDEF',            # Slash Resistance
    'AriesDEF',            # Pierce Resistance
    'StrikeDEF',           # Strike Resistance

    'MiddleSize_Def',      # Offset For Medium Targets

    'Cloth_Def',           # Offset For Cloth-Armored Targets
    'Leather_Def',         # Offset For Leather-Armored Targets
    'Iron_Def',            # Offset For Plate-Armored Targets

    'ResAdd_Damage',       # Additional Damage Resistance
]

TRADABILITY = ['Shop', 'Market', 'Team', 'User']

VISION_TO_CLASS = {
    # Swordsman
    'TSW04_126_1' : 1002, # Highlander       - Dual Sword
    'SWD04_126_5' : 1003, # Peltasta         - Serrated Shield
    'SPR04_127_1' : 1004, # Hoplite          - Javelin
    'SWD04_126_8' : 1006, # Barbarian        - Wrath
    'TSP04_128_2' : 1007, # Cataphract       - Matchless
    'TSW04_126_2' : 1009, # Doppelsoeldner   - Wedge Blast
    'SWD04_126_1' : 1010, # Rodelero         - Escudo Espada
    'SWD04_126_7' : 1012, # Murmillo         - Arena
    'RAP04_124'   : 1014, # Fencer           - Leventador
    'TSP04_128'   : 1015, # Dragoon          - Halberd
    # '' : 1016, # Templar          -
    'TSP04_128_1' : 1017, # Lancer           - Grind
    'RAP04_124_1' : 1018, # Matador          - Banderilla
    'SWD04_126_4' : 1019, # Nak Muay         - Boreas
    'SPR04_127'   : 1020, # Retiarius        - Rete Shooter
    'SWD04_126_2' : 1021, # Hackapell        - Saber
    'TSW04_126'   : 1022, # Blossom Blader   - Florescence
    'SWD04_126_6' : 1023, # Luchador         - Doble Attaque

    # Wizard
    'TSF04_129_2' : 2002, # Pyromancer       - Fire Bolt
    'STF04_127_2' : 2003, # Cryomancer       - Ice Snowdrops
    'TSF04_129_3' : 2004, # Psychokino       - Biased Gravity
    # '' : 2005, # Alchemist        - 
    'STF04_127_1' : 2006, # Sorcerer         - Wicked Desire
    'STF04_127'   : 2008, # Chronomancer     - Time Rush
    'TSF04_129_7' : 2009, # Necromancer      - Immortality
    'TSF04_129_6' : 2011, # Elementalist     - Annihilate
    'STF04_127_4' : 2014, # Sage             - Distortion
    'TSF04_129_8' : 2015, # Warlock          - Demonische
    'TSF04_129_11': 2016, # Featherfoot      - Blood
    'STF04_127_3' : 2017, # Rune Caster      - Rune of Vigilance
    'TSF04_129_1' : 2019, # Shadowmancer     - Diffuse Reflection
    'TSF04_129_5' : 2020, # Onmyoji          - Red Tiger Claw
    'TSF04_129_10': 2024, # Taoist           - Awakening
    'TSF04_129_4' : 2022, # Bokor            - Lewa Advent
    'TSF04_129'   : 2023, # Terramcner       - Stone-Slinger
    'TSF04_129_9' : 2024, # Keraunos         - Electric Flow

    # Archer
    # '' : 3002, # Hunter           - 
    'BOW04_126_1' : 3003, # Quarrel Shooter  - Cluster Bomb
    'TBW04_126_5' : 3004, # Ranger           - Tempest
    # '' : 3005, # Sapper           - 
    'TBW04_126_3' : 3006, # Wugushi          - Shadowless Poison
    'TBW04_126'   : 3011, # Fletcher         - Reinforced Bowstring
    # '' : 3012, # Pied Piper       - 
    # '' : 3013, # Appraiser        - 
    'TBW04_126_2' : 3014, # Falconer         - Hawking
    'CAN04_118'   : 3015, # Cannoneer        - Air Burst
    'MUS04_118'   : 3016, # Musketeer        - Armor-Piercing Shell
    'TBW04_126_1' : 3017, # Mergen           - Orbital Arrow
    'CAN04_118_1' : 3101, # Matross          - Centerfire
    'MUS04_118_1' : 3102, # Tiger Hunter     - Triple Steps Single Shot
    'BOW04_126'   : 3103, # Arbalester       - Double Marking
    'MUS04_118_2' : 3104, # Arquebusier      - Lever Action
    'TBW04_126_4' : 3105, # Hwarang          - Jusalnegi

    # Cleric
    'MAC04_129'   : 4002, # Priest           - Mass Heal: Freeze
    'TMAC04_118_6': 4003, # Krivis           - Sacred Lightning
    # '': 4005, # Druid            - 
    'TMAC04_118_4': 4006, # Sadhu            - Agni
    'MAC04_129_3' : 4007, # Dievdirbys       - Memory Leap
    # '' : 4008, # Oracle           - 
    'TMAC04_118_5': 4009, # Monk             - Thunder Kick
    # '' : 4010, # Pardoner         - 
    'MAC04_129_2' : 4011, # Paladin          - Protecting Grace
    'MAC04_129_1' : 4012, # Chaplain         - Sacred Armor
    'TMAC04_118_3': 4014, # Plague Doctor    - Necrosis
    # '' : 4015, # Kabbalist        - 
    'TMAC04_118_1': 4016, # Inquisitor       - Outrage
    'TMAC04_118_8': 4018, # Miko             - Ema
    'TMAC04_118_7': 4019, # Zealot           - Conviction
    'TMAC04_118_2': 4020, # Exorcist         - Desition
    'TMAC04_118'  : 4021, # Crusader         - Convict

    # Scout
    'DAG04_123_7' : 5002, # Assassin         - Gasp Up
    'PST04_122_3' : 5003, # Outlaw           - Sabotage
    # '' : 5004, # Squire           - 
    'PST04_122_4' : 5005, # Corsair          - Critical Edge
    'DAG04_123_1' : 5006, # Shinobi          - Shadow Clone
    'DAG04_123_8' : 5007, # Thaumaturge      - Rapid Growth
    'DAG04_123_10': 5008, # Enchanter        - Empowering
    'DAG04_123_9' : 5009, # Linker           - Superstring
    'DAG04_123_3' : 5010, # Rogue            - Phantom Blade
    'PST04_122_1' : 5011, # Schwarzer Reiter - Renovate Trigger
    'PST04_122'   : 5012, # Bullet Marker    - Cryolite Bullet
    'DAG04_123_2' : 5013, # Ardito           - Carpet Bombing
    'PST04_122_2' : 5014, # Sheriff          - Speedloader
    'DAG04_123'   : 5015, # Rangda           - Cursed Dagger
    'DAG04_123_5' : 5016, # Clown            - Ecliptic Blades
    'PST04_122_5' : 5017, # Hakkapeliitta    - Carbine
}