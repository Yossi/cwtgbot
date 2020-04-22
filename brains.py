import datetime
import io
import os
import pickle
import re
from collections import defaultdict
from pprint import pprint

import matplotlib.pyplot as plt

from util import is_witching_hour, warehouse_load_saved, get_id_location
from util import id_lookup, name_lookup


def withdraw_parts(matches, guild):
    '''builds withdraw commands.
       expects an iterator of dicts with one key named "number" and the other named "id" or "name"'''
    warehouse = warehouse_load_saved(guild)
    hours = 2.5
    now = datetime.datetime.utcnow()
    command_suffixes = set()

    matches = list(matches)
    for match in matches:
        if match.get('name'):
            match['id'] = name_lookup[match['name'].strip().lower()]['id']

        if match['id'][0].isdigit():
            if int(match['id']) <= 38:
                command_suffixes.add('res')
            else:
                command_suffixes.add('alch')
        elif match['id'][0] in 'sp':
            command_suffixes.add('misc')
        elif match['id'][0] == 'r':
            command_suffixes.add('rec')
        elif match['id'][0] == 'k':
            command_suffixes.add('parts')
        elif match['id'][0] in 'wuea':
            command_suffixes.add('other')

    notice = ''
    guild_stock = {}
    for suffix in command_suffixes:
        suf = warehouse.get(suffix, {})
        if suf:
            age = now - suf['timestamp']
            if age < datetime.timedelta(hours=hours):
                guild_stock.update(suf['data'])
            else:
                guild_stock = {}
                break
        else:
            guild_stock = {}
            break

    if not guild_stock:
        for suffix in sorted(command_suffixes):
            notice += f'\n/g_stock_{suffix}'

    command = ['<code>/g_withdraw']
    have = []
    missing = []
    for d in matches:
        d["number"] = d["number"] if d["number"] else "1"

        if guild_stock:
            diff = int(d["number"]) - guild_stock.get(d['id'], 0)
            if diff > 0:
                if d['id'][0] not in 'rk':
                    exchange = False
                    if id_lookup[d['id']]['exchange']:
                        exchange = True
                        missing.append(f"<code>/wtb_{d['id']}_{diff}</code> {id_lookup[d['id']]['name']}")
                    if id_lookup[d['id']]['craftable']:
                        craftcmd = f"/craft_{d['id']}_{diff} {id_lookup[d['id']]['name']}"
                        if exchange:
                            missing[-1] = missing[-1].split()[0] + f' or {craftcmd}'
                        else:
                            missing.append(craftcmd)
                else:
                    missing.append(f"<code>{d['id']} {diff}</code> {id_lookup[d['id']]['name']}")
                d['number'] = guild_stock.get(d['id'], 0)

        if d['number']:
            have.append(f' {d["id"]} {d["number"]}')

    if have:
        command = ['<code>/g_withdraw']
        for n, id in enumerate(have):
            if not (n + 1) % 9:
                command.append('</code>\n<code>/g_withdraw')
            command.append(id)
        command.append('</code>\n\n')
        command = ''.join(command)
    else:
        command = ''

    if missing:
        missing = '\n'.join([f"Based on data {age.seconds // 60} minutes old, need to get:"] + missing)
    else:
        missing = ''

    if notice:
        notice = 'Missing current guild stock state. Consider forwarding:' + notice

    return command + missing + notice


