import datetime
import pickle
import re

from utils.wiki import name_lookup


def special_sort(x):
    m = re.search(r'>(\D*)(\d*)<', x)
    prefix = m.groups()[0]
    num = ''
    try:
        num = int(m.groups()[1])
    except:
        pass
    return prefix, num


def prices_report(context):
    output = []
    now = datetime.datetime.utcnow()
    with open('stockprices.dict', 'rb') as fp:
        prices = pickle.load(fp)
        price_age = prices['last_update']
    with open('auctionprices.dict', 'rb') as fp:
        prices.update(pickle.load(fp))

    prices['last_update'] = min(prices['last_update'], price_age)

    args = []
    if context.args:
        args = context.args

    for name, data in name_lookup.items():
        if data.get('exchange') or data.get('auction'):
            id = data['id']
            if args and id not in args:
                continue
            price = prices.get(id, '')
            if not price:
                continue

            out_str = f"<code>{id}</code> {data['name']} {'💰' if data.get('exchange') else '👝'}{price}"
            output.append(out_str)
    output.sort(key = special_sort)
    output.append(f"\nPrices no fresher than {(now - prices['last_update']).seconds // 60} minutes.")
    return '\n'.join(output)
