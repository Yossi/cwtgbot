import io
import datetime
import pickle
from utils.warehouse import load_saved
from utils.wiki import id_lookup, name_lookup
import matplotlib.pyplot as plt


def stock(context):
    args = ['']
    if context.args:
        args = context.args

    warehouse = load_saved(guild=context.user_data.get('guild', ''))
    hours = 1.5
    responses = []
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
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

        if args[0] == 'nosort':
            ordered_items = sorted(res['data'], reverse=True)
        else:
            ordered_items = sorted(res['data'], key=res['data'].get, reverse=True)

        for id in ordered_items:
            trade = '✅' if id_lookup[id].get('exchange') else '❌'
            price = prices.get(id, '')
            if price:
                price = f' 💰{price}'

            craftable = ''
            if id_lookup[id]['craftable']:
                recipe = id_lookup[id]['recipe']
                fullsets = 1000000
                for name, count in recipe.items():
                    fullsets = min(res['data'].get(name_lookup[name.lower()]['id'], 0) // int(count), fullsets)
                craftable = f' ⚒ /c_{id} {fullsets}'

            output.append(f'{trade}<code>{id}</code> {id_lookup[id]["name"]} x {res["data"][id]}{price}{craftable}')
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
