from flask import Flask, jsonify
from datetime import timedelta
import logging
import os
from db import get_db_connection, execute_query

app = Flask(__name__)

logging.basicConfig (
    filename = "app.log",
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/")
def home():
    return "Biday prithibi"

@app.route("/health")
def health(): 
    row = execute_query("SELECT 1 AS ok FROM stock LIMIT 1;", fetch_one = True)
    if row is None:
        return jsonify({"status": "error", "detail": "db unreachable or schema missing"}), 500
    return jsonify({"status": "ok"}), 200 

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 8001, debug = True)