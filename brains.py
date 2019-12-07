import re
import os
import pickle
import datetime
from pprint import pprint
from pathlib import Path
from collections import defaultdict

from util import scrape_data, is_witching_hour, emoji_number


if not Path("data.dict").is_file():
    with open('data.dict', 'wb') as fp:
        scrape_data(fp)
with open('data.dict', 'rb') as fp:
    data = pickle.load(fp)
    id_to_weight = dict(data.values())
    id_to_name = {v[0]: k for k, v in data.items()}
    name_to_id = {v: k for k, v in id_to_name.items()}


def main(update, context):
    '''returns a list of strings that are then each sent as a separate message'''
    text = update.effective_message.text
    ret = []

    def storage(m):
        '''handles /stock output'''
        percent_full = 100*int(m[1])/int(m[2])
        ret.append(f'{percent_full}% full')
        items = text.split('\n')[1:]
        if items[0].startswith('Use /sg_{code} to trade some amount of resource for '):
            items = (''.join(item.partition(' ')[::-1]) for item in items[2:])
        generic(items)

    def more(items):
        '''handles /more output'''
        def tidy(items):
            for item in items[1:]:
                slash, _ = item.partition(' ')[::2]
                name, count = _.partition(' x ')[::2]
                yield f'{name} ({count}) {slash}'
        generic(tidy(items))

    def generic(items):
        '''does most of the work sorting a list of items into /wts and /g_deposit buckets.
           expects an iterator of strings in the form ['<Item Name> (<Item Count>)']'''
        sales = []
        deposits = []
        for item in items:
            match = re.search(r'(.+)\((\d+)\)', item)
            if not match: continue
            name = match[1].strip()
            if 'murky' in name: continue
            name = name.replace('📃', '')
            if name.startswith('/sg_'):
                name = name.partition(' ')[2]
            id = name_to_id.get(name.lower())
            if not id and '_' in name:
                id = item.strip().rpartition('_')[2]
            if id not in id_to_name: continue
            if id in ('100', '501', 'a16', 'a26', 'tch'): continue # partial list of undepositable ids
            count_total = int(match[2])
            if id in context.user_data.get('save', {}):
                max_weight = 1000 // id_to_weight[id]
                count_keep = context.user_data['save'][id]
                if not count_keep:
                    count_keep = count_total
                count_keep = min(int(count_keep), count_total)
                count_deposit = count_total - count_keep
                while count_keep > max_weight:
                    sales.append(f'/wts_{id}_{max_weight}_1000')
                    count_keep = count_keep - max_weight
                sales.append(f'/wts_{id}_{count_keep}_1000 {name}')
                if count_deposit:
                    deposits.append(f'<code>/g_deposit {id}{" "+str(count_deposit) if count_deposit != 1 else ""}</code> {name}')
            elif id in context.user_data.get('ignore', {}):
                count_keep = context.user_data['ignore'][id]
                if not count_keep:
                    count_keep = count_total
                count_keep = min(int(count_keep), count_total)
                count_deposit = count_total - count_keep
                if count_deposit:
                    deposits.append(f'<code>/g_deposit {id}{" "+str(count_deposit) if count_deposit != 1 else ""}</code> {name}')
            else:
                deposits.append(f'<code>/g_deposit {id}{" "+str(count_total) if count_total != 1 else ""}</code> {name}')

        if sales:
            if len(sales) == 1:
                sales = sales[0].split()[0]
            else:
                sales = '\n'.join(sorted(sales))
            if is_witching_hour():
                matches = re.finditer(r'\/wts_(?P<id>\d+)_(?P<number>\d+)_1000 (?P<name>.+)', sales)
                fire_sale = ['Market is closed so you get deposit commands.\nForward this message back to the bot after battle to get the withdraw commands for a refund.\n']
                for match in matches:
                    d = match.groupdict()
                    fire_sale.append(f'<code>/g_deposit {d["id"]}{" "+d["number"] if d["number"] != "1" else ""}</code> {d["name"]}')
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
        pprint(context.user_data)

    def withdraw():
        '''process missing items messages'''
        matches = re.finditer(r'(?P<number>\d+) x (?P<name>.+)', text)
        if matches:
            ret.append(f'{text}\n{withdraw_parts((match.groupdict() for match in matches))}')

    def refund():
        '''process returned /g_deposit message from ourselves'''
        matches = re.finditer(r'\/g_deposit (?P<id>[aestchwpmkr]{0,3}\d+) (?P<number>\d+)?', text)
        if matches:
            ret.append(withdraw_parts((match.groupdict() for match in matches)))

    def rerequest():
        '''you asked for a withdrawal and then you wandered off to look at squirrels too long? i gotchu fam'''
        matches = list(re.finditer(r'(?P<name>.+) x (?P<number>\d+)', text))
        response = ['Timeout expired. Please resend:']
        for match in matches:
            response.append(match.string[match.start():match.end()])
        response = "\n".join(response)
        ret.append(f'{response}\n{withdraw_parts((match.groupdict() for match in matches))}')

    def consolidate():
        '''consolidate /g_withdraw commands'''
        response = []
        command = []
        count = defaultdict(int)
        matches = re.finditer(r'(?P<id>[aestchwpmkr]{0,3}\d+)\s+(?P<number>\d+)', text)
        for match in matches:
            d = match.groupdict()
            count[d['id']] += int(d['number'])
        for id, number in count.items():
            response.append(f'{id_to_name[id].capitalize()} x {number}\n')
            command.append({'id': id, 'number': number})
        ret.append(f'{"".join(response)}\n{withdraw_parts(command)}')

    def withdraw_parts(matches):
        '''builds withdraw commands.
           expects an iterator of dicts with one key named "number" and the other named "id" or "name"'''
        command = ['<code>/g_withdraw']
        for n, d in enumerate(matches):
            if not (n + 1) % 9:
                command.append('</code>\n<code>/g_withdraw')
            if d.get('name'):
                d['id'] = name_to_id[d['name'].lower()]
            command.append(f' {d["id"]} {d["number"] if d["number"] else "1"}')
        command.append('</code>')
        return ''.join(command)

    def warehouse_load_saved(ignore_exceptions):
        try:
            with open('warehouse.dict', 'rb') as warehouseFile:
                return pickle.load(warehouseFile)
        except IOError:
            if not ignore_exceptions:
                raise
            else:
                return {} # Ignore if warehouse.dict doesn't exist or can't be opened.

    def warehouse_in():
        if not hasattr(update.message.forward_from, 'id') or update.message.forward_from.id not in [408101137]: # @chtwrsbot
            ret.append('Must be a forward from @chtwrsbot. Try again.')
        else:
            now = update.message.forward_date
            warehouse = warehouse_load_saved(True)
            data = {}
            for row in text.split('\n')[1:]:
                s = row.split()
                data[s[0]] = int(s[-1])

            id_sample = list(data.keys())[0]
            if id_sample[0].isdigit():
                if int(id_sample) <= 36:
                    key = 'res'
                else:
                    key = 'alch'
            elif id_sample[0] in 'sp':
                key = 'misc'
            elif id_sample[0] == 'r':
                key = 'rec'
            elif id_sample[0] == 'k':
                key = 'parts'
            elif id_sample[0] in 'wuea':
                key = 'other'

            if not warehouse.get(key) or now > warehouse[key].get('timestamp', datetime.datetime.min):
                warehouse[key] = {'timestamp': now, 'data': data}
                with open('warehouse.dict', 'wb') as warehouseFile
                    pickle.dump(warehouse, warehouseFile)
                ret.append(key)
            else:
                ret.append(f'{key}, but not newer than data on file')

    storage_match = re.search(r'📦Storage \((\d+)/(\d+)\):', text)
    more_match = re.search(r'📦Your stock:', text)
    generic_match = re.search(r'(.+)\((\d+)\)', text)
    exchange_match = re.search(r'Your deals \((\d+)/(\d+)\):', text)
    withdraw_match = re.search(r'Not enough materials|Materials needed for', text)
    refund_match = re.search(r'\/g_deposit [aestchwpmkr]{0,3}\d+ (\d+)?', text)
    consolidate_match = re.search(r'^\/g_withdraw', text)
    rerequest_match = re.search(r'\/g_receive', text)
    warehouse_match = re.search(r'Guild Warehouse:', text)

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
    elif consolidate_match:
        consolidate()
    elif rerequest_match:
        rerequest()
    elif warehouse_match:
        warehouse_in()
    else:
        ret.append('Unclear what to do with this.')

    return ret

