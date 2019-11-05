import re
import os
import pickle
from pprint import pprint
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from util import scrape_data, is_witching_hour

if not Path("data.dict").is_file():
    with open('data.dict', 'wb') as fp:
        scrape_data(fp)
with open('data.dict', 'rb') as fp:
    name_to_id = pickle.load(fp)
    id_to_name = {v: k for k, v in name_to_id.items()}


def main(text, user_data):
    '''deals with all forwarded messages'''
    ret = []

    def storage(m):
        '''handles /stock output'''
        percent_full = 100*int(m[1])/int(m[2])
        ret.append(f'{percent_full}% full')
        items = text.split('\n')[1:]
        if items[0].startswith('Use /sg_{code} to trade some amount of resource for '):
            items = items[2:]
        generic(items)

    def more(items):
        '''handles /more output'''
        generic(('%s (%s)' % item.partition(' ')[2].partition(' x ')[::2] for item in items[1:]))

    def generic(items):
        '''does most of the work sorting a list of items into /wts and /g_deposit buckets'''
        sales = []
        deposits = []
        for item in items:
            match = re.search(r'(.+)\((\d+)\)', item)
            if not match: continue
            name = match[1].strip()
            if name.startswith('/sg_'):
                name = name.partition(' ')[2]
            id = name_to_id[name.lower()]
            count_total = int(match[2])
            if id in user_data.get('save', {}):
                count_keep = user_data['save'][id]
                if not count_keep:
                    count_keep = count_total
                count_keep = min(int(count_keep), count_total)
                count_deposit = count_total - count_keep
                while count_keep > 1000:
                    sales.append(f'/wts_{id}_1000_1000')
                    count_keep = count_keep - 1000
                sales.append(f'/wts_{id}_{count_keep}_1000 {name}')
                if count_deposit:
                    deposits.append(f'<code>/g_deposit {id}{" "+str(count_deposit) if count_deposit != 1 else ""}</code> {name}')
            elif id in user_data.get('ignore', {}):
                count_keep = user_data['ignore'][id]
                if not count_keep:
                    count_keep = count_total
                count_keep = min(int(count_keep), count_total)
                count_deposit = count_total - count_keep
                if count_deposit:
                    deposits.append(f'<code>/g_deposit {id}{" "+str(count_deposit) if count_deposit != 1 else ""}</code> {name}')
            else:
                deposits.append(f'<code>/g_deposit {id}{" "+str(count_total) if count_total != 1 else ""}</code> {name}')

        if sales:
            sales = '\n'.join(sorted(sales))
            if is_witching_hour():
                matches = re.finditer(r'\/wts_(?P<id>\d+)_(?P<number>\d+)_1000 (?P<name>.+)', sales)
                fire_sale = []
                for match in matches:
                    d = match.groupdict()
                    fire_sale.append(f'<code>/g_deposit {d["id"]}{" "+d["number"] if d["number"] != "1" else ""}</code> {d["name"]}*')
                sales = '\n'.join(sorted(fire_sale))
            ret.append(sales)

        if deposits:
            ret.append('\n'.join(sorted(deposits)))

    def exchange(m):
        '''unfinished business. non functional at this time'''
        res = {}
        current_deals = int(m[1])
        total_slots = int(m[2])
        active_slots = total_slots

        matches = re.finditer(r'(?P<name>\w+)\n(?P<number>\d+) x (?P<price>\d+)💰 \[Selling\] (?P<command>\/rm_\w+)', text)
        for match in matches:
            d = match.groupdict()
            if d['price'] == '1000' and d['number'] != '1000':
                res[name_to_id[match['name'].lower()]] = d
            else:
                active_slots -= 1
        pprint(res)
        pprint(user_data)

    def withdraw():
        '''process missing items messages'''
        command = [f'{text}\n<code>']
        matches = re.finditer(r'(?P<number>\d+) x (?P<name>.+)', text)
        if matches:
            withdraw_parts(command, matches)

    def refund():
        '''process returned /g_deposit message from ourselves'''
        command = ['<code>']
        matches = re.finditer(r'\/g_deposit (?P<id>[aestchwpmkr]{0,3}\d+) (?P<number>\d+)?', text)
        if matches:
            withdraw_parts(command, matches)

    def withdraw_parts(command, matches):
        '''builds withdraw commands'''
        command.append('/g_withdraw')
        for n, match in enumerate(matches):
            if not (n + 1) % 9:
                command.append('</code>\n<code>/g_withdraw')
            d = match.groupdict()
            if d.get('name'):
                d['id'] = name_to_id[d['name'].lower()]
            command.append(f' {d["id"]} {d["number"] if d["number"] else "1"}')
        command.append('</code>')
        ret.append(''.join(command))


    storage_match = re.search(r'📦Storage \((\d+)/(\d+)\):', text)
    more_match = re.search(r'📦Your stock:', text)
    generic_match = re.search(r'(.+)\((\d+)\)', text)
    exchange_match = re.search(r'Your deals \((\d+)/(\d+)\):', text)
    withdraw_match = re.search(r'Not enough materials|Materials needed for repair', text)
    refund_match = re.search(r'\/g_deposit [aestchwpmkr]{0,3}\d+ (\d+)?', text)

    if storage_match:
        storage(storage_match)
    elif more_match:
        more(text.split('\n'))
    elif generic_match:
        generic(text.split('\n'))
    elif exchange_match:
        exchange(exchange_match)
    elif withdraw_match:
        withdraw()
    elif refund_match:
        refund()
    else:
        ret.append('What should I do with this?')

    return ret



