from flask import Flask, render_template, request, redirect, url_for, session
from tempfile import mkdtemp
from flask_session import Session
import os
from random import randint
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import datetime

app = Flask(__name__)

# Auto reload .html and .css files without resetting the website
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Flask app key for basic requirement
app.secret_key = os.environ["FLASK_SKEY"]

# Cookie settings
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Config for file
app.config['UPLOAD_FOLDER'] = "/home/runner/pikitup/files/"
app.config['MAX_CONTENT_PATH'] = 5000000


# Return error function
def error(name, code=400):
    return render_template("error.html", name=name, code=code)


# DB Connection
connection = sqlite3.connect("data.db", check_same_thread=False)
cursor = connection.cursor()


def loggedIn(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email"):
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


def needLogin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("email"):
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


# TRASH LIST
plastics = [
    [
        "Plastic Bottle", 2000,
        "Any plastic bottle, with or without cap. Worth 2000 coins per kilogram",
        "/static/assets/img/plasticbottle.jpg"
    ],
    [
        "Plastic Glass", 3000,
        "One time use plastic glasses. Worth 3000 coins per kilogram",
        "/static/assets/img/plasticglass.jpg"
    ],
    [
        "Plastic Bucket", 1000,
        "Any type of buckets that is made out of plastic. Worth 1000 coins per kilogram",
        "/static/assets/img/plasticbucket.jpg"
    ],
    [
        "Plastic Bag", 250,
        "Plastic trash bags etc. Worth 250 coins per kilogram",
        "/static/assets/img/plasticbag.jpg"
    ],
    [
        "Other Plastic", 1000,
        "Other type of plastics that is excluded from the list. Worth ~1000 coins per kilogram (Depends on what plastic it is)",
        "/static/assets/img/plasticmisc.jpg"
    ]
]

papers = [
    [
        "Opaque Paper", 1000,
        "Opaque papers that usually used for math scrabbling on schools. Worth 1000 coins per kilogram",
        "/static/assets/img/paperopaque.jpg"
    ],
    [
        "HVS Paper", 1500,
        "Used white HVS paper, preferably A4 sized. Worth 1500 coins per kilogram",
        "/static/assets/img/paperhvs.jpg"
    ],
    [
        "Magazine", 1000,
        "Old magazines to be recycled. Worth 1000 coins per kilogram",
        "/static/assets/img/papermagazine.jpg"
    ],
    [
        "Newspaper", 2000,
        "Newspapers that is currently unused. Worth 2000 coins per kilogram",
        "/static/assets/img/papernewspaper.jpg"
    ],
    [
        "Old Book", 1500,
        "Books to be recycled, new empty books worth more. Worth 1500 per kilogram",
        "/static/assets/img/paperbook.jpg"
    ],
    [
        "Cardboard", 1700,
        "Cardboards that is in a decent condition. Worth 1700 per kilogram",
        "/static/assets/img/papercardboard.jpg"
    ]
]

metals = [
    [
        "Aluminum Can", 9000,
        "Aluminum cans to be recycled and in a decent condition. Worth 9000 per kilogram",
        "/static/assets/img/metalaluminumcan.jpg"
    ],
    [
        "Can", 500,
        "Old cans that is both in good or bad condition. Worth 500 per kilogram",
        "/static/assets/img/metalcan.jpg"
    ],
    [
        "Brass", 18000,
        "Recyclable brass to be recycled as another brass item. Worth 18000 per kilogram",
        "/static/assets/img/metalbrass.jpg"
    ],
    [
        "Iron Sheeting", 300,
        "Iron sheeting from building scraps. Worth 300 per kilogram",
        "/static/assets/img/metalironsheeting.jpg"
    ],
    [
        "Other Metal", 5000,
        "Other kinds of metal that is not in the list. Worth ~5000 coins per kilogram (Depends on what metal it is)"
    ]
]

others = [
    [
        "Battery", 4000,
        "Any kind of old or used batteries. Worth 4000 coins per kilogram",
        "/static/assets/img/otherbattery.jpg"
    ],
    [
        "Diapers", 1500, "Used diapers. Worth 1500 per kilogram",
        "/static/assets/img/otherdiaper.jpg"
    ],
    [
        "Phone", 13000,
        "Old broken phone that is still decently intact. Worth 13000 coins per kilogram",
        "/static/assets/img/otherphone.jpg"
    ],
    [
        "Other Electronic", 6000,
        "Other electronics that is not in the list. Worth ~6000 per kilogram (Depends on what type of electronic it is)",
        "/static/assets/img/otherelectronic.jpg"
    ]
]


# Home page
@app.route("/")
def home():
    if session.get("email"):
        print(session.get("bag"))

        # Get arguments from URL if it sends an add to bag command
        amount = request.args.get('a')
        if amount:
            amount = int(amount)
            if amount % 50 != 0:
                return error("Trash amounts must be the multiple of 50")
        trash = request.args.get('t')

        all = plastics + papers + metals + others

        # If amount and trash arguments actually have values
        if amount and trash:

            # In case arguments sent is manually inputted
            exists = False
            for i in all:
                if trash in i:
                    exists = True
                    coins = i[1]
                    coins /= 1000
                    coins *= amount
                    coins = int(coins)
                    img = i[3]
                else:
                    pass
            if exists == False:
                return error("Trash item doesn't exists in list")

            # Get current user's bag
            currentSession = session.get("bag")
            # If bag is never touched, set an empty array
            if not currentSession:
                currentSession = []

            # Iterate through their bag
            for i in range(len(currentSession)):
                # If the trash name already exists in their bag
                if trash in currentSession[i]:
                    # Add amount to the existing array
                    currentSession[i][1] += amount
                    session["bag"] = currentSession
                    return redirect(url_for("home"))

            # If there is no trash name exists in the bag
            # Add trash data
            listToAdd = []
            listToAdd.append(trash)
            listToAdd.append(amount)
            listToAdd.append(coins)
            listToAdd.append(img)
            currentSession.append(listToAdd)

            session["bag"] = currentSession
            return redirect(url_for("home"))

        qry = cursor.execute("SELECT * FROM users WHERE email = ?",
                             [session.get("email")])
        qry = qry.fetchall()
        fullname = qry[0][1]
        coins = qry[0][3]

        all = plastics + papers + metals + others

        allLen = len(all)
        plasticsLen = len(plastics)
        papersLen = len(papers)
        metalsLen = len(metals)
        othersLen = len(others)

        return render_template("index.html",
                               fullname=fullname,
                               coins=coins,
                               all=all,
                               plastics=plastics,
                               papers=papers,
                               metals=metals,
                               others=others,
                               allLen=allLen,
                               plasticsLen=plasticsLen,
                               papersLen=papersLen,
                               metalsLen=metalsLen,
                               othersLen=othersLen)
    else:
        return redirect(url_for("register"))


@app.route("/register/", methods=["GET", "POST"])
@loggedIn
def register():
    if request.method == "POST":
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?",
                       [request.form.get("email")])
        emailExists = cursor.fetchall()
        emailExists = emailExists[0][0]

        if request.form.get("password") != request.form.get("confirm"):
            return error("Password and confirmation does not match")

        if not request.form.get("email"):
            return error("Email section is empty")

        elif not request.form.get("password"):
            return error("Password section is empty")

        elif not request.form.get("confirm"):
            return error("Password confirmation section is empty")

        elif not request.form.get("fullname"):
            return error("Fullname section is empty")

        elif not request.form.get("username"):
            return error("Username section is empty")

        hash = generate_password_hash(request.form.get("password"))

        cursor.execute(
            "INSERT INTO users (email, username, fullname, password, coins) VALUES (?, ?, ?, ?, ?)",
            [
                request.form.get("email"),
                request.form.get("username"),
                request.form.get("fullname"), hash, 0
            ])
        connection.commit()

        session["email"] = request.form.get("email")

        return redirect(url_for("home"))
    else:
        return render_template("logister.html")