def warehouse_crafting(context):
    warehouse = warehouse_load_saved(True)
    hours = 2
    responses = []
    now = datetime.datetime.utcnow()
    if (rec := warehouse.get('rec', {})) and (parts := warehouse.get('parts', {})) and \
    (now - rec['timestamp']) < datetime.timedelta(hours=hours) and (now - parts['timestamp']) < datetime.timedelta(hours=hours):
        output = []
        page_counter = 0
        for n in range(1,103):
            if 1 <= n <= 18 or 59 <= n <= 61:
                parts_needed = 3
            elif 100 <= n <= 102:
                parts_needed = 4
            elif 19 <= n <= 58 or n in (91, 96, 97):
                parts_needed = 5
            elif 78 <= n <= 90 or 92 <= n <= 95 or n in (98, 99):
                parts_needed = 6
            elif 62 <= n <= 77:
                parts_needed = 0

            id = f'{n:02}'
            count_recipies = rec['data'].get(f'r{id}', 0)
            count_parts = parts['data'].get(f'k{id}', 0)
            if count_recipies or count_parts:
                complete_parts_sets = count_parts // parts_needed
                parts_missing_for_next_set = count_parts % parts_needed
                recipies_missing = complete_parts_sets - count_recipies
                things_missing = int(not bool(count_recipies)) + max(parts_needed - count_parts, 0)
                num_craftable = min(count_recipies, complete_parts_sets)
                ready = '✅' if num_craftable else '❌'
                name = id_to_name["r"+id].rpartition(" ")[0]
                finished_part_id = name_to_id[name]
                part_name = id_to_name["k"+id].rpartition(" ")[2].title()

                if not num_craftable and not context.args:
                    continue
                if context.args and context.args[0].lower() != 'all':
                    if context.args[0].lower() in name:
                        pass
                    elif context.args[0].isdigit() and 0 < things_missing <= int(context.args[0]):
                        pass
                    else:
                        continue

                output.append(f'{ready} {id} {name.title()} <code>{finished_part_id}</code>')
                if num_craftable:
                    output.append(f'<code> {num_craftable}</code> Can be made')
                output.append(f'<code>{parts_needed} {part_name}s per recipe</code>')
                output.append(f'<code>  {count_recipies} Recipe{"s" if count_recipies != 1 else ""}</code>')
                output.append(f'<code>  {count_parts} {part_name}{"s" if count_parts != 1 else ""}</code>')
                output.append(' ')

                page_counter += 1
                if page_counter >= 20:
                    responses.append('\n'.join(output))
                    page_counter = 0
                    output = []

        if len((result := '\n'.join(output))):
            responses.append(result)
        else:
            responses.append('No matches in stock')
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_parts and /g_stock_rec and try again')
    return responses


