import pickle
import requests
from bs4 import BeautifulSoup
from datetime import datetime, time

def scrape_data(fp):
    '''get itemcode table and stuff it in a pickle'''
    data = {}
    wiki_url = "https://chatwars-wiki.de/index.php?title=Master_List_of_Item_Codes"
    page = requests.get(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, features="html.parser")
    table = soup.find("table", {"class": "sortable wikitable smwtable"})
    for row in table.findAll('tr')[1:]:
        name, code, weight, item_type = row.findAll('td')
        data[name.text.lower()] = code.text.lower(), int(weight.text) if weight.text else 1
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

def emoji_number(n):
    digits = {
        0:'0️⃣',
        1:'1️⃣',
        2:'2️⃣',
        3:'3️⃣',
        4:'4️⃣',
        5:'5️⃣',
        6:'6️⃣',
        7:'7️⃣',
        8:'8️⃣',
        9:'9️⃣',
       10:'🔟',
    }
    if n in digits:
        return digits[n]
    return ''.join([digits[int(x)] for x in str(n)])


if __name__ == '__main__':
    from pprint import pprint

    print(emoji_number(10))