@app.route("/login/", methods=["GET", "POST"])
@loggedIn
def login():
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("password")

        qry = cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?",
                             [email])
        qry = qry.fetchall()
        qry = qry[0][0]

        if qry != 1:
            return error("Email and/or password is incorrect")

        qry = cursor.execute("SELECT password FROM users WHERE email = ?",
                             [email])
        qry = qry.fetchall()
        qry = qry[0][0]

        if not check_password_hash(qry, pwd):
            return error("Email and/or password is incorrect")

        session["email"] = email

        return redirect(url_for("home"))
    else:
        return render_template("logister.html")


@app.route("/logout/")
@loggedIn
def logout():
    session.clear()
    return redirect(url_for("login"))


# MyBag page
@app.route("/mybag/")
@needLogin
def mybag():
    bag = session.get("bag")
    if not bag:
        bag = []
    baglen = len(bag)

    item = request.args.get("removebutton")

    if item:
        for i in bag:
            if item in i:
                bag.pop(bag.index(i))
                return redirect(url_for("mybag"))

        return error("Item is not in bag")

    amount = 0
    coins = 0

    for i in bag:
        amount += i[1]
        coins += i[2]

    final = f"{str(amount)} Grams"

    if amount >= 1000:
        amount /= 1000
        final = f"{str(amount)} Kgs"

    amount = round(amount, 1)
    return render_template("bag.html",
                           bag=bag,
                           baglen=baglen,
                           amount=final,
                           coins=coins)


