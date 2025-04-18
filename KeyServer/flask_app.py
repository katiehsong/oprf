from flask import Flask, request, render_template
from flask_cors import CORS

import OPRF

app = Flask(__name__)
CORS(app, origins=["https://katiehsong.pythonanywhere.com"])

oprf = OPRF.OPRF()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/receive_data", methods=["POST"])
def receiveData():
    data = request.get_json()
    # serverName = data["Server Name"]
    # message = data["Message"]
    input = data["Input"]

    return oprf.raiseToK(input), 200