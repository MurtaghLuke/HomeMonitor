# tracks pubnub and writes to mongodb. Created using ChatGPT



import os
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pymongo import MongoClient
from datetime import datetime, timezone

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME   = os.getenv("DB_NAME","smarthome")
COLL      = os.getenv("COLLECTION","readings")
PUB_KEY   = os.getenv("PUB_KEY")
SUB_KEY   = os.getenv("SUB_KEY")
CHANNEL   = os.getenv("CHANNEL","pi.home.demo")

client = MongoClient(MONGO_URL)
col = client[DB_NAME][COLL]

pnconf = PNConfiguration()
pnconf.publish_key = PUB_KEY
pnconf.subscribe_key = SUB_KEY
pnconf.uuid = "server-subscriber-1" 
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
    pubnub.add_listener(Listener())
    pubnub.subscribe().channels(CHANNEL).execute()
    # keep process alive
    import threading; threading.Event().wait()
