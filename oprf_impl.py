from flask import Flask, redirect, url_for, render_template, request, session, flash

from threading import Thread
# Allows the Flask app to operate in the background

from os import urandom
# Method to generate a string of size random bytes suitable for cryptographic use

from datetime import timedelta
# For storing data for permanent sessions

import hashlib, os
import hmac as HMAC
from base64 import urlsafe_b64encode as b64encode

app = Flask(__name__)
app.secret_key = urandom(24)
# In Flask, the secret key is used to sign session cookies cryptographically, ensuring data integrity and preventing tampering.

app.permanent_session_lifetime = timedelta(minutes=5)
# Store the permanent session data for 10 seconds (other options: minutes, days, )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        # Needed to store data "permanently"
        
        user = request.form["nm"]
        password = request.form["pw"]
        session["user"] = user
        session["password"] = password
        flash("Login Succesful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/secret_code")
def secretCode():
    if "user" in session:
        flash(f"Your secret code is {session['password']}")
        return render_template("secret_code.html")
    else:
        flash("No secret code yet. You need to log in first!")
        return redirect(url_for("login"))

@app.route("/hash_code")
def hashCode():
    if "user" in session:
        password = session["password"]
        saltedHash, salt = saltHash(password)
        session["salt"] = salt
        session["saltedHash"] = saltedHash
        flash(f"After salt-hashing: {saltedHash}")
        return render_template("secret_code.html")
    else:
        flash("You need to log in first.")
        return redirect(url_for("login"))

@app.route("/check_hash")
def checkSaltHash():
    if "user" in session:
        recreatedHash = getHash(session["password"].encode("utf-8") + session["salt"])
        if session["saltedHash"] != recreatedHash:
            flash("The hashes do NOT match :(")
        else:
            flash("The hashes match :)")
            flash(f"Recreated hash: {recreatedHash}")
        return render_template("secret_code.html")
    return redirect(url_for("login"))
        
def saltHash(password):
    salt = getSalt()
    salted = password.encode("utf-8") + salt
    return getHash(salted), salt

def getSalt(n = 32):
    if n < 32:
        return os.urandom(32)
    return os.urandom(n)
    
def getHash(saltedString):
    return hashlib.sha256(saltedString).hexdigest()
