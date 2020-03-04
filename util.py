import csv
import pickle
from datetime import datetime, time, timezone
from pathlib import Path
from urllib.parse import quote

import filetype
import requests
from telegram import ParseMode

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

if __name__ == '__main__':
    from pprint import pprint
    from pathlib import Path
    if not Path("data.dict").is_file() or True:
        with open('data.dict', 'wb') as fp:
            scrape_data(fp)

    with open('data.dict', 'rb') as fp:
        data = pickle.load(fp)
        pprint(data)
