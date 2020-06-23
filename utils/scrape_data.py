import requests


def scrape_data():
    """returns a JSON object with wiki items"""
    url = 'https://raw.githubusercontent.com/AVee/cw_wiki_sync/master/data/resources.json'
    data = requests.get(url).json
    return data