# Order page
@app.route("/order/", methods=["GET", "POST"])
@needLogin
def order():
    if request.method == "POST":
        f = request.files['trashphoto']
        filename = os.path.join(app.config['UPLOAD_FOLDER'],
                                secure_filename(f.filename))

        addr = request.form.get("pickupaddress")
        tipAmt = request.form.get("driverstip")
        tipPayMethod = request.form.get("paymentmethod")

        timeNow = datetime.datetime.now()
        timeNow = timeNow.strftime("%d-%b-%y-%H:%M")

        bag = session.get("bag")

        qry = cursor.execute("SELECT coins FROM users WHERE email = ?",
                             [session.get("email")])
        qry = cursor.fetchall()
        currentCoins = qry[0][0]

        # If bag is empty, do not iterate
        if bag is not None:
            for i in bag:
                cursor.execute(
                    "INSERT INTO history (type, amount, time, email, coinsworth) VALUES (?, ?, ?, ?, ?)",
                    [i[0], i[1], timeNow,
                     session.get("email"), i[2]])
                connection.commit()
                currentCoins += i[2]

        cursor.execute(
            "INSERT INTO pickup (email, address, tipamt, method, filedir, status) VALUES (?, ?, ?, ?, ?, ?)",
            [
                session.get("email"), addr, tipAmt, tipPayMethod, filename,
                "On Verification"
            ])
        connection.commit()

        # ntar kalo orderannya belom diverifikasi, mending jangan ditambah dulu coinsnya le
        cursor.execute("UPDATE users SET coins = ? WHERE email = ?",
                       [currentCoins, session.get("email")])
        connection.commit()

        session.pop("bag")

        return redirect(url_for("mybag"))
    else:
        bag = session.get("bag")
        if not bag:
            bag = []
        baglen = len(bag)

        item = request.args.get("removebutton")

        if item:
            for i in bag:
                if item in i:
                    bag.pop(bag.index(i))
                    return redirect(url_for("order"))

            return error("Item is not in bag")

        amount = 0
        coins = 0

        for i in bag:
            amount += i[1]
            coins += i[2]

        final = f"{str(amount)} Grams"

        if amount >= 1000:
            amount /= 1000
            final = f"{str(amount)} Kgs"

        amount = round(amount, 1)
        return render_template("order.html",
                               bag=bag,
                               baglen=baglen,
                               amount=final,
                               coins=coins)


# History page
@app.route("/history/")
@needLogin
def history():
    qry = cursor.execute("SELECT * FROM users WHERE email = ?",
                         [session.get("email")])
    qry = qry.fetchall()
    fullname = qry[0][1]
    coins = qry[0][3]
    return render_template("history.html", fullname=fullname, coins=coins)


# MyCoins page
@app.route("/mycoins/")
@needLogin
def mycoins():
    qry = cursor.execute("SELECT * FROM users WHERE email = ?",
                         [session.get("email")])
    qry = qry.fetchall()
    fullname = qry[0][1]
    coins = qry[0][3]
    return render_template("coins.html", fullname=fullname, coins=coins)


# Settings page
@app.route("/settings/")
@needLogin
def settings():
    qry = cursor.execute("SELECT * FROM users WHERE email = ?",
                         [session.get("email")])
    qry = qry.fetchall()
    fullname = qry[0][1]
    coins = qry[0][3]
    return render_template("settings.html", fullname=fullname, coins=coins)


# Error handler function
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)


# If error occured, call the error handler function
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# Run
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=randint(2000, 9000))
