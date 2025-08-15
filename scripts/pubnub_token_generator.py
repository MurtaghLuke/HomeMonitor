import os
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.models.consumer.v3.channel import Channel

load_dotenv()




PUB = os.getenv("PUB_KEY")
SUB = os.getenv("SUB_KEY")
SEC = os.getenv("SECRET_KEY")

def admin():
    cfg = PNConfiguration()
    cfg.publish_key = PUB
    cfg.subscribe_key = SUB
    cfg.secret_key = SEC
    cfg.user_id = "server-api"
    return PubNub(cfg)

if __name__ == "__main__":
    pn = admin()

    
    #### BELOW MADE WITH CHATGPT
    # Server token can read device channels and write ui channel
    server_env = (pn.grant_token()
                    .channels([Channel.pattern("pi.home.*").read()])
                    .authorized_uuid("server-subscriber-1")
                    .ttl(60)   # expires in 60mins
                    .sync())

    if server_env.status.is_error():
        raise SystemExit(server_env.status.error_data.information)
    server_token = server_env.result.get_token()

    #device token: can only write to single device -> server channel
    chan = os.getenv("CHANNEL","pi.home.luke")
    device_env = (pn.grant_token()
                    .channels([Channel.id(chan).write()])
                    .authorized_uuid("my-device-1")
                    .ttl(60)
                    .sync())

    if device_env.status.is_error():
        raise SystemExit(device_env.status.error_data.information)
    device_token = device_env.result.get_token()

    print("\nPN_SERVER_TOKEN=", server_token, sep="")
    print("PN_DEVICE_TOKEN=", device_token, sep="")
