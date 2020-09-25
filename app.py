from cs50 import SQL
import json
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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """User's home page"""

    # Get user id & cash
    user_id = session['user_id']
    cash = db.execute("""
        SELECT cash FROM users
        WHERE id = :id;
    """, id=user_id)[0]['cash']

    # Method is POST
    if request.method == 'POST':

        # Get month
        month = request.form.get('month')

        # Ensure a month was submitted
        if not month:
            return apology('Missing a month?', 400)

        # Get month name
        month_name = datetime(2020, int(month), 1).strftime('%B')
        month_name.capitalize()

        # Fromat month
        if month not in ('10', '11', '12'):
            month = '0' + month

        # Get month total
        spent = db.execute("""
            SELECT SUM(t.price) AS sum
            FROM transactions t
            JOIN bridge b
            ON b.id = t.bridge_id
            AND b.user_id = :id 
            AND strftime('%m', t.occurred_at) = :month
        """, id=user_id, month=month)[0]['sum']

        # Get remaining cash
        if not spent:
            remain, spent = cash, 0
        else:
            remain = cash - spent

        # Get listings by month
        rows = db.execute("""
            SELECT c.name category, 
            t.description description,
            t.price price, 
            strftime('%d/%m/%Y' ,t.occurred_at) date
            FROM categories c
            JOIN bridge b
            ON c.id = b.category_id 
            AND user_id = :id
            JOIN transactions t
            ON b.id = t.bridge_id
            AND strftime('%m', t.occurred_at) = :month
            ORDER BY t.occurred_at DESC, c.name DESC;
        """, id=user_id, month=month)

        return render_template('index.html',
                               spent=spent, remain=remain, rows=rows, month=month_name)

    # Method is GET
    else:

        # Get current month total
        spent = db.execute("""
            SELECT SUM(t.price) AS sum
            FROM transactions t
            JOIN bridge b
            ON b.id = t.bridge_id
            AND b.user_id = :id 
            AND strftime('%m', t.occurred_at) 
            = strftime('%m', date('now'));
        """, id=user_id)[0]['sum']

        # Get remaining cash
        if not spent:
            remain, spent = cash, 0
        else:
            remain = cash - spent

        # Get current month transactions
        rows = db.execute("""
            SELECT c.name category, 
            t.description description,
            t.price price, 
            strftime('%d/%m/%Y' ,t.occurred_at) date
            FROM categories c
            JOIN bridge b
            ON c.id = b.category_id 
            AND user_id = :id
            JOIN transactions t
            ON b.id = t.bridge_id
            AND strftime('%m', t.occurred_at) 
            = strftime('%m', date('now'))
            ORDER BY t.occurred_at DESC, c.name DESC;
        """, id=user_id)

        return render_template('index.html',
                               spent=spent, remain=remain, rows=rows)


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


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a transaction"""

    # Get user id
    user_id = session['user_id']

    # Method is POST
    if request.method == 'POST':

        # Get form input
        category = request.form.get('category')
        new_category = request.form.get('new-category').lower().strip()
        description = request.form.get('description')
        price = request.form.get('price')

        # Ensure a category is chosen
        if not category and not new_category:
            return apology('Missing category?', 400)

        # Ensure only one category is choosen
        if category and new_category:
            return apology('Multiple categories choosen?', 400)

        # Ensure description is submitted
        if not description:
            return apology('Missing description?', 400)

        # Ensure price is submitted
        if not price:
            return apology('Missing price?', 400)

        # Existing category is choosen
        if category:

            # Get bridge id
            bridge_id = db.execute("""
                SELECT b.id id
                FROM categories c
                JOIN bridge b
                ON c.id = b.category_id
                AND c.name = :category
                AND user_id = :id;
            """, id=user_id, category=category)[0]['id']

            # Insert into transactions
            db.execute("""
                INSERT INTO transactions
                (bridge_id, description, price, occurred_at)
                VALUES (:id, :des, :price, date('now'));
            """, id=bridge_id, des=description, price=price)

        # New category is added
        else:

            # Check if new category exists
            rows = db.execute("""
                SELECT id FROM categories
                WHERE name = :name;
            """, name=new_category)

            # Category exists
            if len(rows) == 1:

                # Get category id
                category_id = rows[0]['id']

                # Insert into bridge
                db.execute("""
                    INSERT INTO bridge (user_id, category_id)
                    VALUES (:user_id, :category_id)
                """, user_id=user_id, category_id=category_id)

                # Get bridge id
                bridge_id = db.execute("""
                    SELECT id FROM bridge
                    WHERE user_id = :user_id
                    AND category_id = :category_id;
                """, user_id=user_id, category_id=category_id)[0]['id']

                # Insert into transactions
                db.execute("""
                    INSERT INTO transactions
                    (bridge_id, description, price, occurred_at)
                    VALUES (:id, :des, :price, date('now'));
                """, id=bridge_id, des=description, price=price)

            # Category doesn't exist
            else:

                # Insert into category
                db.execute("""
                    INSERT INTO categories (name)
                    VALUES (:name)
                """, name=new_category)

                # Get category id
                category_id = db.execute("""
                    SELECT id FROM categories
                    WHERE name = :name
                """, name=new_category)[0]['id']

                # Insert into bridge
                db.execute("""
                    INSERT INTO bridge (user_id, category_id)
                    VALUES (:user_id, :category_id)
                """, user_id=user_id, category_id=category_id)

                # Get bridge id
                bridge_id = db.execute("""
                    SELECT id FROM bridge
                    WHERE user_id = :user_id
                    AND category_id = :category_id;
                """, user_id=user_id, category_id=category_id)[0]['id']

                # Insert into transactions
                db.execute("""
                    INSERT INTO transactions
                    (bridge_id, description, price, occurred_at)
                    VALUES (:id, :des, :price, date('now'));
                """, id=bridge_id, des=description, price=price)

        # Redirect user to homepage
        return redirect(url_for('index'))

    # Method is GET
    else:

        # Get user's categories
        rows = db.execute("""
            SELECT c.name category
            FROM categories c
            JOIN bridge b
            ON c.id = b.category_id
            AND b.user_id = :id;
        """, id=user_id)

        return render_template('add.html', rows=rows)


@app.route('/insights')
@login_required
def insights():

    # Get user id
    user_id = session['user_id']

    # Create data list
    data = []

    # Get spendings by category
    rows = db.execute("""
        SELECT c.name category, SUM(t.price) sum
        FROM categories c
        JOIN bridge b
        ON c.id = b.category_id
        AND b.user_id = :id
        JOIN transactions t
        ON b.id = t.bridge_id
        GROUP BY 1
        ORDER BY 2 DESC;
    """, id=user_id)

    # Add to data list
    data.append([i for i in rows[0]])
    for i in range(len(rows)):
        data.append([j for j in rows[i].values()])

    return render_template('insights.html', donut_data=json.dumps(data))
