from flask import Flask, redirect, url_for, render_template, request, session, flash
import requests

from os import urandom
# Method to generate a string of size random bytes suitable for cryptographic use

from datetime import timedelta
# For storing data for permanent sessions


import Server

app = Flask(__name__)

app.secret_key = urandom(24)
# In Flask, the secret key is used to sign session cookies cryptographically, ensuring data integrity and preventing tampering.

app.permanent_session_lifetime = timedelta(minutes=5)
# Store the permanent session data for 5 minutes (other options: minutes, days, seconds, etc)

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
        response = requests.post("https://katieehsong.pythonanywhere.com/receive_data", json=data)
        return response.text
    except requests.exceptions.RequestException:
        return " :( "

def requestKeyChange():
    data = {
        "Server Name": "Basebook",
        "Message": "Hello from Web Server to the Key Server",
        "Request Type": "Key Change",
        "Input": None
        }
    try:
        response = requests.post("https://katieehsong.pythonanywhere.com/receive_data", json=data)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pw"]
        if not server.validData(user, password):
            flash("Please make sure your username and password are valid.")
        elif server.addUser(user, password):
            f = requestData(server.computeOutput(user, password))
            flash(f"Received: {f}")
            server.addF(user, f)
            flash("Sign Up Succesful! Please log in.")
            return redirect(url_for("login"))
        else:
            flash("Sign Up Failed...")
        return redirect(url_for("signup"))
    else:
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
        return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        # Needed to store data "permanently"

        user = request.form["nm"]
        password = request.form["pw"]

        if not server.validData(user, password):
            flash("Please make sure your username and password are valid.")
        elif not server.existName(user):
            flash("The username does not exist.")
        else:
            f = requestData(server.computeOutput(user, password))
            flash(f"Received: {f}")
            if server.userLogin(user, f):
                session["user"] = user
                session["password"] = password
                flash("Login Succesful!")
            else:
                flash("Login failed")
                flash(f"{server.users[user]['F_Output']}")
                flash(f"{server.dummyReverseF(f)}")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))
        return render_template("login.html", data=server.users)

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        flash("You have been logged out!", "info")
        session.pop("user", None)
    else:
        flash("You are not logged in.")
    return redirect(url_for("login"))

@app.route("/secret_code")
def secretCode():
    if "user" in session:
        name = session["user"]
        password = session['password']
        flash(f"Username:\n\t{name}")
        flash(f"Password:\n\t{password}")
        salt = bytes.fromhex(server.users[name]['Salt'])
        flash(f"H(pw || salt):\n\t{server.getHash(password.encode('utf-8') + salt)}")
        flash(f"H(pw || salt)^r:\n\t{server.computeOutput(name, password)}")
        flash(f"H(pw || salt)^k:\n\t{server.users[name]['F_Output']}")
        return render_template("secret_code.html")
    else:
        flash("You need to log in first!")
        return redirect(url_for("login"))

@app.route("/r_update")
def updateR():
    if "user" in session:
        name = session["user"]
        password = session['password']
        flash(f"Username:\n\t{name}")
        flash(f"H(pw || salt)^r:\n\t{server.computeOutput(name, password)}")
        flash(f"H(pw || salt)^k:\n\t{server.users[name]['F_Output']}")
        for each in server.users.keys():
            if each != name:
                flash(f"Username:\t{each}")
                flash(f"H(pw || salt)^k:\t{server.users[each]['F_Output']}")
        flag = server.updateR()
        if flag:
            flash("--------------------------- After R change ---------------------------")
            flash(f"Username:\n\t{name}")
            flash(f"H(pw || salt)^r':\n\t{server.computeOutput(name, password)}")
            flash(f"H(pw || salt)^k:\n\t{server.users[name]['F_Output']}")
            for each in server.users.keys():
                if each != name:
                    flash(f"Username:\t{each}")
                    flash(f"H(pw || salt)^k:\t{server.users[each]['F_Output']}")

        return render_template("secret_code.html")
    else:
        flash("You need to log in first.")
        return redirect(url_for("login"))

'''
@app.route("/k_update")
def updateK():
    if "user" in session:
        name = session["user"]
        password = session['password']
        flash(f"Username:\n\t{name}")
        flash(f"H(pw || salt)^r:\n\t{server.computeOutput(name, password)}")
        flash(f"H(pw || salt)^k:\n\t{server.users[name]['F_Output']}")
        for each in server.users.keys():
            if each != name:
                flash(f"Username:\t{each}")
                flash(f"H(pw || salt)^k:\t{server.users[each]['F_Output']}")
        flag = requestKeyChange() and server.updateF()
        if flag:
            flash("--------------------------- After K change ---------------------------")
            flash(f"Username:\n\t{name}")
            flash(f"H(pw || salt)^r:\n\t{server.computeOutput(name, password)}")
            flash(f"H(pw || salt)^k':\n\t{server.users[name]['F_Output']}")
            for each in server.users.keys():
                if each != name:
                    flash(f"Username:\t{each}")
                    flash(f"H(pw || salt)^k':\t{server.users[each]['F_Output']}")

        return render_template("secret_code.html")
    else:
        flash("You need to log in first.")
        return redirect(url_for("login"))
'''