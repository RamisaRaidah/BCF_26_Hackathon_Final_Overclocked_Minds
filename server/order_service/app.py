from flask import Flask, jsonify
import logging
import os

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
    return jsonify({"status": "ok"}), 200 

# @app.route("/alert")
# def alert():
    

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = os.environ["ORDER_PORT"], debug = True)