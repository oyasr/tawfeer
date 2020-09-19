from cs50 import SQL
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import apology, login_required

# Create flask app instance
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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to database
db = SQL('sqlite:///tawfeer.db')


@app.route('/')
@login_required
def index():
    return apology('TODO', 400)

@app.route('/logout')
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # Method is POST
    if request.method == 'POST':

        # Ensure username was submitted
        if not request.form.get('username'):
            return apology('Missing a username?', 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology('Missing a password?', 403)

        # Query database for username
        rows = db.execute("""
            SELECT * FROM users 
            WHERE username = :username;
            """, username=request.form.get('username'))

        # Ensure username exists and password is correct
        password = request.form.get('password')
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], password):
            return apology('Invalid username and/or password.', 403)

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # Redirect user to home page
        return redirect('/')
    
    # Method is GET
    else:
        return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # Method is POST
    if request.method == 'POST':

        # Get username, password & cash
        username = request.form.get('username')
        password = request.form.get('password')
        password_again = request.form.get('password-again')
        cash = request.form.get('cash')

        # Ensure user submitted a name
        if not username:
            return apology('Missing a username?', 400)

        # Ensure user submitted matching passwords
        if not password or password != password_again:
            return apology('Submit matching passwords.', 400)

        # Check if username is unique
        row = db.execute("""
            SELECT COUNT(*) AS count 
            FROM users 
            WHERE username = :username;
            """, username=username)

        # Username taken
        if row[0]["count"] > 0:
            return apology("Username already taken.", 400)

        # Generate password hash
        password_hash = generate_password_hash(password)

        # Add user to database
        if not cash:
            db.execute("""
                INSERT INTO users (username, hash)
                VALUES (:username, :hash);
                """, username=username, hash=password_hash)
        else:
            db.execute("""
                INSERT INTO users (username, hash, cash)
                VALUES (:username, :hash, :cash);
                """, username=username, hash=password_hash, cash=cash)

        # Get user id
        user_id = db.execute("""
            SELECT id FROM users 
            WHERE username = :username;
            """, username=username)

        # Remember which user has logged in
        session["user_id"] = user_id[0]["id"]

        # Flash message
        #flash("Registered successfully!")

        # Redirect user to home page
        return redirect("/")

    # Method is GET
    else:
        return render_template("register.html")