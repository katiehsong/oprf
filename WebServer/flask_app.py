from flask import Flask, redirect, url_for, render_template, request, session, flash
import requests

from os import urandom
# Method to generate a string of size random bytes suitable for cryptographic use

from datetime import timedelta
# For storing data for permanent sessions

import Server

KEY_SERVER = "https://katieehsong.pythonanywhere.com/receive_data"

app = Flask(__name__)

# Set secure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True       # Ensures cookies are sent only over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True     # Prevents JavaScript access to the cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'    # Helps mitigate CSRF attacks

app.secret_key = urandom(24)
# In Flask, the secret key is used to sign session cookies cryptographically, ensuring data integrity and preventing tampering.

app.permanent_session_lifetime = timedelta(minutes=15)
# Store the permanent session data for 15 minutes (other options: minutes, days, seconds, etc)

server = Server.Server()

@app.route("/")
def home():
    return render_template("index.html")

def requestData(input):
    data = {
        "Server Name": "Basebook",
        "Message": "Hello from Web Server to the Key Server",
        "Request Type": "F",
        "Input": input
        }
    try:
        response = requests.post(KEY_SERVER, json=data)
        return response.text
    except requests.exceptions.RequestException:
        return " :( "

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pw"]
        if not server.validData(user, password):
            flash("Please make sure your username and password are valid.")
        elif server.addUser(user, password):
            r, rPower = server.computeRPower(user, password)
            f = requestData(rPower)
            server.addF(user, f)
            flash("Sign Up Succesful! Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Sign Up Failed...")
        return redirect(url_for("signup"))
    else:
        # If a user is already logged in (tracked via session), redirect to user page
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
        return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True # Enables the session to last based on `permanent_session_lifetime`

        user = request.form["nm"]
        password = request.form["pw"]

        if not server.validData(user, password):
            flash("Please make sure your username and password are valid.")
        elif not server.existName(user):
            flash("The username does not exist.")
        else:
            r, rPower = server.computeRPower(user, password)
            f = requestData(rPower)
            flash(f"Username:\n\t{user}")
            flash(f"H(pw || salt):\n\t{server.getHash(user, password)}")
            flash(f"r: {r}")
            flash(f"Sent H(pw || salt)^r:\n\t{rPower}")
            flash(f"Received H(pw || salt)^(rk):\n\t{f}")

            inverseR, fInverseR = server.reverseRPower(user, f)
            flash(f"inverse of r in mod: {inverseR}")
            flash(f"H(pw || salt)^(rk/r) = H(pw || salt)^k: {fInverseR}")

            if server.users[user]['F_Output'] == fInverseR:
                session["user"] = user
                session["password"] = password
                flash("Login Succesful!")
            else:
                flash("Login failed")
                flash(f"{server.users[user]['F_Output']}")
                flash(f"{fInverseR}")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
        return render_template("login.html", data=server.users)

@app.route("/user")
def user():
    if "user" in session: # Access control: only show user page if session contains a logged-in user
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out!", "info")
        session.pop("user", None) # Remove user from session
    else:
        flash("You are not logged in.")
    return redirect(url_for("login"))
