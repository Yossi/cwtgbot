import datetime
import io
import os
import pickle
import re
from collections import defaultdict
from pprint import pprint
from rich import print


from util import is_witching_hour, warehouse_load_saved, get_id_location
from util import id_lookup, name_lookup
















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
