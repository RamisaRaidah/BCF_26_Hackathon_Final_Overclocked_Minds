from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

logging.basicConfig (
    filename = "app.log",
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/")
def profile():
    return "Ami"

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return "hello"
    else:
        name = request.get_json()["name"]
        return jsonify(name)

@app.route("/helth")
def health():
    return jsonify({"status": "ok"}), 200 

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 8001, debug = True)