def main(update, context, testing=False):
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
            name = name.replace('📃', '').replace('🏷', '')
            if name.startswith('/sg_'):
                name = name.partition(' ')[2]
            id = name_lookup.get(name.lower(), {}).get('id')
            if not id and '_' in name:
                id = item.strip().rpartition('_')[2]
            if id not in id_lookup: continue
            if not id_lookup[id]['depositable'] and id[0] not in 'kr': continue
            count_total = int(match[2])
            if id in context.user_data.get('save', {}):
                max_weight = 1000 // id_lookup[id]['weight']
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

    def withdraw():
        '''process missing items messages'''
        matches = re.finditer(r'(?P<number>\d+) x (?P<name>.+)', text)
        if matches:
            ret.append(f'{text}\nRecipient shall send to guild leader/squire:\n{withdraw_parts((match.groupdict() for match in matches), context.user_data.get("guild", ""))}')

    def refund():
        '''process returned /g_deposit message from ourselves'''
        matches = re.finditer(r'\/g_deposit (?P<id>[aestchwpmkr]{0,3}\d+) (?P<number>\d+)?', text)
        if matches:
            ret.append(withdraw_parts((match.groupdict() for match in matches), context.user_data.get('guild', '')))

    def rerequest():
        '''you asked for a withdrawal and then you wandered off to look at squirrels too long? i gotchu fam'''
        matches = list(re.finditer(r'\n(?P<name>[^⚡️+\d\v]+) x (?P<number>\d+)', text))
        response = ['Timeout expired. Please resend:']
        for match in matches:
            response.append(match.string[match.start():match.end()])
        response = "".join(response)
        ret.append(f'{response}\n{withdraw_parts((match.groupdict() for match in matches), context.user_data.get("guild", ""))}')

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
            response.append(f'{id_lookup[id]["name"]} x {number}\n')
            command.append({'id': id, 'number': number})
        ret.append(f'{"".join(response)}\n{withdraw_parts(command, context.user_data.get("guild", ""))}')

    def warehouse_in():
        followup = {
            'res': '/stock',
            'alch': '/alch',
            'rec': '/warehouse',
            'parts': '/w_1',
            'other': '/other'
        }
        guild = context.user_data.get('guild', '')
        if not hasattr(update.effective_message.forward_from, 'id') or update.effective_message.forward_from.id not in [408101137]:  # @chtwrsbot
            ret.append('Must be a forward from @chtwrsbot. Try again.')
        else:
            now = update.effective_message.forward_date
            warehouse = warehouse_load_saved()
            data = {}
            for row in text.split('\n')[1:]:
                s = row.split()
                data[s[0]] = int(s[-1])

            id_sample = list(data.keys())[0]
            if id_sample[0].isdigit():
                if int(id_sample) <= 38:
                    key = 'res'
                else:
                    key = 'alch'
            elif id_sample[0] in 'spfc':
                key = 'misc'
            elif id_sample[0] == 'r':
                key = 'rec'
            elif id_sample[0] == 'k':
                key = 'parts'
            elif id_sample[0] in 'wuea':
                key = 'other'
                data = {}
                for row in text.split('\n')[1:]:
                    s = row.split()
                    supplied_id = s[0]
                    count = s[-1]
                    modifier = ''
                    if s[1].startswith('⚡'):
                        modifier = s.pop(1)
                    name = ' '.join(s[1:-2])
                    base_id = name_lookup.get(name.lower(), {}).get('id', 'zzz')
                    data.setdefault(base_id, []).append( (supplied_id, f'{modifier} {name}', int(count)) )

            if not warehouse.get(guild):
                warehouse[guild] = {}
            if not warehouse[guild].get(key) or now > warehouse[guild][key].get('timestamp', datetime.datetime.min):
                warehouse[guild][key] = {'timestamp': now, 'data': data}
                with open('warehouse.dict', 'wb') as warehouseFile:
                    pickle.dump(warehouse, warehouseFile)
                ret.append(followup.get(key, key))
            else:
                ret.append(f'{key}, but not newer than data on file')
        if not guild:
            ret.append("Your guild affiliation is not on file with this bot. Consider forwarding something that indicates what guild you're in. Eg: /me or /report or /hero")

    def guild(match):
        if not hasattr(update.effective_message.forward_from, 'id') or update.effective_message.forward_from.id not in [408101137]: # @chtwrsbot  (265204902 is cw3)
            ret.append('Must be a forward from @chtwrsbot. Try again.')
        else:
            context.user_data['guild'] = match.groupdict()['guild']
            ret.append(f'Recording you as a member of [{context.user_data["guild"]}] Guild')

    def inspect():
        output = []
        for match in re.finditer(r'(?P<equip_name>.+) \/.{2,3}_(?P<equip_id>.+)', text):
            match = match.groupdict()
            output.append(f'/inspect_{match["equip_id"]} {match["equip_name"]}')
            output.sort()
        ret.append('\n'.join(output))

    storage_match = re.search(r'📦Storage \((\d+)/(\d+)\):', text)
    more_match = '📦Your stock:' in text
    generic_match = re.search(r'(.+)(?<!arrow )\((\d+)\)', text)
    withdraw_match = re.search(r'Not enough materials|Materials needed for|Not enough resources', text)
    refund_match = re.search(r'\/g_deposit [aestchwpmkr]{0,3}\d+ (\d+)?', text)
    consolidate_match = text.startswith('/g_withdraw')
    rerequest_match = '/g_receive' in text
    warehouse_match = 'Guild Warehouse:' in text
    guild_match = re.search(r'(?P<castle_sign>[(🐺🐉🌑🦌🥔🦅🦈)])\[(?P<guild>[A-Z\d]{2,3})\]', text)
    equipment_match = '🎽Equipment' in text

    matched_regexs = {
        'storage_match': bool(storage_match),
        'more_match': bool(more_match),
        'generic_match': bool(generic_match),
        'withdraw_match': bool(withdraw_match),
        'refund_match': bool(refund_match),
        'consolidate_match': bool(consolidate_match),
        'rerequest_match': bool(rerequest_match),
        'warehouse_match': bool(warehouse_match),
        'guild_match': bool(guild_match),
        'equipment_match': bool(equipment_match),
    }
    #print(matched_regexs)

    if storage_match:
        storage(storage_match)
    elif more_match:
        more(text.split('\n'))
    elif generic_match:
        generic(text.split('\n'))
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
    elif guild_match:
        guild(guild_match)
    elif equipment_match:
        inspect()
    else:
        ret.append('')

    if testing:
        return ret, matched_regexs
    return ret


