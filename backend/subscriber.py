# tracks pubnub and writes to mongodb. Created using ChatGPT



import os, time
import requests
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pymongo import MongoClient
from datetime import datetime, timezone


load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME   = os.getenv("DB_NAME","smarthome")
COLL_NAME = os.getenv("COLLECTION","readings")
PUB_KEY   = os.getenv("PUB_KEY")
SUB_KEY   = os.getenv("SUB_KEY")
CHANNEL   = os.getenv("CHANNEL","pi.home.luke")
CIPHER_KEY = os.getenv("CIPHER_KEY")
PN_SERVER_TOKEN = os.getenv("PN_SERVER_TOKEN")


#mongodb
client = MongoClient(MONGO_URL)
col = client[DB_NAME][COLL_NAME]

#pubnunb
pnconf = PNConfiguration()
pnconf.publish_key = PUB_KEY
pnconf.subscribe_key = SUB_KEY
pnconf.user_id = "server-api" 


if CIPHER_KEY:
    pnconf.cipher_key = CIPHER_KEY

pubnub = PubNub(pnconf)
if PN_SERVER_TOKEN:
    pubnub.set_token(PN_SERVER_TOKEN)



print(f"Subscriber listening on channel {CHANNEL}...")


class Listener(SubscribeCallback):
    def message(self, pubnub, event):
        msg = event.message or {}
        try:
            doc = {
                "sensor": msg.get("sensor"),
                "value": msg.get("value"),
                "src": msg.get("src", "pi"),
                "ts": msg.get("ts") or datetime.now(timezone.utc).isoformat()
            }
            if doc["sensor"] and doc["value"] is not None:
                col.insert_one(doc)
                print(f"saved {doc['sensor']}={doc['value']} at {doc['ts']}")
            else:
                print("skipped bad msg:", msg)
        except Exception as e:
            print("error saving:", e, "msg:", msg)

pubnub.add_listener(Listener())
pubnub.subscribe().channels(CHANNEL).execute()

while True:
    time.sleep(60)
