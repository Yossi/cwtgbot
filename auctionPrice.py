import datetime
import json
import pickle
from pathlib import Path
from pprint import pprint
from time import sleep

import websocket

from util import name_lookup

domain = 'doge-stock.com/EUCW'
feed = 'au_digest'
picklename = 'auctionprices.dict'

def on_message(ws, message):
    with open(picklename, 'rb') as fp:
        store = pickle.load(fp)

    data = json.loads(message)
    for datum in data:
        if datum['status'] not in ['Finished']: continue
        name = datum['itemName'].lower()
        id = name_lookup.get(name, {}).get('id')
        if not id: continue
        price = datum['price']
        store[id] = price
    store['last_update'] = datetime.datetime.utcnow()

    with open(picklename, 'wb') as fp:
        pickle.dump(store, fp)

    pprint(store)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

if __name__ == "__main__":
    if not Path(picklename).is_file():
        with open(picklename, 'wb') as fp:
            pickle.dump({}, fp)

    #websocket.enableTrace(True)
    while True:
        ws = websocket.WebSocketApp(f'wss://{domain}/{feed}',
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.run_forever()
        print('waiting 2 seconds..')
        sleep(2)
        print("time's up. connecing again")
