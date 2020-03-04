import csv
import pickle
from datetime import datetime, time, timezone
from pathlib import Path
from urllib.parse import quote

import filetype
import requests
from telegram import ParseMode

from tealeyes import CW_OFFSET, CW_PERIODS, SPEED

def scrape_data(fp):
    '''get itemcode table and stuff it in a pickle'''
    url = 'https://raw.githubusercontent.com/AVee/cw_wiki_sync/master/data/resources.json'
    data = requests.get(url).json()['items']
    pickle.dump(data, fp)

def is_witching_hour():
    '''return True if market is closed'''
    closed_times = (
        (time( 6, 52), time( 7, 00)),
        (time(14, 52), time(15, 00)),
        (time(22, 52), time(23, 00))
    )
    now = datetime.utcnow().time()
    return any((start < now < end for start, end in closed_times))

def game_phase():
    adjustment = -37.0
    utcdt = datetime.now(timezone.utc)
    cwtdt = datetime.fromtimestamp(SPEED * (utcdt.timestamp() + CW_OFFSET), tz=timezone.utc)
    cwadt = datetime.fromtimestamp(cwtdt.timestamp() + SPEED * adjustment, tz=timezone.utc)
    return f'{CW_PERIODS[cwadt.hour//6]}'

def get_id_location(id):
    info = id_lookup.get(id, {})
    locations = (
        ('Forest', '🌲'),
        ('Swamp', '🍄'),
        ('Valley', '⛰')
    )
    phase = game_phase()
    output = ''
    for place, emoji in locations:
        if info.get(f'drop{place}{phase}'):
            output += emoji
    if output: output += ' ' + get_qualifications(id)
    return output

def get_qualifications(id):
    levels = {
        22: '22≤🏅≤39',
        32: '32≤🏅≤39',
        40: '40≤🏅≤45',
        46: '46≤🏅'
    }
    level = levels.get(id_lookup.get(id, {}).get('questMinLevel'), '')
    roman = ['', '<code>I/II</code>', '<code>II</code>', '<code>III</code>', '<code>IV</code>']
    perception_level = roman[id_lookup.get(id, {}).get('questPerceptionLevel', 0)]
    if perception_level: perception_level = '👀' + perception_level

    return level + perception_level

def warehouse_load_saved(ignore_exceptions=True, guild='full'):
    try:
        with open('warehouse.dict', 'rb') as warehouseFile:
            if guild == 'full':
                return pickle.load(warehouseFile)
            return pickle.load(warehouseFile).get(guild, {})

    except IOError:
        if not ignore_exceptions:
            raise
        else:
            return {}  # Ignore if warehouse.dict doesn't exist or can't be opened.

def get_lookup_dicts():
    if not Path('data.dict').is_file():
        with open('data.dict', 'wb') as fp:
            scrape_data(fp)
    with open('data.dict', 'rb') as fp:
        data = pickle.load(fp)
        id_lookup = {}
        name_lookup = {}
        for item in data:
            id_lookup[item['id']] = item
            name_lookup[item['name'].lower()] = item
    return id_lookup, name_lookup

def send(payload, update, context):
    chat_id = update.effective_message.chat_id
    if isinstance(payload, str):
        max_size = 4096
        for text in [payload[i:i + max_size] for i in range(0, len(payload), max_size)]:
            context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        kind = filetype.guess(payload.read(261))
        payload.seek(0)
        if kind and kind.mime.startswith('image'):
            context.bot.send_photo(chat_id=update.effective_message.chat_id, photo=payload)
        else:
            context.bot.send_document(chat_id=chat_id, document=payload)


id_lookup, name_lookup = get_lookup_dicts()


if __name__ == '__main__':
    from pprint import pprint
    pprint(id_lookup.get('r87'))
