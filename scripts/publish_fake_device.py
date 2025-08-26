#backend testing.



import os, random, time
from dotenv import load_dotenv
from pathlib import Path
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.crypto import AesCbcCryptoModule
load_dotenv(Path(__file__).resolve().parent.parent / "backend" / ".env")


def require(name):
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing {name} in .env. Add it and re-run.")
    return v

CIPHER_KEY      = require("CIPHER_KEY")
PN_DEVICE_TOKEN = require("PN_DEVICE_TOKEN")
PUB_KEY         = require("PUB_KEY")
SUB_KEY         = require("SUB_KEY")
CHANNEL         = os.getenv("CHANNEL", "pi.home.demo")

pnconf = PNConfiguration()
pnconf.publish_key = os.getenv("PUB_KEY")
pnconf.subscribe_key = os.getenv("SUB_KEY")
pnconf.user_id = "my-device-1"
pnconf.cipher_key = CIPHER_KEY
pnconf.crypto_module = AesCbcCryptoModule(pnconf)
pubnub = PubNub(pnconf)

#BELOW MADE WITH CHATGPT 
def send_once():
    payload = {"sensor":"temperature","value":round(random.uniform(18,25),2)}
    envelope = pubnub.publish().channel(CHANNEL).message(payload).sync()
    print("pub status:", envelope.status.is_error())

if __name__ == "__main__":
    if PN_DEVICE_TOKEN:
        pubnub.set_token(PN_DEVICE_TOKEN)
    else:
        raise SystemExit("Missing PN_DEVICE_TOKEN in .env. cannot publish with PAM enabled.")
    while True:
        send_once()
        time.sleep(5)
