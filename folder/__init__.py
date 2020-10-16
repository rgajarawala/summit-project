import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
import json
import smtplib
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

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


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///summit.db")

def getApp():
    return app


@app.route("/home")
def home():
    """Renders homepage"""
    return render_template("home.html")


@app.route("/")
@login_required
def index():
    """Displays all lists of goals"""

    # Selects each of the lists of todos and goals to display
    academics = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id",
                           list_id=2, user_id=session["user_id"])
    health = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id",
                        list_id=3, user_id=session["user_id"])
    sociallife = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id",
                            list_id=4, user_id=session["user_id"])
    extracurriculars = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id",
                                  list_id=5, user_id=session["user_id"])
    goals = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id", list_id=1, user_id=session["user_id"])

    return render_template("index.html", academics=academics, health=health, sociallife=sociallife, extracurriculars=extracurriculars, goals=goals)


@app.route("/addindex", methods=["POST", "GET"])
@login_required
def addindex():
    """Adds items to lists from index page"""

    # Receives todo from user input
    newitem = request.form.get("todoitem")

    # Receives priority level from user selection
    priority = request.form.get("priority")

    # Receives list from user selection
    list_id = request.form.get("list_id")

    # If input is not received, flash message error
    if not newitem:
        flash("Please input a task", category="danger")
        return redirect("/#message")
    if not priority:
        flash("Please select a priority", category="danger")
        return redirect("/#message")

    # Insert new todo item into appropriate list
    db.execute("INSERT INTO summit (user_id, list_id, task, complete, priority) VALUES(:user_id, :list_id, :task, :complete, :priority)",
               user_id=session["user_id"], list_id=list_id, task=newitem, complete=False, priority=priority)
    return redirect("/")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    # Select any usernames from users table that are the same username as the inputted one
    result = db.execute("SELECT username FROM users WHERE username=:username", username=username)
    # If there a duplicate usernames, return false. If not, return true
    if result:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registers user"""

    if request.method == "POST":
        username = request.form.get("username")

        # Check if username field has a value
        if not username:
            flash("Please input a username", category="danger")
            return redirect("/register#message")

        # Check if password field has a value
        elif not request.form.get("password") or not request.form.get("confirmation"):
            flash("Please input a password", category="danger")
            return redirect("/register#message")

        # Check if password field equals confirmation field
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Please ensure both passwords match", category="danger")
            return redirect("/register#message")

        # Hash the inputted password for security
        hash = generate_password_hash(request.form.get("password"))

        # Insert a new row of username and hash into the users table
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                            username=username, hash=hash)

        flash("You've successfully registered with username: " + username, category="success")
        # Set unique indicator that the user is logged in and has an account
        session["user_id"] = result

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please input your username", category="danger")
            return redirect("/login#message")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please input your password", category="danger")
            return redirect("/login#message")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Please input a valid username and/or password", category="danger")
            return redirect("/login#message")

        flash("You've successfully logged in!", category="success")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/profile")
@login_required
def profile():
    # Display username, id
    username = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
    # Redirect user to profile form
    return render_template("profile.html", username=username)


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if username field has a value
        if not request.form.get("username"):
            flash("Please input your username", category="danger")
            return redirect("/profile#message")

        # Check if password field has a value
        elif not request.form.get("password"):
            flash("Please input your password", category="danger")
            return redirect("/profile#message")

        # Check if new password field has a value
        elif not request.form.get("newpassword"):
            flash("Please input your new password", category="danger")
            return redirect("/profile#message")

        # Check if confirmation password field has a value
        elif not request.form.get("confirmation"):
            flash("Please input your new password again", category="danger")
            return redirect("/profile#message")

        # Check if new password and confirmation password are equal
        elif request.form.get("newpassword") != request.form.get("confirmation"):
            flash("Your new password does not equal your confirmation", category="danger")
            return redirect("/profile#message")

        # Update hash in users table to hash of new password
        db.execute("UPDATE users SET hash = :hash WHERE id=:id AND username=:username",
                   id=session["user_id"], hash=generate_password_hash(request.form.get("newpassword")),
                   username=request.form.get("username"))

        flash("You have changed your password!", category="success")

        return redirect("/profile")


@app.route("/passwordcheck", methods=["GET"])
def passcheck():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")

    # Select any usernames from users table that are the same username as the inputted one
    result = db.execute("SELECT username FROM users WHERE username = :username", username=username)

    # If the inputted username is in the table, return true. If not, return false.
    if result:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/email", methods=["POST"])
def email():
    """Creates database of emails for newsletter"""

    # Recieve user input for email
    email = request.form.get("email")

    # Input into newsletter table
    db.execute("INSERT INTO newsletter (email) VALUES (:email)", email=email)

    # Error handling for no inputted email
    if not email:
        flash("Please input an email", category="danger")
        return redirect("/#message")

    # Display successful message
    message = "You are registered for our newsletter! Excited to have you on board. Please stay tuned for upcoming information"

    # Connects to SMTP
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    # Logs into email
    server.login("cs50summit@gmail.com", os.getenv("davidmalan"))

    # Sends email through server
    server.send_message("cs50summit@gmail.com", email, message)
    server.quit()

    return render_template("/")


@app.route("/list/1")
@login_required
def goals():
    """Generates list of goals"""

    # Select all todos for goals
    goals = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id", list_id=1, user_id=session["user_id"])

    return render_template("goals.html", goals=goals)


@app.route('/list/<list_id>')
@login_required
def list(list_id):
    """Generates list of todos"""

    # Make list_id an integer
    list_id = int(list_id)

    # Selects todos under the list_id
    todos = db.execute("SELECT * FROM summit WHERE list_id=:list_id AND user_id=:user_id",
                       list_id=list_id, user_id=session["user_id"])

    # Select appropriate listname
    listname = db.execute("SELECT listname from lists WHERE list_id=:list_id", list_id=list_id)

    return render_template("list.html", todos=todos, listname=listname, list_id=list_id)


@app.route('/add/<id>', methods=['POST'])
def add(id):
    """Adds new item to todo list"""

    # Receive input and priority level from user
    newitem = request.form.get("todoitem")
    priority = request.form.get("priority")

    # If not input is received, flash message error
    if not newitem:
        flash("Please input a task", category="danger")

    # Insert new todo item into appropriate list
    db.execute("INSERT INTO summit (user_id, list_id, task, complete, priority) VALUES(:user_id, :list_id, :task, :complete, :priority)",
               user_id=session["user_id"], list_id=int(id), task=newitem, complete=False, priority=priority)

    # Display success message
    flash("You've successfully added a task!", category="success")

    return redirect("/list/" + id + "#message")


@app.route('/delete/<id>')
def delete(id):
    """Deletes items from list"""

    task_id = int(id)

    # Deletes selected todo with appropriate task id
    todo = db.execute("SELECT list_id FROM summit WHERE task_id=:task_id AND user_id=:user_id",
                      task_id=task_id, user_id=session["user_id"])
    db.execute("DELETE FROM summit WHERE task_id=:task_id AND user_id=:user_id", task_id=task_id, user_id=session["user_id"])

    # Display success message
    flash("You've successfully deleted this task!", category="success")

    return redirect("/list/" + str(todo[0]["list_id"]) + "#message")


@app.route('/complete/<id>')
def complete(id):
    """Marks todos as complete"""

    task_id = int(id)

    # Check if task is currently completed
    current = db.execute("SELECT complete FROM summit WHERE task_id=:task_id AND user_id=:user_id",
                         task_id=task_id, user_id=session["user_id"])

    # If task is not currently completed, set it as completed and display success message
    if current[0]["complete"] == False:
        db.execute("UPDATE summit SET complete=:complete WHERE task_id=:task_id AND user_id=:user_id",
                   complete=True, task_id=task_id, user_id=session["user_id"])
        flash("You've completed your task!", category="success")

    # If is task is already completed, revert completion
    else:
        db.execute("UPDATE summit SET complete=:complete WHERE task_id=:task_id AND user_id=:user_id",
                   complete=False, task_id=task_id, user_id=session["user_id"])
    todo = db.execute("SELECT list_id FROM summit WHERE task_id=:task_id", task_id=task_id)

    return redirect("/list/" + str(todo[0]["list_id"]) + "#message")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    flash("You've successfully logged out!", category="success")

    # Redirect user to login form
    return redirect("/#logout")


# run Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)