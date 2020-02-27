import unittest
from brains import main


cases = [
    {   'name': '',
        'input':
            '',
        'output':
            ['Unclear what to do with this.'],
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


]


class TestBrainsMain(unittest.TestCase):

    def setUp(self):
        class Mock:
            pass

        self.u = Mock()
        self.u.effective_message = Mock()
        self.c = Mock()
        self.c.user_data = {'save': {'01': '', '02': '', '08': '10'}}

    def test_main(self):
        for case in cases[-1:]:
            with self.subTest(name=case['name']):
                self.u.effective_message.text = case['input']
                output, matches = main(self.u, self.c, True)
                print(case['name'])
                print(output)
                print(matches, '\n')
                self.assertEqual( matches, case['matches'] )
                self.assertEqual( output , case['output'] )


if __name__ == '__main__':
    unittest.main()

    #python test.py -b
