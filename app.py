import os
import random

from flask import Flask, flash, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, create_database, generate_teams

# The basic app framework reuses some elements from the solution to cs50's "finance" problem set to provide its login functionality

if not os.path.exists("database.db"):
    create_database()

db = SQL("sqlite:///database.db")

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    """Redirect to team generator as default"""
    return redirect("/teams")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Clear session
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please fill all fields")
            return redirect("/login", code=400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please fill all fields")
            return redirect("/login", code=400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return redirect("/login", code=400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Clear session
    session.clear()

    # Redirect user to login
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please fill all fields")
            return redirect("/register", code=400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please fill all fields")
            return redirect("/register", code=400)

        # check for username and ensure it is not taken yet

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(rows) > 0:
            flash("Username is already taken")
            return redirect("/register", code=400)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match")
            return redirect("/register", code=400)

        # Save new user
        hash = generate_password_hash(request.form.get("password"))
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            hash,
        )
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change password"""

    # User reached route via POST
    if request.method == "POST":

        user_id = session["user_id"]

        # Ensure all password fields where submitted
        if not (
            request.form.get("old_password")
            and request.form.get("password")
            and request.form.get("confirmation")
        ):
            flash("All fields must be filled")
            return redirect("/password", code=400)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match", code=400)
            return redirect("/password")

        # Query database for user_id
        rows = db.execute("SELECT * FROM users WHERE id=?", user_id)

        # Ensure old password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            flash("Invalid username and/or password")
            return redirect("/password", code=400)

        # Change password in database
        hash = generate_password_hash(request.form.get("password"))
        db.execute("UPDATE users SET hash=? WHERE id=?", hash, user_id)

        flash("Password changed")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("password.html")

@app.route("/ideas", methods=["GET", "POST"])
@login_required
def ideas():

    # User reached route via POST so add, delete or reset ideas
    if request.method == "POST":
        data = request.json

        # Delete an idea from the database
        if data["function"] == "delete":
            db.execute("DELETE FROM votes WHERE idea_id = ?;", data["id"])
            db.execute("DELETE FROM ideas WHERE id = ?;", data["id"])

        # Add a new idea to the database
        elif data["function"] == "add":
            if data["text"]:
                user_id = session["user_id"]
                db.execute("INSERT INTO ideas (user_id, text) VALUES (?, ?);", user_id, data["text"])

        # Reset the database by deleting everything from the votes and idea tables
        elif data["function"] == "reset":
                db.execute("DELETE FROM votes;")
                db.execute("DELETE FROM ideas;")
        return redirect("/ideas")

    # User reached route via GET so show all ideas from the database
    else:
        ideas = []
        ideas_count = 0
        rows = db.execute("SELECT ideas.id, text, username FROM ideas JOIN users ON ideas.user_id = users.id;")
        for idea in rows:
            ideas.append({
                "id": idea["id"],
                "text": idea["text"],
                "creator": idea["username"]
            })
            ideas_count += 1
        return render_template("ideas.html", ideas=ideas, ideas_count=ideas_count)

@app.route("/teams", methods=["GET", "POST"])
@login_required
def teams():

    # User reached route via POST and the submit button
    if request.method == "POST" and request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        if not session.get("participants"):
            flash("Please add at least one participant")
            return redirect("/teams", code=400)

        # Check if the number of teams data is valid
        try:
            number_of_teams = int(request.form.get("number_of_teams"))
            if number_of_teams < 1:
                raise ValueError
        except (ValueError, TypeError):
            flash("Please enter a positive number of teams")
            return render_template("teams.html", users=session["participants"])

        # Generate the teams via a helper function and convert it to a list
        teams_dict = generate_teams(session["participants"], number_of_teams)
        teams = [value for (key, value) in teams_dict.items()]
        return render_template("teams_output.html", teams=teams)

    # User reached route via POST and the update_participants function
    elif request.method == "POST" and request.headers.get("Content-Type") == "application/json":
        try:
            data = request.json
        except TypeError:
            return "Failure", 400

        # update the participants stored in session
        session["participants"] = data["participants"]
        return "Success", 200

    # User reached route via GET
    else:

        # Get users from database of there are no participants stored in session
        if not session.get("participants"):
            users = []
            rows = db.execute("SELECT username FROM users")
            for user in rows:
                users.append(user["username"])
            session["participants"] = sorted(users)
        participants = session["participants"]

        # Display participants/users in table
        return render_template("teams.html", users=participants)

@app.route("/vote", methods=["GET", "POST"])
@login_required
def vote():

    # User reached route via GET
    if request.method == "GET":
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM ideas WHERE id NOT IN (SELECT idea_id FROM votes WHERE votes.user_id = ?);", user_id)

        # Check if user voted for all ideas already
        if not rows:
            flash("You voted on all available ideas")
            return redirect("/ideas")
        if len(rows) == 1:
            remaining = "No more ideas remaining"
        elif len(rows) == 2:
            remaining = "One more idea remaining"
        else:
            remaining = str(len(rows) - 1) + " more ideas remaining"
        # Show user a random idea he did not vote on yet
        return render_template("vote.html", idea=random.choice(rows), remaining=remaining)

    # User reached route via POST so vote is processed
    else:
        data = request.json

        # Check if vote is valid
        if data["vote"] in [0, 1]:
            vote = data["vote"]
            idea_id = data["id"]
            user_id = session["user_id"]

            # Save vote to database
            db.execute("INSERT INTO votes (idea_id, user_id, vote) VALUES (?, ?, ?);", idea_id, user_id, vote)

        # Redirect to vote page
        return redirect("/vote")

@app.route("/voting_results")
@login_required
def voting_results():
    rows = db.execute("SELECT idea_id, text, SUM(vote) AS votes FROM votes JOIN ideas ON votes.idea_id = ideas.id GROUP BY idea_id ORDER BY votes DESC;")
    if not rows:
        flash("No votes yet")
        return redirect("/ideas")
    return render_template("results.html", ideas=rows)
