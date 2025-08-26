# tracks pubnub and writes to mongodb. Created using ChatGPT



import os
import requests
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pymongo import MongoClient
from datetime import datetime, timezone
from pubnub.crypto import AesCbcCryptoModule


load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME   = os.getenv("DB_NAME","smarthome")
COLL      = os.getenv("COLLECTION","readings")
PUB_KEY   = os.getenv("PUB_KEY")
SUB_KEY   = os.getenv("SUB_KEY")
CHANNEL   = os.getenv("CHANNEL","pi.home.demo")
CIPHER_KEY = os.getenv("CIPHER_KEY")
PN_SERVER_TOKEN = os.getenv("PN_SERVER_TOKEN")

client = MongoClient(MONGO_URL)
col = client[DB_NAME][COLL]


pnconf = PNConfiguration()
pnconf.publish_key = PUB_KEY
pnconf.subscribe_key = SUB_KEY
pnconf.user_id = "server-api" 
pnconf.cipher_key = CIPHER_KEY
pnconf.crypto_module = AesCbcCryptoModule(pnconf)
pubnub = PubNub(pnconf)

class Listener(SubscribeCallback):
    def message(self, pubnub, event):
        msg = event.message or {}
        sensor = msg.get("sensor")
        value  = msg.get("value")
        if sensor is None or value is None:
            return
        col.insert_one({"ts": datetime.now(timezone.utc),
                        "sensor": sensor,
                        "value": float(value)})

if __name__ == "__main__":
    if PN_SERVER_TOKEN:
        pubnub.set_token(PN_SERVER_TOKEN)
    else:
        raise SystemExit("Missing PN_SERVER_TOKEN in .env. Cannot subscribe with PAM enabled.")


    pubnub.add_listener(Listener())
    pubnub.subscribe().channels(CHANNEL).execute()
    # keep process alive
    import threading; threading.Event().wait()
