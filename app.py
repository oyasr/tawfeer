from cs50 import SQL
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session
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
    return '<h1>Hello, World!</h1>'

@app.route("/login", methods=["GET", "POST"])
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
            return apology('invalid username and/or password', 403)

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']

        # Redirect user to home page
        return redirect('/')
    
    # Method is GET
    else:
        return render_template("login.html")