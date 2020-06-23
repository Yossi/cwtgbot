import io
import datetime
from utils.warehouse import load_saved
from utils.wiki import id_lookup
import matplotlib.pyplot as plt
import pickle


def alch_list(context):
    warehouse = load_saved(guild=context.user_data.get('guild', ''))
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
