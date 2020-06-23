import datetime
import io
import pickle

import matplotlib.pyplot as plt

from utils.warehouse import load_saved
from utils.wiki import id_lookup


def misc_list(context):
    warehouse = load_saved(guild=context.user_data.get('guild', ''))
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
