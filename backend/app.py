from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import os, pathlib



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