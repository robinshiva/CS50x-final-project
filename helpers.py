import sqlite3
import random

from functools import wraps
from flask import session, redirect
from cs50 import SQL

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def create_database():
    """Creates a new database if there is none"""
    con = sqlite3.connect("database.db")
    db = con.cursor()
    db.execute("CREATE TABLE 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL);")
    db.execute("CREATE TABLE 'ideas' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'user_id' INTEGER NOT NULL, 'text' TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id));")
    db.execute("CREATE TABLE 'votes' ('idea_id' INTEGER NOT NULL, 'user_id' INTEGER NOT NULL, 'vote' INTEGER NOT NULL, FOREIGN KEY (idea_id) REFERENCES ideas(id), FOREIGN KEY (user_id) REFERENCES users(id));")
    db.close()
    con.close()

def generate_teams(names, number_of_teams):
    """Generates a specified number of random teams with all provided names"""
    # create a dictionary for the teams and a list for all names that have to be allocated still
    teams = {}
    names_to_allocate = names
    # create a list in the teams dictionary for each team
    for i in range(number_of_teams):
        teams[i] = []
    # allocate names one by one until list is empty
    while names_to_allocate:
        min_team_size = min(calc_team_sizes(teams))
        random_team_pick = random.randint(0, number_of_teams - 1)
        # ensure that the picked team is not larger than the others and then allocate a random name to it
        if len(teams[random_team_pick]) == min_team_size:
            random_name_pick = random.choice(names_to_allocate)
            teams[random_team_pick].append(random_name_pick)
            names_to_allocate.remove(random_name_pick)
    return teams

def calc_team_sizes(teams):
    """Returns a list of the different team sizes"""
    team_sizes = []
    for i in teams:
        team_sizes.append(len(teams[i]))
    return team_sizes