from flask import Flask, request, render_template, flash, session
from flask_cors import CORS
from os import urandom
from datetime import timedelta

import OPRF

app = Flask(__name__)
CORS(app, origins=["https://katiehsong.pythonanywhere.com"])

# Set secure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True       # Ensures cookies are sent only over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True     # Prevents JavaScript access to the cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'    # Helps mitigate CSRF attacks

app.secret_key = urandom(24)
# In Flask, the secret key is used to sign session cookies cryptographically, ensuring data integrity and preventing tampering.

app.permanent_session_lifetime = timedelta(minutes=15)
# Store the permanent session data for 15 minutes (other options: minutes, days, seconds, etc)

app.last_received = ""
app.last_sent = ""

oprf = OPRF.OPRF()

@app.route("/")
def home():
    session.permanent = True
    flash(f"Last received: {app.last_received}")
    flash(f"Last sent: {app.last_sent}")
    return render_template("index.html")

@app.route("/receive_data", methods=["POST"])
def receiveData():
    data = request.get_json()
    # serverName = data["Server Name"]
    # message = data["Message"]
    input = data["Input"]
    app.last_received = input
    app.last_sent = oprf.raiseToK(input)

    return app.last_sent, 200