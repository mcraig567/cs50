import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    holdings = db.execute("SELECT symbol, amount FROM stocks WHERE stocks.user_id = :userid AND amount != 0", userid = session["user_id"])
    total = 0

    for row in holdings:
        sDict = lookup(row['symbol'])
        row['name'] = sDict['name']
        row['share_total'] = sDict['price'] * row['amount']
        total += row['share_total']

        row['price'] = usd(sDict['price'])
        row['share_total'] = usd(row['share_total'])

    cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid = session["user_id"])
    cash = cash[0]["cash"]
    total += cash

    return render_template("index.html", holdings=holdings, cash=usd(cash), total=usd(total))

#    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        #Get symbol & number to buy - ok
        #Get price - ok
        #Ensure user can afford to buy - ok
        #Remove cash from user table - ok
        #Add row to stocks table - ok
        #Add row to history table - ok

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Pick a company")

        if not shares:
            return apology("Pick a number > 0")
        elif int(shares) < 1:
            return apology("sneaky")
        else:
            shares = int(shares)


        sDict = lookup(symbol)
        row = db.execute("SELECT cash FROM users WHERE id = :userid", userid = session["user_id"])

        if not sDict:
            return apology("Invalid Symbol")

        if shares * sDict["price"] > row[0]["cash"]:
            return apology("You broke, son")

        #Calculate remaining cash and update users table
        rmcash = row[0]["cash"] - shares * sDict["price"]
        db.execute("UPDATE users SET cash = :cash WHERE id = :userid", cash = rmcash, userid = session["user_id"])

        #Update stocks table with new holding
        curStock = db.execute("SELECT amount FROM stocks WHERE user_id = :userid AND symbol = :symbol", userid=session["user_id"], symbol=sDict["symbol"])

        if len(curStock) == 0:
            db.execute("INSERT INTO stocks (user_id, symbol, amount) VALUES (:userid, :symbol, :amount)", userid=session["user_id"], symbol=sDict["symbol"], amount=shares)

        else:
            db.execute("UPDATE stocks SET amount = :amount WHERE user_id = :userid and symbol = :symbol", amount=curStock[0]["amount"]+shares, userid=session["user_id"], symbol=sDict["symbol"])

        """Update history table with transaction"""
        time = datetime.now()
        db.execute("INSERT INTO history(user_id, symbol, amount, price, date) VALUES (:user_id, :symbol, :amount, :price, :date)",
        user_id=session["user_id"], symbol=sDict["symbol"], price=sDict["price"], amount=shares, date=time)

        flash("Bought!")
        return redirect('/')

    return apology("Unknown Error")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    #Get users history (no amount = 0)
    #Prepare table

    rows = db.execute("SELECT * from history WHERE user_id = :userid AND amount != 0", userid = session["user_id"])
    for row in rows:
        row['price'] = usd(row['price'])

    return render_template("history.html", history=rows)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Missing Symbol")

        #Look up name and price of symbol - returns None if doesn't exist
        symbol_dict = lookup(symbol)

        if not symbol_dict:
            return apology("Invalid Symbol")

        return render_template("symbol.html", name=symbol_dict["name"], symbol=symbol_dict["symbol"], cost=symbol_dict["price"])


    return apology("Unknown Error")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("name")
        password = request.form.get("password")
        passconf = request.form.get("passconf")
        rows = db.execute("SELECT username FROM users WHERE username = :username", username=name)

        #Look for possible issues
        if len(rows) == 1:
            return apology("This username is already taken")
        if password != passconf:
            return apology("Your passwords don't match")
        if not password:
            return apology("No password entered")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (:name, :hash)", name=name, hash=hash)

        return redirect('/')

    return apology("Unknown Error")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        #Get companies that user has stocks in
        symbols = db.execute("SELECT symbol FROM stocks WHERE user_id = :userid AND amount != 0", userid = session["user_id"])

        return render_template("sell.html", symbols=symbols)

    else:
        #get stock symbol and amount to sell - ok
        #check that user has enough stock - ok
        #get current value for stock and add value*amount to users.cash - ok
        #Update stocks table - ok
        #Update history table - ok

        #Get values from user
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Pick a company")

        if not shares:
            return apology("Gotta sell something")
        elif int(shares) < 1:
            return apology("sneaky")
        else:
            shares = int(shares)

        #Ensure that the user has enough stock to sell
        stocks = db.execute("SELECT amount from stocks WHERE user_id = :userid AND symbol = :symbol", userid = session["user_id"], symbol = symbol)
        stocks = stocks[0]["amount"]

        if shares > stocks:
            return apology ("You don't own that many")

        #Get value for stock and update tables
        sDict = lookup(symbol)

        #Update user's cash
        newCash = sDict['price'] * shares
        cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid = session["user_id"])
        cash = cash[0]["cash"] + newCash
        db.execute("UPDATE users SET cash = :cash WHERE id = :userid", cash=cash, userid = session["user_id"])

        #Update user's stocks
        stocks = stocks - shares
        db.execute("UPDATE stocks SET amount = :amount WHERE user_id = :userid AND symbol = :symbol", amount = stocks, userid = session["user_id"], symbol = symbol)

        #Update user's history
        time = datetime.now()
        db.execute("INSERT INTO history(user_id, symbol, amount, price, date) VALUES (:user_id, :symbol, :amount, :price, :date)",
        user_id=session["user_id"], symbol=sDict["symbol"], price=sDict["price"], amount=shares*-1, date=time)

        flash("Sold!")
        return redirect('/')

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add money to a user's account"""
    if request.method == "GET":
        return render_template("add.html")
    else:
        #Get amount to add from user
        cashAdd = request.form.get("amount")

        #Check for issues
        if not cashAdd:
            return apology("Cheap")
        elif float(cashAdd) <= 0:
            return apology("sneaky")
        else:
            cashAdd = float(cashAdd)

        #Get user's existing cash
        cash = db.execute("SELECT cash FROM users WHERE id = :userid", userid = session["user_id"])[0]["cash"]

        #Update user's cash
        db.execute("UPDATE users SET cash = :cash WHERE id = :userid", userid = session["user_id"], cash = cash+  cashAdd)

        return redirect('/')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