def stock_list(context):
    warehouse = warehouse_load_saved(guild = context.user_data.get('guild', ''))
    hours = 1.5
    responses = []
    now = datetime.datetime.utcnow()
    if (res := warehouse.get('res', {})) and (age := now - res['timestamp']) < datetime.timedelta(hours=hours):
        with open('stockprices.dict', 'rb') as fp:
            prices = pickle.load(fp)

        output = [f'Based on /g_stock_res data {age.seconds // 60} minutes old:\n⚖️']
        for x in range(1, 39):
            if f'{x:02}' in id_lookup:
                res['data'][f'{x:02}'] = res['data'].get(f'{x:02}', 0)

        for id in sorted(res['data'], key=res['data'].get, reverse=True):
            trade = '✅' if id_lookup[id]['exchange'] else '❌'
            price = prices.get(id, '')
            if price: price = f'💰{price}'
            output.append(f'{trade}<code>{id}</code> {id_lookup[id]["name"]} x {res["data"][id]} {price}')
        output.append(f"\nPrices no fresher than {(now - prices['last_update']).seconds // 60} minutes.")

        sort_by_weight = {id: res['data'][id]*id_lookup[id]['weight'] for id in res['data']}
        sort_by_weight = sorted(sort_by_weight, key=sort_by_weight.get, reverse=True)
        x = [
            [res['data'][id] for id in sort_by_weight],
            [res['data'][id]*(id_lookup[id]['weight']-1) if id_lookup[id]['weight'] == 2 else 0 for id in sort_by_weight],
            [res['data'][id]*(id_lookup[id]['weight']-1) if id_lookup[id]['weight'] >= 3 else 0 for id in sort_by_weight]
        ]
        r = range(len(sort_by_weight))
        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.barh(r, x[0])
        plt.barh(r, x[1], left=x[0], color=(1, .6, 0))  # some color between yellow and orange
        plt.barh(r, x[2], left=x[0], color='red')
        plt.yticks(r, [f'{id_lookup[id]["name"].lower()} {id}' for id in sort_by_weight], fontsize='8')
        plt.legend(loc='upper right', labels=['Count', 'Double Weight', 'Triple Weight'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        #buf.name = 'weight.png'
        plt.savefig(buf, format='png')
        buf.seek(0)

        responses.append(buf)
        responses.append('\n'.join(output))
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_res and try again')
    return responses

def alch_list(context):
    warehouse = warehouse_load_saved(guild = context.user_data.get('guild', ''))
    hours = 1.5
    responses = []
    now = datetime.datetime.utcnow()
    if (alch := warehouse.get('alch', {})) and (age := now - alch['timestamp']) < datetime.timedelta(hours=hours):
        output = [f'Based on /g_stock_alch data {age.seconds // 60} minutes old:\n']
        with open('stockprices.dict', 'rb') as fp:
            prices = pickle.load(fp)

        for x in range(39, 70):
            if f'{x:02}' in id_lookup:
                alch['data'][f'{x:02}'] = alch['data'].get(f'{x:02}', 0)

        for id in sorted(alch['data'], key=alch['data'].get, reverse=True):
            price = prices.get(id, '')
            if price: price = f'💰{price}'
            output.append(f'<code>{id}</code> {id_lookup[id]["name"]} x {alch["data"][id]} {price}')

        responses.append('\n'.join(output))
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_alch and try again')
    return responses

def other_list(context):
    warehouse = warehouse_load_saved(guild = context.user_data.get('guild', ''))
    hours = 3
    responses = []
    now = datetime.datetime.utcnow()
    if (other := warehouse.get('other', {})) and (age := now - other['timestamp']) < datetime.timedelta(hours=hours):
        output = [f'Based on /g_stock_other data {age.seconds // 60} minutes old:\n']
        page_counter = 0
        for id, items in sorted(other['data'].items()):
            hold_output = []
            sub_output = []
            item_count = 0
            for item in sorted(items): # TODO: do better sort here
                item_count += item[2]
                sub_output.append('<code>  </code>/g_i_{} {} x {}'.format(*item))
            hold_output.append(f"<code>{id}</code> {id_lookup.get(id, {}).get('name', 'Assorted')} ∑ {item_count} 💰{id_lookup.get(id, {}).get('shopSellPrice', '??')}")
            hold_output.extend(sub_output)
            hold_output.append(' ')
            hold_output = '\n'.join(hold_output)

            page_counter += len(hold_output.encode('utf-8'))
            if page_counter >= 3000: # tg officially supports messages as long as 4096, but the formatting gives up around 3000
                responses.append('\n'.join(output))
                page_counter = 0
                output = []
            output.append(hold_output)

        responses.append('\n'.join(output))
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_other and try again')
    return responses

def warehouse_crafting(context):
    warehouse = warehouse_load_saved(guild = context.user_data.get('guild', ''))
    hours = 2.5
    responses = []
    now = datetime.datetime.utcnow()
    if (rec := warehouse.get('rec', {})) and (parts := warehouse.get('parts', {})) and \
    (age_rec := now - rec['timestamp']) < datetime.timedelta(hours=hours) and \
    (age_parts := now - parts['timestamp']) < datetime.timedelta(hours=hours):
        with open('auctionprices.dict', 'rb') as fp:
            prices = pickle.load(fp)

        older_command = '/g_stock_parts' if age_parts >= age_rec else '/g_stock_rec'
        output = [f'Based on {older_command} data {max(age_rec, age_parts).seconds // 60} minutes old:\n']
        page_counter = 0
        for n in range(1, 125):
            if 62 <= n <= 77:
                continue

            rec_id = f'r{n:02}'
            name = id_lookup[rec_id]['name'].rpartition(" ")[0]
            recipe = name_lookup.get(name.lower(), {}).get('recipe', {})
            parts_needed, part_name = '1000000', 'Part'
            for k in recipe:
                if k.startswith(name.split()[0]) and not k.endswith('Recipe'):
                    parts_needed = int(recipe.get(k))
                    part_name = k.rpartition(' ')[2]
                    part_id = name_lookup.get(k.lower(), {}).get('id')

            count_recipes = rec['data'].get(rec_id, 0)
            count_parts = parts['data'].get(part_id, 0)
            complete_parts_sets = count_parts // parts_needed
            parts_missing_for_next_set = count_parts % parts_needed
            recipes_missing = complete_parts_sets - count_recipes
            things_missing = int(not bool(count_recipes)) + max(parts_needed - count_parts, 0)
            num_craftable = min(count_recipes, complete_parts_sets)
            ready = '✅' if num_craftable else '❌'
            finished_part_id = name_lookup[name.lower()]['id']
            recipe_location = get_id_location(rec_id)
            part_location = get_id_location(part_id)
            recipe_price = str(prices.get(rec_id, ''))
            part_price = str(prices.get(part_id, ''))
            if recipe_price: recipe_price = f'👝{recipe_price}'
            if part_price: part_price = f'👝{part_price}'

            # Getting through this gauntlet without hitting a continue means you get displayed
            if not num_craftable and not context.args:
                continue
            if context.args and context.args[0].lower() != 'all': # if it's 'all' then jump to after the gauntlet
                if context.args[0].isdigit() and 0 < things_missing <= int(context.args[0]):
                    pass
                elif context.args[0].lower().startswith('overstock'):
                    try:
                        multiple = int(context.args[1])
                    except IndexError:
                        multiple = 2
                    if count_parts/parts_needed <= multiple and count_recipes <= multiple:
                        continue
                else:
                    try:
                        regex = re.compile(context.args[0].lower())
                        matches = regex.findall(name.lower())
                        if not matches:
                            continue
                    except re.error:
                        continue

            hold = []
            hold.append(f'{ready} <code>{finished_part_id}</code> {name}')
            if num_craftable:
                hold.append(f'Complete sets: <code>{num_craftable}</code>')
            hold.append(f'{part_name}s per recipe: <code>{parts_needed}</code>')
            hold.append(f'<code>{rec_id}</code> Recipe{"s" if count_recipes != 1 else ""}: <code>{count_recipes}</code> {recipe_price} {recipe_location}')
            hold.append(f'<code>{part_id}</code> {part_name}{"s" if count_parts != 1 else ""}: <code>{count_parts}</code> {part_price} {part_location}')
            hold.append(' ')
            hold = '\n'.join(hold)

            page_counter += len(hold.encode('utf-8'))
            if page_counter >= 2500: # tg officially supports messages as long as 4096, but the formatting gives up around 3000
                responses.append('\n'.join(output))
                page_counter = 0
                output = []
            output.append(hold)

        result = '\n'.join(output)
        if result:
            responses.append(result)
        if result.rstrip().endswith(':'):
            responses.append('No matches in stock')
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_parts and /g_stock_rec and try again')
    return responses

def withdraw_craft(context):
    response = ["Can't craft this"]
    if context.args:
        id = context.args[0]
        info = id_lookup.get(id, {})

        count = 1
        if len(context.args) > 1:
            count = int(context.args[1])

        if info.get('craftable', False):
            recipe = [{'name': name, 'number': int(amount) * count} for name, amount in info['recipe'].items()]
            response = [
                f'{info["name"]} x {count}\n'
                f'Mana requirement: {info.get("craftMana", "unknown")} x {count} = {info.get("craftMana", 0) * count} mana total\n'
                f"{withdraw_parts(recipe, context.user_data.get('guild', ''))}"
            ]

    return response

def deals_report(context):
    output = []
    now = datetime.datetime.utcnow()
    with open('stockprices.dict', 'rb') as fp:
        prices = pickle.load(fp)

    args = []
    if context.args:
        args = context.args

    def recipe_price(recipe):
        acumulator = 0
        for name, count in recipe.items():
            data = name_lookup[name.lower()]
            id = data['id']
            craft_price = exchange_price = 1000

            if data.get('craftable'):
                craft_price = recipe_price(data['recipe'])
            if data.get('exchange'):
                exchange_price = prices.get(id, '')

            price = min(craft_price, exchange_price)
            acumulator += int(count) * price
        return acumulator

    for name, data in name_lookup.items():
        if data.get('exchange') and data.get('craftable'):
            id = data['id']
            if args and id not in args:
                continue
            buy_price = prices.get(id, '')
            make_price = recipe_price(data['recipe'])

            out_str = f"<code>{id}</code> {data['name']} /craft_{id}\n {'✅' if buy_price > make_price else '❌'}Make: {make_price}💰, {'❌' if buy_price > make_price else '✅'}Buy: {buy_price}💰"
            output.append(out_str) # \"{data['recipe']}\"
    output.sort()
    output.append(f"\nPrices no fresher than {(now - prices['last_update']).seconds // 60} minutes.")
    return '\n'.join(output)


if __name__ == '__main__':
    class Mock:
        pass
    c = Mock()
    c.user_data = {'save': {'01': '', '02': '', '08': '10'}, 'guild': 'USA'}
    c.args = ['all']

    pprint(warehouse_crafting(c))
