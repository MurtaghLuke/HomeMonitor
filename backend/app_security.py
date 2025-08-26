#### secure pubnub channels.
import os
from flask import Blueprint, request, jsonify, abort
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.models.consumer.v3.channel import Channel

bp = Blueprint("security", __name__)


# load keys from .env and creates pubnub admin client
def _pubnub_admin():
    cfg = PNConfiguration()
    cfg.publish_key = os.getenv("PUB_KEY")
    cfg.subscribe_key = os.getenv("SUB_KEY")
    cfg.secret_key = os.getenv("SECRET_KEY")#needed to grant tokens
    cfg.user_id = "server-api"
    return PubNub(cfg)





###Two functions below made with the help of ChatGPT

#generate tokens when pi makes a post with the json data
@bp.route("/api/token/device", methods=["POST"])
def token_for_device():
    data = request.get_json(force=True)
    device_uuid = data.get("uuid")  #must read unique user id from pi
    if not device_uuid:
        abort(400, "uuid required")

    pubnub = _pubnub_admin() #create a pubnub client in admin mode using secret key. cant grant tokens without secret key.
    envelope =(pubnub.grant_token() # call for pi
                .channels([Channel.id("pi.home.luke").write()]) # token will only allow writing to this channel
                .authorized_uuid(device_uuid) # token only works if clients user_id matches this uuid
                .ttl(336)  #token expires in 60 mins
                .sync()) # runs request and waits till pubnub responds before continuing.
    if envelope.status.is_error():
        abort(500, envelope.status.error_data.information)

    return jsonify({"token": envelope.result.get_token()})


@bp.route("/api/token/server", methods=["POST"])
def token_for_server():
    pubnub = _pubnub_admin()
    # Server subscribes to all device channels and can publish to UI channel
    envelope = (pubnub.grant_token()
                .channels([
                    Channel.pattern("pi.home.*").read(),# lets server read to all pi.home channels
                    Channel.id("ui.home.luke").write()# lets server write updates to ui
                ])
                .authorized_uuid("server-api") # only works if clients user id is "server-api"
                .ttl(336)
                .sync())
    if envelope.status.is_error():
        abort(500, envelope.status.error_data.information)

    return jsonify({"token": envelope.result.get_token()})
