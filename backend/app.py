from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
from pathlib import Path
import os, pathlib
from .app_security import bp as security_bp
from flask_cors import CORS


#load env from backend folder
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "https://homemonitor.click") #CORS suggested by chatgpt. lets browser call endpoints safely.


# load in .env values
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "smarthome")
COLLECTION = os.getenv("COLLECTION", "readings")
API_INGEST_KEY = os.getenv("API_INGEST_KEY")


# Fail if DB url is missing(helps debugging) (chatgpt)
if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set. Put it in backend/.env")




#//  connect to mongo db
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
col = db[COLLECTION]
col.create_index([("ts", DESCENDING)])




# create flask app
app = Flask(
    __name__,
    static_folder="../web",      #  serves index.html
    static_url_path="/static"    # serves the web folder
)
CORS(app, resources={r"/api/*": {"origins": ["https://homemonitor.click"]}}) # allows browser call only /api/ endpoints from site. Chatgpt.


app.register_blueprint(security_bp) # register blueprint so /api/token/ routes exist


#health check to see if server is running.
@app.route("/health", methods=["GET"] )
def health():
    return jsonify({"status": "ok"})


#test endpoint to confirm backend is alive. Suggested by Chatgpt.
@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"ok": True, "server": "up"}), 200


# json POST request recieved from device and saves the reading to mongo. Used ChatGPT
@app.route("/api/readings", methods=["POST"])
def create_reading():
    
    if API_INGEST_KEY and request.headers.get("X-API-Key") != API_INGEST_KEY:
        return jsonify({"detail": "unauthorized"}), 401
    
    data = request.get_json(force=True) or {}
    sensor = data.get("sensor")
    value = data.get("value")

    if sensor is None or value is None:
        return jsonify({"detail": "sensor and value required"}), 400



    doc = {
        "ts": datetime.now(timezone.utc),
        "sensor": sensor,
        "value": float(value)
    }
    result = col.insert_one(doc)
    saved = col.find_one({"_id": result.inserted_id})
    # returns saved reaading as json
    return jsonify({
        "id": str(saved["_id"]),
        "ts": saved["ts"].isoformat(),
        "sensor": saved["sensor"],
        "value": saved["value"]
    }), 201



# latest per sensor. Made  by chatgpt.
@app.route("/api/latest", methods=["GET"])
def latest_per_sensor():
    # choose the sensors you use
    sensors = ["temperature", "humidity", "motion"]
    res = {}
    for s in sensors:
        d = col.find_one({"sensor": s}, sort=[("ts", DESCENDING)])
        if d:
            res[s] = {
                "value": d["value"],
                "ts": d["ts"].isoformat()
            }
        else:
            res[s] = None
    return jsonify(res), 200



# get latest reading from mongodb. Used ChatGPT
@app.route("/api/readings/latest", methods=["GET"])
def latest_reading():
    saved = col.find_one(sort=[("ts", DESCENDING)])
    if not saved:
        return jsonify({"detail": "No readings yet"}), 404
    return jsonify({
        "id": str(saved["_id"]),
        "ts": saved["ts"].isoformat(),
        "sensor": saved["sensor"],
        "value": saved["value"]
    })

@app.route("/api/readings", methods=["GET"])
def list_readings():
    try:
        limit = min(int(request.args.get("limit", 20)), 200)
    except:
        limit = 20

    #fro 'per sensor' data. Suggested by chatgpt.
    sensor = request.args.get("sensor")
    query = {}
    if sensor:
        query["sensor"] = sensor


    docs = col.find(query).sort("ts", DESCENDING).limit(limit)
    out = [{
        "id": str(d["_id"]),
        "ts": d["ts"].isoformat(),
        "sensor": d["sensor"],
        "value": d["value"]
    } for d in docs]
    out.reverse() # acsending time
    return jsonify(out) , 200


# index.html webpage route. Used ChatGPT
@app.route("/")
def index():
    p = pathlib.Path(app.static_folder) / "index.html"
    if p.exists():
        return send_from_directory(app.static_folder, "index.html")
    return "Add web/index.html", 200

# can run locally
if __name__ == "__main__":
    print(app.url_map)
    app.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False, threaded=False)









