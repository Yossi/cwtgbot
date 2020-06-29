import datetime
import io
import json
import matplotlib.pyplot as plt

from utils.warehouse import load_saved
from utils.wiki import id_lookup

def all_stock(context):
    warehouse = load_saved(guild=context.user_data.get('guild', ''))
    hours = 50
    responses = []
    now = datetime.datetime.utcnow()
    if (res := warehouse.get('res', {})) and \
       (rec := warehouse.get('rec', {})) and \
       (alch := warehouse.get('alch', {})) and \
       (misc := warehouse.get('misc', {})) and \
       (parts := warehouse.get('parts', {})) and \
       (other := warehouse.get('other', {})) and \
       (age_res := now - res['timestamp']) < datetime.timedelta(hours=hours) and \
       (age_rec := now - rec['timestamp']) < datetime.timedelta(hours=hours) and \
       (age_alch := now - alch['timestamp']) < datetime.timedelta(hours=hours) and \
       (age_misc := now - misc['timestamp']) < datetime.timedelta(hours=hours) and \
       (age_parts := now - parts['timestamp']) < datetime.timedelta(hours=hours) and \
       (age_other := now - other['timestamp']) < datetime.timedelta(hours=hours):

        ages = (
            (age_res, '/g_stock_res'),
            (age_rec, '/g_stock_rec'),
            (age_alch, '/g_stock_alch'),
            (age_misc, '/g_stock_misc'),
            (age_parts, '/g_stock_parts'),
            (age_other, '/g_stock_other')
        )
        age, command = max(ages)
        output = [f'Based on {command} data {age.seconds // 60} minutes old:\n']

        items_by_weight = {}
        for category in warehouse:
            if category != 'other':
                for id, count in warehouse[category]['data'].items():
                    items_by_weight[id] = count * id_lookup.get(id, {}).get('weight', 0)
            else:
                for id in warehouse[category]['data']:
                    items_by_weight[id] = sum(list(zip(*warehouse[category]['data'][id]))[2]) * id_lookup.get(id, {}).get('weight', 0)

        sorted_by_weight = sorted(items_by_weight, key=items_by_weight.get, reverse=True)

        x = [items_by_weight[id] for id in sorted_by_weight]
        y = [f"{id_lookup.get(id, {'name': 'unidentified object'})['name'].lower()} {id}" for id in sorted_by_weight]
        r = range(len(x))

        plt.clf()  # clear plot, because it doesn't get cleared from last run
        plt.figure(figsize=(6.4, (len(x) * 0.15)))
        plt.barh(r, x)
        plt.yticks(r, y, fontsize='8', fontname='symbola')
        plt.legend(loc='upper right', labels=['Weight in Guild Stock'])
        plt.subplots_adjust(left=0.3)
        buf = io.BytesIO()
        buf.name = 'weights.pdf'
        plt.savefig(buf, format='pdf')
        buf.seek(0)

        responses.append('\n'.join(output))
        responses.append(buf)

    else:
        for missing_category in set(['rec', 'parts', 'res', 'other', 'alch', 'misc']) - set(warehouse.keys()):
            print(f'/g_stock_{missing_category} is missing entirely.')
        for category in warehouse:
            if (now - warehouse[category]['timestamp']) > datetime.timedelta(hours=hours):
                print(f"/g_stock_{category} is over {hours} hours old")

    return responses