if __name__ == '__main__':
    d = {
 'crafting': 'Royal Boots part (1)\n'
             'Royal Gauntlets part (1)\n'
             '📃Royal Gauntlets recipe (1) /view_r41\n'
             'Royal Helmet fragment (1)',

 'exchange': 'Here you can buy and sell some items.\n'
             'To find a tradable item just type:\n'
             '/t [item name]\n'
             'Example:\n'
             '/t coal\n'
             '\n'
             'Your deals (9/11):\n'
             'Thread\n'
             '1000 x 1000💰 [Selling] /rm_blatt6nqqm6jf52f7d40\n'
             'Thread\n'
             '1000 x 9💰 [Selling] /rm_blattknqqm6jf52f7ep0\n'
             'String\n'
             '2 x 2💰 [Selling] /rm_blr9ujvqqm6kjt662q30\n'
             'Bone\n'
             '45 x 9💰 [Selling] /rm_blrd4qfqqm6kjt667b40\n'
             'Cloth\n'
             '127 x 9💰 [Selling] /rm_blrd4sfqqm6kjt667beg\n'
             'Leather\n'
             '109 x 9💰 [Selling] /rm_blrd52vqqm6kjt667c0g\n'
             'Pelt\n'
             '226 x 9💰 [Selling] /rm_blrd55fqqm6kjt667c90\n'
             'Powder\n'
             '225 x 9💰 [Selling] /rm_blrd577qqm6kjt667ceg\n'
             'Thread\n'
             '448 x 9💰 [Selling] /rm_blrd58fqqm6kjt667chg\n'
             '\n'
             'Your last 10 comitted trades: /trades',

 'missing': 'Not enough materials. Missing:\n'
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

 'sg_stock': '📦Storage (2181/4000):\n'
             'Use /sg_{code} to trade some amount of resource for 1💰/pcs\n'
             '\n'
             '/sg_05 Coal (1)\n'
             '/sg_03 Pelt (2)\n'
             '/sg_02 Stick (2)\n'
             '/sg_01 Thread (1)',

 'stock': '📦Storage (1633/4000):\n'
          'Bauxite (4)\n'
          'Bone powder (9)\n'
          'Bone (42)\n'
          'Charcoal (19)\n'
          'Cloth (127)\n'
          'Coal (4)\n'
          'Coke (10)\n'
          'Crafted leather (1)\n'
          'Iron ore (3)\n'
          'Leather (109)\n'
          'Magic stone (2)\n'
          'Metal plate (2)\n'
          'Pelt (226)\n'
          'Powder (223)\n'
          'Ruby (1)\n'
          'Silver ore (13)\n'
          'Solvent (5)\n'
          'Thread (447)',

'more': '📦Your stock:\n'
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
}


    l= d['missing']
    #pprint(l)
    
    pprint(main(l,{}))