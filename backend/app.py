from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timezone 
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import os, pathlib


# load in .env values
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "smarthome")
COLLECTION = os.getenv("COLLECTION", "readings")


#//  connect to mongo db
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
col = db[COLLECTION]

# create flask app
app = Flask(
    __name__,
    static_folder="../web",      #  serves index.html
    static_url_path="/"          # serves the web folder
)





#health check to see if server is running.
@app.route("/health", methods=["GET"] )
def health():
    return jsonify({"status": "ok"})


# json POST request recieved from device and saves the reading to mongo
@app.route("/api/readings", methods=["POST"])
def create_reading():
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
    })



# get latest reading from mongodb
@app.route("/api/readings/latest", methods=["GET"])
def latest_reading():
    saved = col.find_one(sort=[("_id", DESCENDING)])
    if not saved:
        return jsonify({"detail": "No readings yet"}), 404
    return jsonify({
        "id": str(saved["_id"]),
        "ts": saved["ts"].isoformat(),
        "sensor": saved["sensor"],
        "value": saved["value"]
    })



# index.html webpage route
@app.route("/")
def index():
    p = pathlib.Path(app.static_folder) / "index.html"
    if p.exists():
        return send_from_directory(app.static_folder, "index.html")
    return "Add web/index.html", 200

# can run locally
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)









