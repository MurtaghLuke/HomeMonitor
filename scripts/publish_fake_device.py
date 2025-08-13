import os, random, time
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

load_dotenv()

pnconf = PNConfiguration()
pnconf.publish_key = os.getenv("PUB_KEY")
pnconf.subscribe_key = os.getenv("SUB_KEY")
pnconf.uuid = "my-device-1"
pubnub = PubNub(pnconf)
CHANNEL = os.getenv("CHANNEL", "pi.home.demo")

def send_once():
    payload = {"sensor":"temperature","value":round(random.uniform(18,25),2)}
    envelope = pubnub.publish().channel(CHANNEL).message(payload).sync()
    print("pub status:", envelope.status.is_error())

if __name__ == "__main__":
    while True:
        send_once()
        time.sleep(5)
