import unittest
from datetime import datetime
from brains import main


cases = [
    {   'name': '',
        'input':
            '',
        'output':
            [''],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },


    {   'name': 'sg_stock',
        'input':
            '📦Storage (2181/4000):\n'
            'Use /sg_{code} to trade some amount of resource for 1💰/pcs\n'
            '\n'
            '/sg_05 Coal (1)\n'
            '/sg_03 Pelt (2)\n'
            '/sg_02 Stick (2)\n'
            '/sg_01 Thread (1)',
        'output':
            [
                '54.525% full',

                '/wts_01_1_1000 Thread\n'
                '/wts_02_2_1000 Stick',

                '<code>/g_deposit 03 2</code> Pelt\n'
                '<code>/g_deposit 05</code> Coal'
            ],
        'matches':
            {
                'storage_match': True,
                'more_match': False,
                'generic_match': True,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'stock',
        'input':
            '📦Storage (1633/4000):\n'
            'Bauxite (4)\n'
            'Bone powder (9)\n'
            'Bone (42)\n'
            'Charcoal (19)\n'
            'Cloth (127)\n'
            'Coal (4)\n'
            'Coke (10)\n'
            'Crafted leather (1)\n'
            'Iron ore (757)\n'
            'Leather (109)\n'
            'Magic stone (2)\n'
            'Metal plate (2)\n'
            'Pelt (226)\n'
            'Powder (223)\n'
            'Ruby (1)\n'
            'Silver ore (13)\n'
            'Solvent (5)\n'
            'Thread (447)',
        'output':
            [
                '40.825% full',

                '/wts_01_447_1000 Thread\n'
                '/wts_08_10_1000 Iron ore',

                '<code>/g_deposit 03 226</code> Pelt\n'
                '<code>/g_deposit 04 42</code> Bone\n'
                '<code>/g_deposit 05 4</code> Coal\n'
                '<code>/g_deposit 06 19</code> Charcoal\n'
                '<code>/g_deposit 07 223</code> Powder\n'
                '<code>/g_deposit 08 747</code> Iron ore\n'
                '<code>/g_deposit 09 127</code> Cloth\n'
                '<code>/g_deposit 10 13</code> Silver ore\n'
                '<code>/g_deposit 11 4</code> Bauxite\n'
                '<code>/g_deposit 13 2</code> Magic stone\n'
                '<code>/g_deposit 16 5</code> Solvent\n'
                '<code>/g_deposit 17</code> Ruby\n'
                '<code>/g_deposit 20 109</code> Leather\n'
                '<code>/g_deposit 21 9</code> Bone powder\n'
                '<code>/g_deposit 23 10</code> Coke\n'
                '<code>/g_deposit 33 2</code> Metal plate\n'
                '<code>/g_deposit 35</code> Crafted leather'
            ],
        'matches':
            {
                'storage_match': True,
                'more_match': False,
                'generic_match': True,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'more',
        'input':
            '📦Your stock:\n'
            '/a_11 Bauxite x 3\n'
            '/a_21 Bone powder x 2\n'
            '/a_04 Bone x 9\n'
            '/a_06 Charcoal x 3\n'
            '/a_09 Cloth x 4\n'
            '/a_05 Coal x 7\n'
            '/a_23 Coke x 3\n'
            '/a_08 Iron ore x 2\n'
            '/a_20 Leather x 7\n'
            '/a_13 Magic stone x 1\n'
            '/a_33 Metal plate x 3\n'
            '/a_34 Metallic fiber x 1\n'
            '/a_03 Pelt x 7\n'
            '/a_07 Powder x 21\n'
            '/a_31 Rope x 2\n'
            '/a_10 Silver ore x 11\n'
            '/a_16 Solvent x 2\n'
            '/a_02 Stick x 1\n'
            '/a_01 Thread x 9',
        'output':
            [
                '/wts_01_9_1000 Thread\n'
                '/wts_02_1_1000 Stick\n'
                '/wts_08_2_1000 Iron ore',

                '<code>/g_deposit 03 7</code> Pelt\n'
                '<code>/g_deposit 04 9</code> Bone\n'
                '<code>/g_deposit 05 7</code> Coal\n'
                '<code>/g_deposit 06 3</code> Charcoal\n'
                '<code>/g_deposit 07 21</code> Powder\n'
                '<code>/g_deposit 09 4</code> Cloth\n'
                '<code>/g_deposit 10 11</code> Silver ore\n'
                '<code>/g_deposit 11 3</code> Bauxite\n'
                '<code>/g_deposit 13</code> Magic stone\n'
                '<code>/g_deposit 16 2</code> Solvent\n'
                '<code>/g_deposit 20 7</code> Leather\n'
                '<code>/g_deposit 21 2</code> Bone powder\n'
                '<code>/g_deposit 23 3</code> Coke\n'
                '<code>/g_deposit 31 2</code> Rope\n'
                '<code>/g_deposit 33 3</code> Metal plate\n'
                '<code>/g_deposit 34</code> Metallic fiber'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': True,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'crafting',
        'input':
            'Royal Boots part (1)\n'
            'Royal Gauntlets part (1)\n'
            '📃Royal Gauntlets recipe (1) /view_r41\n'
            'Royal Helmet fragment (1)',
        'output':
            [
                '<code>/g_deposit k39</code> Royal Helmet fragment\n'
                '<code>/g_deposit k40</code> Royal Boots part\n'
                '<code>/g_deposit k41</code> Royal Gauntlets part\n'
                '<code>/g_deposit r41</code> Royal Gauntlets recipe'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': True,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'crafting2',
        'input':
            '📃Royal Gauntlets recipe (1) /view_r41',
        'output':
            [
                '<code>/g_deposit r41</code> Royal Gauntlets recipe'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': True,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'missing',
        'input':
            'Not enough materials. Missing:\n'
            ' 11 x Powder\n'
            ' 9 x Charcoal\n'
            ' 9 x Stick\n'
            ' 7 x Iron ore\n'
            ' 64 x Pelt\n'
            ' 1 x Silver ore\n'
            ' 22 x Coal\n'
            ' 2 x Bauxite\n'
            ' 15 x Thread\n'
            ' 1 x Solvent',
        'output':
            [
                'Not enough materials. Missing:\n'
                ' 11 x Powder\n 9 x Charcoal\n'
                ' 9 x Stick\n'
                ' 7 x Iron ore\n'
                ' 64 x Pelt\n'
                ' 1 x Silver ore\n'
                ' 22 x Coal\n'
                ' 2 x Bauxite\n'
                ' 15 x Thread\n'
                ' 1 x Solvent\n'
                'Recipient shall send to guild leader/squire:\n'
                '<code>/g_withdraw 07 11 06 9 02 9 08 7 03 64 10 1 05 22 11 2</code>\n'
                '<code>/g_withdraw 01 15 16 1</code>\n'
                '\n'
                'Missing current guild stock state. Consider forwarding:\n'
                '/g_stock_res'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': True,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'clarity',
        'input':
            'Not enough materials to craft Clarity Robe.\n'
            'Required:\n'
            '15 x Leather\n'
            '9 x Coke\n'
            '12 x Rope\n'
            '7 x Solvent\n'
            '5 x Sapphire\n'
            '1 x Clarity Robe recipe\n'
            '3 x Clarity Robe piece\n'
            '3 x Silver mold',
        'output':
            [
                'Not enough materials to craft Clarity Robe.\n'
                'Required:\n'
                '15 x Leather\n'
                '9 x Coke\n'
                '12 x Rope\n'
                '7 x Solvent\n'
                '5 x Sapphire\n'
                '1 x Clarity Robe recipe\n'
                '3 x Clarity Robe piece\n'
                '3 x Silver mold\n'
                'Recipient shall send to guild leader/squire:\n'
                '<code>/g_withdraw 20 15 23 9 31 12 16 7 15 5 r15 1 k15 3 28 3</code>\n'
                '\n'
                'Missing current guild stock state. Consider forwarding:\n'
                '/g_stock_parts\n'
                '/g_stock_rec\n'
                '/g_stock_res'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': True,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'reinforcement',
        'input':
            'Materials needed for reinforcement:\n'
            '1 x Solvent\n'
            '12 x Pelt\n'
            '2 x Stick\n'
            '6 x Charcoal\n'
            '4 x Bone\n'
            '1 x Thread\n'
            '2 x Powder\n'
            '5 x Coal\n'
            '\n'
            '💧Mana: 33\n'
            '💰Gold: 1\n'
            '/wsr_ResPh_u115_confirm to make an order',
        'output':
            [
                'Materials needed for reinforcement:\n'
                '1 x Solvent\n'
                '12 x Pelt\n'
                '2 x Stick\n'
                '6 x Charcoal\n'
                '4 x Bone\n'
                '1 x Thread\n'
                '2 x Powder\n'
                '5 x Coal\n'
                '\n'
                '💧Mana: 33\n'
                '💰Gold: 1\n'
                '/wsr_ResPh_u115_confirm to make an order\n'
                'Recipient shall send to guild leader/squire:\n'
                '<code>/g_withdraw 16 1 03 12 02 2 06 6 04 4 01 1 07 2 05 5</code>\n'
                '\n'
                'Missing current guild stock state. Consider forwarding:\n'
                '/g_stock_res'],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': True,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'repair',
        'input':
            'Materials needed for repair:\n'
            '18 x Charcoal\n'
            '22 x Powder\n'
            '22 x Iron ore\n'
            '12 x Bone\n'
            '16 x Silver ore\n'
            '19 x Coal\n'
            '18 x Stick\n'
            '80 x Pelt\n'
            '19 x Cloth\n'
            '\n'
            '💧Mana: 226\n'
            '💰Gold: 2\n'
            '/wsr_mz1CQ_u115_confirm to make an order',
        'output':
            [
                'Materials needed for repair:\n'
                '18 x Charcoal\n'
                '22 x Powder\n'
                '22 x Iron ore\n'
                '12 x Bone\n'
                '16 x Silver ore\n'
                '19 x Coal\n'
                '18 x Stick\n'
                '80 x Pelt\n'
                '19 x Cloth\n'
                '\n'
                '💧Mana: 226\n'
                '💰Gold: 2\n'
                '/wsr_mz1CQ_u115_confirm to make an order\n'
                'Recipient shall send to guild leader/squire:\n'
                '<code>/g_withdraw 06 18 07 22 08 22 04 12 10 16 05 19 02 18 03 80</code>\n'
                '<code>/g_withdraw 09 19</code>\n'
                '\n'
                'Missing current guild stock state. Consider forwarding:\n'
                '/g_stock_res'],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': True,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'wrapped_equipment',
        'input':
            '🏷Gloves (1) /bind_a16\n'
            '🏷Crusader Shield (1) /bind_u114\n'
            '🏷Royal Guard Cape (1) /bind_a26',
        'output':
            ['<code>/g_deposit a49</code> Crusader Shield'],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': True,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'misc',
        'input':
            'Azure murky potion (9) /use_tw2\n'
            'Bottle of Greed (13) /use_p09\n'
            'Bottle of Rage (5) /use_p03\n'
            'Crimson murky potion (9) /use_tw3\n'
            'Potion of Greed (13) /use_p08\n'
            'Potion of Nature (2) /use_p11\n'
            'Potion of Rage (6) /use_p02\n'
            'Pouch of gold (10) /use_100\n'
            'Vial of Greed (13) /use_p07\n'
            'Vial of Health (1) /use_p22\n'
            'Vial of Rage (6) /use_p01\n'
            'Vial of Twilight (14) /use_p16\n'
            'Wrapping (10) \n'
            '🍫Chocolate (5) /use_e9\n'
            '📘Scroll of Peace (2) /use_s06\n'
            '📙Scroll of Rage (1) /use_s07',
        'output':
            [
                '<code>/g_deposit p01 6</code> Vial of Rage\n'
                '<code>/g_deposit p02 6</code> Potion of Rage\n'
                '<code>/g_deposit p03 5</code> Bottle of Rage\n'
                '<code>/g_deposit p07 13</code> Vial of Greed\n'
                '<code>/g_deposit p08 13</code> Potion of Greed\n'
                '<code>/g_deposit p09 13</code> Bottle of Greed\n'
                '<code>/g_deposit p11 2</code> Potion of Nature\n'
                '<code>/g_deposit p16 14</code> Vial of Twilight\n'
                '<code>/g_deposit s06 2</code> 📘Scroll of Peace\n'
                '<code>/g_deposit s07</code> 📙Scroll of Rage'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': True,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'consolidate',
        'input':
            '/g_withdraw a09 13 02 10 11 1 05 37 08 4 17 2 01 6 06 21'
            '/g_withdraw 04 39 13 4 07 19 16 2 10 3 03 24 '
            '/g_withdraw 13 3 15 1 08 6 01 5 04 10 03 23 05 19 16 1\n'
            '/g_withdraw 11 2 09 4 02 10 06 8 07 10 \n'
            '/g_withdraw 07 19 08 8 05 19 04 35 02 30 06 14 10 4 13 7',
        'output':
            [
                'Silver helmet x 13\n'
                'Stick x 50\n'
                'Bauxite x 3\n'
                'Coal x 75\n'
                'Iron ore x 18\n'
                'Ruby x 2\n'
                'Thread x 11\n'
                'Charcoal x 43\n'
                'Bone x 84\n'
                'Magic stone x 14\n'
                'Powder x 48\n'
                'Solvent x 3\n'
                'Silver ore x 7\n'
                'Pelt x 47\n'
                'Sapphire x 1\n'
                'Cloth x 4\n'
                '\n'
                '<code>/g_withdraw a09 13 02 50 11 3 05 75 08 18 17 2 01 11 06 43</code>\n'
                '<code>/g_withdraw 04 84 13 14 07 48 16 3 10 7 03 47 15 1 09 4</code>\n'
                '\n'
                'Missing current guild stock state. Consider forwarding:\n'
                '/g_stock_other\n'
                '/g_stock_res'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': True,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'missed',
        'input':
            'Withdrawing:\n'
            'Iron ore x 60\n'
            'Powder x 60\n'
            'Stick x 60\n'
            'Recipient shall send to bot:\n'
            '/g_receive bn48vanqqm6g62k9bsj0',
        'output':
            [
                'Timeout expired. Please resend:\n'
                'Iron ore x 60\n'
                'Powder x 60\n'
                'Stick x 60\n'
                '<code>/g_withdraw 08 60 07 60 02 60</code>\n'
                '\n'
                'Missing current guild stock state. Consider forwarding:\n'
                '/g_stock_res'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': True,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'warehouse_other',
        'input':
            'Guild Warehouse:\n'
            'w97 Nightfall Bow x 2\n'
            'w39c Composite Bow x 1\n'
            'w39b Composite Bow x 1\n'
            'w33 Thundersoul Sword x 2\n'
            'w31b War hammer x 1\n'
            'w28 Champion Sword x 1\n'
            'u188 Thundersoul Sword x 1\n'
            'u187 Ghost Gloves x 1\n'
            'u186 Hunter dagger x 1\n'
            'u184 Hunter Boots x 1\n'
            'u183 ⚡+3 Hunter Armor x 1\n'
            'u180 Clarity Bracers x 1\n'
            'u178 Order Shield x 1\n'
            'u167 ⚡+1 Ghost Armor x 1\n'
            'u166 ⚡+3 Champion Sword x 1\n'
            'u164 Thundersoul Sword x 1\n'
            'u163 Ghost Helmet x 1\n'
            'u162 Clarity Circlet x 1\n'
            'u161 ⚡+3 Divine Circlet x 1\n'
            'u160 \U0001f9df\u200d♂️ Fleder Scimitar x 1\n'
            'u159 \U0001f9df\u200d♂️ Demon Bracers x 1\n'
            'u158 Clarity Shoes x 1\n'
            'u154 ⚡+1 Ghost Boots x 1\n'
            'u148 Hunter dagger x 1\n'
            'u147 Blessed Cloak x 1\n'
            'u146 Hunter Boots x 1\n'
            'u145 Hunter Helmet x 1\n'
            'u130 ⚡+3 Forest Bow x 1\n'
            'u129 ⚡+1 Ghost Boots x 1\n'
            'u126 ⚡+1 Lion Gloves x 1\n'
            'u118 ⚡+3 Mithril shield x 1\n'
            'u102 ⚡+3 Mithril helmet x 1\n'
            'u100 ⚡+3 Mithril axe x 1\n'
            'u091 ⚡+3 Hunter Helmet x 1\n'
            'u061 ⚡+1 Imperial Axe x 1\n'
            'u060 ⚡+3 Hunter Bow x 1\n'
            'u056 ⚡+3 Mithril gauntlets x 1\n'
            'u051 ⚡+1 Lightning Bow x 1\n'
            'u041 ⚡+3 Crusader Gauntlets x 1\n'
            'e123 \U0001f9df\u200d♂️ Demon Robe x 1\n'
            'e106 \U0001f9df\u200d♂️ Witch Circlet x 1\n'
            'a73 Blessed Cloak x 3\n'
            'a67 Divine Robe x 1\n'
            'a64 Demon Circlet x 1\n'
            'a63 Demon Robe x 1\n'
            'a61 Lion Boots x 1\n'
            'a58 Ghost Gloves x 1\n'
            'a57c Ghost Boots x 1\n'
            'a57a Ghost Boots x 1\n'
            'a36c Clarity Robe x 1\n'
            'a35b Hunter Gloves x 1\n'
            'a34a Hunter Boots x 1\n'
            'a33b Hunter Helmet x 1\n'
            'a32b Hunter Armor x 1',

        'output':
            ['other'],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': True,
                'guild_match': False,
                'equipment_match': False
            },
    },
    {   'name': 'inv',
        'input':
            '🎽Equipment +88⚔️+108🛡\n'
            '⚡️+3 Imperial Axe +26⚔️ +25🛡 /off_u119\n'
            'Lion Knife +13⚔️ /off_w46\n'
            'Griffin Helmet +11⚔️ +18🛡 /off_a84\n'
            'Ghost Gloves +8⚔️ +13🛡 /off_u121\n'
            'Griffin Armor +16⚔️ +34🛡 /off_u122\n'
            'Ghost Boots +10⚔️ +15🛡 /off_u120\n'
            '🐉Silver Aries ring /off_s2s\n'
            '🐉Gold Taurus amulet /off_s3g\n'
            'Storm Cloak +4⚔️ +3🛡 /off_u118\n'
            '\n'
            '🎒Bag(2/15):\n'
            'Crusader Shield  +3⚔️ +14🛡 /on_u114\n'
            'Torch  /on_tch',
        'output':
            [
                '/inspect_a84 Griffin Helmet +11⚔️ +18🛡\n'
                '/inspect_s2s 🐉Silver Aries ring\n'
                '/inspect_s3g 🐉Gold Taurus amulet\n'
                '/inspect_tch Torch \n'
                '/inspect_u114 Crusader Shield  +3⚔️ +14🛡\n'
                '/inspect_u118 Storm Cloak +4⚔️ +3🛡\n'
                '/inspect_u119 ⚡️+3 Imperial Axe +26⚔️ +25🛡\n'
                '/inspect_u120 Ghost Boots +10⚔️ +15🛡\n'
                '/inspect_u121 Ghost Gloves +8⚔️ +13🛡\n'
                '/inspect_u122 Griffin Armor +16⚔️ +34🛡\n'
                '/inspect_w46 Lion Knife +13⚔️'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': True
            },
    },
    {   'name': 'inv2',
        'input':
            '🎽Equipment +102⚔️+126🛡\n'
            '⚡️+4 Galadhrim Nightfall Bow +44⚔️ +16🛡 /off_u178\n'
            'Compound arrow (88) /off_518\n'
            '⚡️+1 Griffin Helmet +11⚔️ +20🛡 /off_u230\n'
            '⚡️+4 Ghost Gloves +10⚔️ +21🛡 /off_u220\n'
            '⚡️+4 Ghost Armor +17⚔️ +37🛡 /off_u212\n'
            '⚡️+4 Ghost Boots +10⚔️ +21🛡 /off_u204\n'
            '🐉Silver Aries ring /off_s2s\n'
            '🐉Gold Taurus amulet /off_s3g\n'
            '⚡️+4 Durable Cloak +10⚔️ +11🛡 /off_u242\n'
            '\n'
            '🎒Bag(10/15):\n'
            'Ghost dagger  +13⚔️ +2🛡 /on_u190\n'
            'Short sword  +3⚔️ /on_w02\n'
            'Wooden sword  +1⚔️ /on_w01\n'
            'Gloves  +1🛡 /on_a16\n'
            'Kitchen knife  +1⚔️ /on_w13\n'
            'Silver arrow (153)  /on_512\n'
            'Hat  +1🛡 /on_a06\n'
            'Doomblade Sword  +36⚔️ +1🛡 /on_u138\n'
            'Cloth jacket  +2🛡 /on_a01\n'
            'Wooden arrow (100)  /on_504',
        'output':
            [
                '/inspect_504 Wooden arrow (100) \n'
                '/inspect_512 Silver arrow (153) \n'
                '/inspect_518 Compound arrow (88)\n'
                '/inspect_a01 Cloth jacket  +2🛡\n'
                '/inspect_a06 Hat  +1🛡\n'
                '/inspect_a16 Gloves  +1🛡\n'
                '/inspect_s2s 🐉Silver Aries ring\n'
                '/inspect_s3g 🐉Gold Taurus amulet\n'
                '/inspect_u138 Doomblade Sword  +36⚔️ +1🛡\n'
                '/inspect_u178 ⚡️+4 Galadhrim Nightfall Bow +44⚔️ +16🛡\n'
                '/inspect_u190 Ghost dagger  +13⚔️ +2🛡\n'
                '/inspect_u204 ⚡️+4 Ghost Boots +10⚔️ +21🛡\n'
                '/inspect_u212 ⚡️+4 Ghost Armor +17⚔️ +37🛡\n'
                '/inspect_u220 ⚡️+4 Ghost Gloves +10⚔️ +21🛡\n'
                '/inspect_u230 ⚡️+1 Griffin Helmet +11⚔️ +20🛡\n'
                '/inspect_u242 ⚡️+4 Durable Cloak +10⚔️ +11🛡\n'
                '/inspect_w01 Wooden sword  +1⚔️\n'
                '/inspect_w02 Short sword  +3⚔️\n'
                '/inspect_w13 Kitchen knife  +1⚔️'
            ],
        'matches':
            {
                'storage_match': False,
                'more_match': False,
                'generic_match': False,
                'withdraw_match': False,
                'refund_match': False,
                'consolidate_match': False,
                'rerequest_match': False,
                'warehouse_match': False,
                'guild_match': False,
                'equipment_match': True
            },
    },


]

#print(cases[4]['input'])


class TestBrainsMain(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        class Mock:
            pass

        self.u = Mock()
        self.u.effective_message = Mock()
        self.u.effective_message.forward_from = Mock()
        self.u.effective_message.forward_from.id = 408101137
        self.u.effective_message.forward_date = datetime.now()

        self.c = Mock()
        self.c.user_data = {'save': {'01': '', '02': '', '08': '10'}, 'guild': 'TEST'}


    def test_main(self):
        for case in cases[0:]:
            with self.subTest(name=case['name']):
                self.u.effective_message.text = case['input']
                output, matches = main(self.u, self.c, True)
                #print(case['name'])
                #print(output)
                #print(matches, '\n')
                self.assertEqual( matches, case['matches'] )
                self.assertEqual( output , case['output'] )


if __name__ == '__main__':
    unittest.main()

    #python test.py -b
