# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 09:14:45 2021

@author: CPPG02619
"""

def insert_static(c):
    vaivora_vision = c.data['items']['R_misc_ore25'].copy()

    vaivora_vision['$ID'] =  '00000000'
    vaivora_vision['$ID_NAME'] = 'ViboraArcane_Random_Lv1'
    vaivora_vision['Name'] = 'Random Vaivora Vision lv 1'
    vaivora_vision['Icon'] = 'icon_item_vibora_vision'
    vaivora_vision['Link_Materials'] = []
    vaivora_vision['Link_Target'] = []
    vaivora_vision['Type'] = ''
    vaivora_vision['Description'] = 'Dummy for Random Vaivora Vision Drop'

    c.data['items'] ['ViboraArcane_Random_Lv1'] = vaivora_vision
    
    silver_coin = c.data['items']['ViboraArcane_Random_Lv1'].copy()

    silver_coin['$ID'] =  '00000001'
    silver_coin['$ID_NAME'] = 'Moneybag1'
    silver_coin['Name'] = 'Silver'
    silver_coin['Icon'] = 'icon_item_silver'
    silver_coin['Link_Materials'] = []
    silver_coin['Link_Target'] = []
    silver_coin['Type'] = ''
    silver_coin['Description'] = 'A Silver Coin'

    c.data['items']['Moneybag1'] = silver_coin

    goddess_coin = c.data['items']['ViboraArcane_Random_Lv1'].copy()

    goddess_coin['$ID'] =  '00000002'
    goddess_coin['$ID_NAME'] = 'GabijaCertificate'
    goddess_coin['Name'] = 'Gabija Coin'
    goddess_coin['Icon'] = 'icon_item_gabijacertificatecoin_1p'
    goddess_coin['Link_Materials'] = []
    goddess_coin['Link_Target'] = []
    goddess_coin['Type'] = ''
    goddess_coin['Description'] = 'Dummy for Gabija Coin'
    
    c.data['items']['GabijaCertificate'] = goddess_coin