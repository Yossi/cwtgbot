import datetime
import io
import os
import pickle
import re
from collections import defaultdict
from pprint import pprint
from rich import print

import matplotlib.pyplot as plt

from util import is_witching_hour, warehouse_load_saved, get_id_location
from util import id_lookup, name_lookup







def stock_list(context):
    warehouse = warehouse_load_saved(guild=context.user_data.get('guild', ''))
    hours = 1.5
    responses = []
    now = datetime.datetime.utcnow()
    if (res := warehouse.get('res', {})) and (age := now - res['timestamp']) < datetime.timedelta(hours=hours):
        try:
            with open('stockprices.dict', 'rb') as fp:
                prices = pickle.load(fp)
        except FileNotFoundError:
            prices = {}

        output = [f'Based on /g_stock_res data {age.seconds // 60} minutes old:\n⚖️']
        for x in range(1, 39):
            if f'{x:02}' in id_lookup:
                res['data'][f'{x:02}'] = res['data'].get(f'{x:02}', 0)

        for id in sorted(res['data'], key=res['data'].get, reverse=True):
            trade = '✅' if id_lookup[id]['exchange'] else '❌'
            price = prices.get(id, '')
            if price:
                price = f'💰{price}'
            output.append(f'{trade}<code>{id}</code> {id_lookup[id]["name"]} x {res["data"][id]} {price}')
        if prices:
            output.append(f"\nPrices no fresher than {(now - prices['last_update']).seconds // 60} minutes.")

        sort_by_weight = {id: res['data'][id] * id_lookup[id]['weight'] for id in res['data']}
        sort_by_weight = sorted(sort_by_weight, key=sort_by_weight.get, reverse=True)
        x = [
            [res['data'][id] for id in sort_by_weight],
            [res['data'][id] * (id_lookup[id]['weight'] - 1) if id_lookup[id]['weight'] == 2 else 0 for id in sort_by_weight],
            [res['data'][id] * (id_lookup[id]['weight'] - 1) if id_lookup[id]['weight'] >= 3 else 0 for id in sort_by_weight]
        ]
        r = range(len(sort_by_weight))
        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.figure(figsize=(6.4, 1.5+(len(sort_by_weight)*0.15)))
        plt.barh(r, x[0])
        plt.barh(r, x[1], left=x[0], color=(1, .6, 0))  # some color between yellow and orange
        plt.barh(r, x[2], left=x[0], color='red')
        plt.yticks(r, [f'{id_lookup[id]["name"].lower()} {id}' for id in sort_by_weight], fontsize='8')
        plt.legend(loc='upper right', labels=['Stock Count', 'Double Weight', 'Triple Weight'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        responses.append(buf)

        responses.append('\n'.join(output))
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_res and try again')
    return responses


def alch_list(context):
    warehouse = warehouse_load_saved(guild=context.user_data.get('guild', ''))
    hours = 1.5
    responses = []
    now = datetime.datetime.utcnow()
    if (alch := warehouse.get('alch', {})) and (age := now - alch['timestamp']) < datetime.timedelta(hours=hours):
        try:
            with open('stockprices.dict', 'rb') as fp:
                prices = pickle.load(fp)
        except FileNotFoundError:
            prices = {}

        output = [f'Based on /g_stock_alch data {age.seconds // 60} minutes old:\n']
        for x in range(39, 70):
            if f'{x:02}' in id_lookup:
                alch['data'][f'{x:02}'] = alch['data'].get(f'{x:02}', 0)

        for id in sorted(alch['data'], key=alch['data'].get, reverse=True):
            price = prices.get(id, '')
            if price:
                price = f'💰{price}'
            output.append(f'<code>{id}</code> {id_lookup[id]["name"]} x {alch["data"][id]} {price}')
        if prices:
            output.append(f"\nPrices no fresher than {(now - prices['last_update']).seconds // 60} minutes.")

        sort_by_count = sorted(alch['data'], key=alch['data'].get, reverse=True)
        x = [alch['data'][id] for id in sort_by_count]
        y = [f'{id_lookup[id]["name"].lower()} {id}' for id in sort_by_count]
        r = range(len(x))
        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.figure(figsize=(6.4, 1.5+(len(sort_by_count)*0.15)))
        plt.barh(r, x)
        plt.yticks(r, y, fontsize='8')
        plt.legend(loc='upper right', labels=['Alch Count'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        responses.append(buf)

        responses.append('\n'.join(output))
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_alch and try again')
    return responses


def other_list(context):
    warehouse = warehouse_load_saved(guild=context.user_data.get('guild', ''))
    hours = 3
    responses = []
    now = datetime.datetime.utcnow()
    if (other := warehouse.get('other', {})) and (age := now - other['timestamp']) < datetime.timedelta(hours=hours):
        output = [f'Based on /g_stock_other data {age.seconds // 60} minutes old:\n']
        page_counter = 0
        value_to_weight = {id: id_lookup.get(id, {}).get('shopSellPrice', 0)/id_lookup.get(id, {}).get('weight', 1) for id in other['data']}
        for id in sorted(value_to_weight, key=value_to_weight.get, reverse=True):
            items = other['data'][id]
            hold_output = []
            sub_output = []
            item_count = 0
            for item in sorted(items):
                item_id, name, count = item
                if item_id.startswith('u') and (match := re.search(r'[ˢᵃᵇᶜᵈᵉ]+', item_id)):
                    split = match.span()[0]
                    item_id = item_id[:split] + '​' + item_id[split:]  # zero width space
                item_count += count
                sub_output.append(f'<code>  </code>/g_i_{item_id} {name} x {count}')
            hold_output.append(f"<code>{id}</code> {id_lookup.get(id, {}).get('name', 'Assorted')} ∑ {item_count} 💰{id_lookup.get(id, {}).get('shopSellPrice', '??')}")
            hold_output.append(f"💰/⚖️ {value_to_weight[id]:.2f}")
            hold_output.extend(sub_output)
            hold_output.append(' ')
            hold_output = '\n'.join(hold_output)

            page_counter += len(hold_output.encode('utf-8'))
            if page_counter >= 3000:  # tg officially supports messages as long as 4096, but the formatting gives up around 3000
                responses.append('\n'.join(output))
                page_counter = 0
                output = []
            output.append(hold_output)

        count_and_weight = {id: sum(list(zip(*other['data'][id]))[2]) * id_lookup.get(id, {}).get('weight', 0) for id in other['data']}
        sort_by_weight = sorted(count_and_weight, key=count_and_weight.get, reverse=True)
        x = [count_and_weight[id] for id in sort_by_weight]
        y = [f"{id_lookup.get(id, {'name': 'assorted'})['name'].lower()} {id}" for id in sort_by_weight]
        r = range(len(x))
        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.figure(figsize=(6.4, 1.5+(len(sort_by_weight)*0.15)))
        plt.barh(r, x)
        plt.yticks(r, y, fontsize='8')
        plt.legend(loc='upper right', labels=['Other by Weight'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        responses.append('\n'.join(output))

        responses.append(buf)
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_other and try again')
    return responses


def misc_list(context):
    warehouse = warehouse_load_saved(guild=context.user_data.get('guild', ''))
    hours = 5
    responses = []
    now = datetime.datetime.utcnow()
    if (misc := warehouse.get('misc', {})) and (age := now - misc['timestamp']) < datetime.timedelta(hours=hours):
        try:
            with open('auctionprices.dict', 'rb') as ap, open('stockprices.dict', 'rb') as sp:
                auction_prices = pickle.load(ap)
                stock_prices = pickle.load(sp)
                price_age = min(auction_prices['last_update'], stock_prices['last_update'])
                prices = {**auction_prices, **stock_prices}
                prices['last_update'] = price_age
        except FileNotFoundError:
            prices = {}

        output = [f'Based on /g_stock_misc data {age.seconds // 60} minutes old:\n']
        for id in sorted(misc['data'], key=misc['data'].get, reverse=True):
            price = prices.get(id, '')
            if price:
                currency = '💰' if isinstance(price, int) else '👝'
                price = f'{currency}{price}'

            output.append(f'<code>{id}</code> {id_lookup.get(id, {}).get("name", "Name Missing")} x {misc["data"][id]} {price}')

        sort_by_weight = {id: misc['data'][id] * id_lookup.get(id, {}).get('weight', 1) for id in misc['data']}
        sort_by_weight = sorted(sort_by_weight, key=sort_by_weight.get, reverse=True)
        x = [misc['data'][id] * id_lookup.get(id, {}).get('weight', 1) for id in sort_by_weight]
        y = [f'{id_lookup.get(id, {}).get("name", "??").lower()} {id}' for id in sort_by_weight]
        r = range(len(sort_by_weight))
        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.figure(figsize=(6.4, 1.5+(len(sort_by_weight)*0.15)))
        plt.barh(r, x)
        plt.yticks(r, y, fontsize='8')
        plt.legend(loc='upper right', labels=['Weight'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        responses.append(buf)

        responses.append('\n'.join(output))
    else:
        responses.append(f'Missing recent guild stock state (&lt; {hours} hours old). Please forward the output from /g_stock_misc and try again')
    return responses


def warehouse_crafting(context):
    warehouse = warehouse_load_saved(guild=context.user_data.get('guild', ''))
    hours = 2.5
    responses = []
    now = datetime.datetime.utcnow()
    if (rec := warehouse.get('rec', {})) and (parts := warehouse.get('parts', {})) and \
       (age_rec := now - rec['timestamp']) < datetime.timedelta(hours=hours) and \
       (age_parts := now - parts['timestamp']) < datetime.timedelta(hours=hours):
        try:
            with open('auctionprices.dict', 'rb') as fp:
                prices = pickle.load(fp)
        except FileNotFoundError:
            prices = {}

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
            # parts_missing_for_next_set = count_parts % parts_needed
            # recipes_missing = complete_parts_sets - count_recipes
            things_missing = int(not bool(count_recipes)) + max(parts_needed - count_parts, 0)
            num_craftable = min(count_recipes, complete_parts_sets)
            ready = '✅' if num_craftable else '❌'
            finished_part_id = name_lookup[name.lower()]['id']
            recipe_location = get_id_location(rec_id)
            part_location = get_id_location(part_id)
            recipe_price = ''
            part_price = ''
            if prices:
                recipe_price = str(prices.get(rec_id, ''))
                part_price = str(prices.get(part_id, ''))
                if recipe_price:
                    recipe_price = f'👝{recipe_price}'
                if part_price:
                    part_price = f'👝{part_price}'

            # Getting through this gauntlet without hitting a continue means you get displayed
            if not num_craftable and not context.args:
                continue
            if context.args and context.args[0].lower() != 'all':  # if it's 'all' then jump to after the gauntlet
                if context.args[0].isdigit() and 0 < things_missing <= int(context.args[0]):
                    pass
                elif context.args[0].lower().startswith('overstock'):
                    try:
                        multiple = int(context.args[1])
                    except IndexError:
                        multiple = 2
                    if count_parts / parts_needed <= multiple and count_recipes <= multiple:
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
            if page_counter >= 2500:  # tg officially supports messages as long as 4096, but the formatting gives up around 3000
                responses.append('\n'.join(output))
                page_counter = 0
                output = []
            output.append(hold)

        result = '\n'.join(output)
        if result:
            responses.append(result)
        if result.rstrip().endswith(':'):
            responses.append('No matches in stock')

        if context.args and context.args[0].lower() in ('all', 'chart'):
            parts_rec = {**parts['data'], **rec['data']}
            count_and_weight = {id: parts_rec[id] * id_lookup[id]['weight'] for id in parts_rec}
            sort_by_weight = sorted(count_and_weight, key=count_and_weight.get, reverse=True)
            x = [
                [count_and_weight[id] if id[0] == 'k' else 0 for id in sort_by_weight],
                [count_and_weight[id] if id[0] == 'r' else 0 for id in sort_by_weight]
            ]
            y = [f"{id_lookup[id]['name'].lower()} {id}" for id in sort_by_weight]
            r = range(len(sort_by_weight))
            plt.clf()  # clear plot, because it doesn't get cleared from last run
            plt.figure(figsize=(6.4, 1.5+(len(sort_by_weight)*0.15)))
            plt.barh(r, x[0])
            plt.barh(r, x[1], color='red')
            plt.yticks(r, y, fontsize='8')
            plt.legend(loc='upper right', labels=['Parts', 'Recipes'])
            plt.subplots_adjust(left=0.3)
            buf = io.BytesIO()
            buf.name = 'weights.pdf'
            plt.savefig(buf, format='pdf')
            buf.seek(0)
            responses.append(buf)

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
            recipe = [{'name': name, 'number': int(amount) * count} for name, amount in info['recipe'].items() if name != 'Gold']
            recipe_str = '\n'.join([f'   {name}: {amount}{(f" x {count} = {int(amount) * count}" if count > 1 else "")}' for name, amount in info['recipe'].items()])
            response = [
                f'<b>{info["name"]}{(f" x {count}" if count > 1 else "")}</b>\n'
                f'''   Mana requirement: {info.get("craftMana", "unknown")}💧{(f" x {count} = {info.get('craftMana', 0) * count}💧" if count > 1 else "")}\n'''
                f'{recipe_str}\n\n'
                f'{withdraw_parts(recipe, context.user_data.get("guild", ""))}'
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
            output.append(out_str)  # \"{data['recipe']}\"
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
