from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
import os, pathlib
