import datetime
import json
import pickle
from pathlib import Path
from pprint import pprint

import websocket

from util import name_lookup


def on_message(ws, message):
    with open('stockprices.dict', 'rb') as fp:
        store = pickle.load(fp)

    data = json.loads(message)
    for datum in data:
        id = name_lookup[datum['name'].lower()]['id']
        price = datum['prices'][0]
        store[id] = price
    store['last_update'] = datetime.datetime.utcnow()

    with open('stockprices.dict', 'wb') as fp:
        pickle.dump(store, fp)

    pprint(store)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

if __name__ == "__main__":
    if not Path('stockprices.dict').is_file():
        with open('stockprices.dict', 'wb') as fp:
            pickle.dump({}, fp)

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://mc.guppygalaxy.com:18518/sex_digest",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.run_forever()