if __name__ == '__main__':
    d = {
    'sg_stock':
        '📦Storage (2181/4000):\n'
        'Use /sg_{code} to trade some amount of resource for 1💰/pcs\n'
        '\n'
        '/sg_05 Coal (1)\n'
        '/sg_03 Pelt (2)\n'
        '/sg_02 Stick (2)\n'
        '/sg_01 Thread (1)',

    'stock':
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

    'more':
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

    'crafting':
        'Royal Boots part (1)\n'
        'Royal Gauntlets part (1)\n'
        '📃Royal Gauntlets recipe (1) /view_r41\n'
        'Royal Helmet fragment (1)',

    'missing':
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

    'clarity':
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

    'reinforcement':
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

    'repair':
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

    'misc':
        'Azure murky potion (4) /use_tw2\n'
        'Bottle of Peace (1) /use_p06\n'
        'Bottle of Rage (5) /use_p03\n'
        'Crimson murky potion (4) /use_tw3\n'
        'Potion of Greed (4) /use_p08\n'
        'Potion of Nature (2) /use_p11\n'
        'Potion of Rage (6) /use_p02\n'
        'Pouch of gold (10) /use_100\n'
        'Vial of Rage (6) /use_p01\n'
        'Vial of Twilight (4) /use_p16\n'
        'Wrapping (10)\n'
        '📙Scroll of Peace (2) /use_s08\n'
        '📙Scroll of Rage (1) /use_s07',

    'equipment':
        '🏷Gloves (1) /bind_a16\n'
        '🏷Royal Guard Cape (1) /bind_a26',

    'consolidate':
        '/g_withdraw a09 13 02 10 11 1 05 37 08 4 17 2 01 6 06 21'
        '/g_withdraw 04 39 13 4 07 19 16 2 10 3 03 24 '
        '/g_withdraw 13 3 15 1 08 6 01 5 04 10 03 23 05 19 16 1\n'
        '/g_withdraw 11 2 09 4 02 10 06 8 07 10 \n'
        '/g_withdraw 07 19 08 8 05 19 04 35 02 30 06 14 10 4 13 7',

    'missed':
        'Withdrawing:\n'
        'Iron ore x 60\n'
        'Powder x 60\n'
        'Stick x 60\n'
        'Recipient shall send to bot:\n'
        '/g_receive bn48vanqqm6g62k9bsj0',

    'warehouse':
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
    }

    name = 'warehouse'
    d = {name: d[name]}
    for name, l in d.items():
        print(name)
        #pprint(l)
        pprint(main(l, {'save': {'01': '', '02': '', '08': ''}}))






    #  'exchange': 'Here you can buy and sell some items.\n'
    #              'To find a tradable item just type:\n'
    #              '/t [item name]\n'
    #              'Example:\n'
    #              '/t coal\n'
    #              '\n'
    #              'Your deals (9/11):\n'
    #              'Thread\n'
    #              '1000 x 1000💰 [Selling] /rm_blatt6nqqm6jf52f7d40\n'
    #              'Thread\n'
    #              '1000 x 9💰 [Selling] /rm_blattknqqm6jf52f7ep0\n'
    #              'String\n'
    #              '2 x 2💰 [Selling] /rm_blr9ujvqqm6kjt662q30\n'
    #              'Bone\n'
    #              '45 x 9💰 [Selling] /rm_blrd4qfqqm6kjt667b40\n'
    #              'Cloth\n'
    #              '127 x 9💰 [Selling] /rm_blrd4sfqqm6kjt667beg\n'
    #              'Leather\n'
    #              '109 x 9💰 [Selling] /rm_blrd52vqqm6kjt667c0g\n'
    #              'Pelt\n'
    #              '226 x 9💰 [Selling] /rm_blrd55fqqm6kjt667c90\n'
    #              'Powder\n'
    #              '225 x 9💰 [Selling] /rm_blrd577qqm6kjt667ceg\n'
    #              'Thread\n'
    #              '448 x 9💰 [Selling] /rm_blrd58fqqm6kjt667chg\n'
    #              '\n'
    #              'Your last 10 comitted trades: /trades',

