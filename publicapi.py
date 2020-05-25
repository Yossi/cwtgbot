import datetime
import json
import pickle
from pathlib import Path

from kafka import KafkaConsumer
from rich import print

from util import name_lookup

consumer = KafkaConsumer(
    #'cw2-offers',
    #'cw2-deals',
    #'cw2-duels',
    'cw2-sex_digest',
    #'cw2-yellow_pages',
    'cw2-au_digest',

    bootstrap_servers=['digest-api.chtwrs.com:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='💩',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


def handle_sex(message):
    with open('stockprices.dict', 'rb') as fp:
        store = pickle.load(fp)

    sex = message.value
    sex_list = ['New Cheapest Items:\n']
    for item in sex:
        id = name_lookup[item['name'].lower()]['id']
        price = item['prices'][0]
        store[id] = price
    store['last_update'] = datetime.datetime.utcnow()

    with open('stockprices.dict', 'wb') as fp:
        pickle.dump(store, fp)

    print(store)


def handle_au(message):
    with open('auctionprices.dict', 'rb') as fp:
        store = pickle.load(fp)

    au = message.value
    for auction in au:

        if auction['status'] not in ['Finished']: continue
        name = auction['itemName'].lower()
        id = name_lookup.get(name, {}).get('id')
        if not id: continue
        price = auction['price']
        store[id] = price
    store['last_update'] = datetime.datetime.utcnow()

    with open('auctionprices.dict', 'wb') as fp:
        pickle.dump(store, fp)

    print(store)


def handle_deals(message):
    deal = message.value

    deal_structure = 'New Deal:\n' + \
                     'sellerId: {}\n' + \
                     'sellerCastle: {}\n' + \
                     'sellerName: {}\n' + \
                     'buyerId: {}\n' + \
                     'buyerCastle: {}\n' + \
                     'buyerName: {}\n' + \
                     'item: {}\n' + \
                     'qty: {}\n' + \
                     'price: {}\n'

    print(deal_structure.format(deal['sellerId'],
                                deal['sellerCastle'],
                                deal['sellerName'],
                                deal['buyerId'],
                                deal['buyerCastle'],
                                deal['buyerName'],
                                deal['item'],
                                deal['qty'],
                                deal['price']))


def handle_duels(message):
    duel = message.value

    duel_structure = 'New Duel:\n' + \
                     'Winner:\n' + \
                     '   id: {}\n' + \
                     '   name: {}\n' + \
                     '   castle: {}\n' + \
                     '   level: {}\n' + \
                     '   hp: {}\n' + \
                     'Looser:\n' + \
                     '   id: {}\n' + \
                     '   name: {}\n' + \
                     '   castle: {}\n' + \
                     '   level: {}\n' + \
                     '   hp: {}\n' + \
                     'isChallenge: {}\n' + \
                     'isGuildDuel: {}\n'

    print(duel_structure.format(duel['winner']['id'],
                                duel['winner']['name'],
                                duel['winner']['castle'],
                                duel['winner']['level'],
                                duel['winner']['hp'],
                                duel['loser']['id'],
                                duel['loser']['name'],
                                duel['loser']['castle'],
                                duel['loser']['level'],
                                duel['loser']['hp'],
                                duel['isChallenge'],
                                duel['isGuildDuel']))


def handle_offers(message):
    offer = message.value

    offer_structure = 'New Offer:\n' + \
                      'sellerId: {}\n' + \
                      'sellerCastle: {}\n' + \
                      'sellerName: {}\n' + \
                      'item: {}\n' + \
                      'qty: {}\n' + \
                      'price: {}\n'

    print(offer_structure.format(offer['sellerId'],
                                 offer['sellerCastle'],
                                 offer['sellerName'],
                                 offer['item'],
                                 offer['qty'],
                                 offer['price']))


def handle_yellow(message):
    yellow = message.value
    yellow_list = ['Open Shops:\n']
    for shop in yellow:
        yellow_list.append(shop['kind'])
        yellow_list.append(shop['name'])
        yellow_list.append(' of ')
        yellow_list.append(shop['ownerCastle'])
        yellow_list.append(shop['ownerName'])
        yellow_list.append(' - current Mana: ')
        yellow_list.append(str(shop['mana']))
        yellow_list.append(' /ws_')
        yellow_list.append(shop['link'])
        yellow_list.append('\n')
    print(''.join(yellow_list))


def handle_message(message):
    switcher = {
        'cw2-deals': handle_deals,
        'cw2-offers': handle_offers,
        'cw2-sex_digest': handle_sex,
        'cw2-yellow_pages': handle_yellow,
        'cw2-au_digest': handle_au,
        #'cw3-deals': handle_deals,
        #'cw3-offers': handle_offers,
        #'cw3-sex_digest': handle_sex,
        #'cw3-yellow_pages': handle_yellow,
        #'cw3-au_digest': handle_au,
    }
    func = switcher.get(message.topic, lambda x: f"No handler for topic {message.topic}")
    return func(message)

def main():
    for picklename in ['stockprices.dict', 'auctionprices.dict']:
        if not Path(picklename).is_file():
            with open(picklename, 'wb') as fp:
                pickle.dump({}, fp)

    for message in consumer:
        handle_message(message)

if __name__ == '__main__':
    main()
