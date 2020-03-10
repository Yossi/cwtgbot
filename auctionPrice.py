import datetime
import json
import pickle
from pathlib import Path
from pprint import pprint

import websocket

from util import name_lookup

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

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://mc.guppygalaxy.com:18518/au_digest",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.run_forever()
