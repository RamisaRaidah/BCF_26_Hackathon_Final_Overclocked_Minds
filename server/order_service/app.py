from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import timedelta
import logging
import os

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ["SECRET_KEY"] 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days = 1) 
jwt = JWTManager(app)

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

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 8001, debug = True)