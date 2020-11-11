import datetime
import pickle

from utils.wiki import name_lookup


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

            out_str = f"/c_{id} {data['name']}\n {'✅' if buy_price > make_price else '❌'}Make: {make_price}💰, {'❌' if buy_price > make_price else '✅'}Buy: {buy_price}💰"
            output.append(out_str)  # \"{data['recipe']}\"
    output.sort()
    output.append(f"\nPrices no fresher than {(now - prices['last_update']).seconds // 60} minutes.")
    return '\n'.join(output)
