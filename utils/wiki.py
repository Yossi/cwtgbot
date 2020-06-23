import requests
import json
from pathlib import Path


def scrape_data(fp):
    """get itemcode table and stuff it in a file"""
    url = 'https://raw.githubusercontent.com/AVee/cw_wiki_sync/master/data/resources.json'
    data = requests.get(url).text
    fp.write(data)


def get_lookup_dicts():
    try:
        lastrev = requests.get('https://raw.githubusercontent.com/AVee/cw_wiki_sync/master/data/lastrev').text

        with open('lastrev', 'r') as revfp:
            localrev = revfp.readline()
            if lastrev != localrev:
                with open('data.json', 'w') as fp:
                    scrape_data(fp)

        with open('lastrev', 'w') as fp:
            fp.write(lastrev)
    except:
        pass  # if we end up here for whatever reason (almost certainly a network error) then just move on. If network is really down AND we don't have data.dict yet then we explode later

    if not Path('data.json').is_file():
        with open('data.json', 'w') as fp:
            scrape_data(fp)
    with open('data.json', 'r') as fp:
        j = json.load(fp)
        data = j['items']
        data.extend(j['incomplete'])
        id_lookup = {}
        name_lookup = {}
        for item in data:
            id_lookup[item['id']] = item
            name_lookup[item['name'].lower()] = item
    return id_lookup, name_lookup


id_lookup, name_lookup = get_lookup_dicts()
