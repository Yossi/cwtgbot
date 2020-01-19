import pickle
import requests
from telegram import ParseMode
from bs4 import BeautifulSoup
from datetime import datetime, time
import yaml
import csv
from urllib.parse import quote

def scrape_data(fp):
    '''get itemcode table and stuff it in a pickle'''
    data = []
    step = 500
    for offset in range(0, step*4, step):
        base = 'https://chatwars-wiki.de/index.php?title=Special:Ask/'
        settings = f'format=csv/searchlabel=CSV/offset={offset}/limit={step}/prettyprint=true/unescape=true'
        q = '/mainlabel=Name/[[ItemID::+]]/?ItemID/?Weight/?BoolExchange=Exchange/?BoolDepositGuild=Guild'
        query = quote(q, safe='=/:+').replace('%', '-')
        url = base+quote(settings+query, safe=':/')
        result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        for item in csv.DictReader(result.content.decode('utf-8')[1:].splitlines()):
            item['Name'] = item['Name'].lower()
            item['ItemID'] = item['ItemID'].lower()
            item['Weight'] = int(item['Weight']) if item['Weight'] else None
            item['Exchange'] = item['Exchange'] == 'true'
            if item['Guild'] == '':
                item['Guild'] = None
            else:
                item['Guild'] = item['Guild'] == 'true'
            data.append(item)
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

hsn = yaml.load(open('data/hebrew-special-numbers/styles/default.yml', encoding="utf8"), Loader=yaml.SafeLoader)
def hebrew_numeral(val, gershayim=True):
    '''get hebrew numerals for the number in val'''
    def add_gershayim(s):
        if len(s) == 1:
            return s + hsn['separators']['geresh']
        else:
            return ''.join([s[:-1], hsn['separators']['gershayim'], s[-1:]])

    k, val = divmod(val, 1000) # typically you leave off the thousands when writing the year

    if val in hsn['specials']:
        retval = hsn['specials'][val]
        return add_gershayim(retval) if gershayim else retval

    parts = []
    rest = str(val)
    l = len(rest) - 1
    for n, d in enumerate(rest):
        digit = int(d)
        if digit == 0: continue
        power = 10 ** (l-n)
        parts.append(hsn['numerals'][power * digit])
    retval = ''.join(parts)

    return add_gershayim(retval) if gershayim else retval

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
            return {} # Ignore if warehouse.dict doesn't exist or can't be opened.

def send(text, update, context):
    context.bot.send_message(chat_id=update.effective_message.chat_id, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

if __name__ == '__main__':
    from pprint import pprint
    from pathlib import Path
    if not Path("data2.dict").is_file() or True:
        with open('data2.dict', 'wb') as fp:
            scrape_data2(fp)
    
    with open('data.dict', 'rb') as fp:
        data = pickle.load(fp)
        pprint(data)
