from sqlalchemy import create_engine, text
import random
from csi3335s2025 import mysql
from flask import flash, redirect, url_for
import json

# === SQLAlchemy Setup ===
engine = create_engine(f"mysql+mysqlconnector://{mysql['user']}:{mysql['password']}@{mysql['location']}/{mysql['database']}")


# === Helper ===
def fetch_one(query):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.scalar()


# === Retry wrapper ===
def try_fetch(query, retries=5):
    for _ in range(retries):
        val = fetch_one(query)
        if val:
            return val
    return None


# === Fetch Functions ===

# Year-based (difficulty-aware)
def fetch_year(difficulty="easy"):
    if difficulty == "easy":
        query = "SELECT yearID FROM teams WHERE yearID >= YEAR(CURDATE()) - 20 ORDER BY RAND() LIMIT 1"
    elif difficulty == "medium":
        query = "SELECT yearID FROM teams WHERE yearID >= YEAR(CURDATE()) - 40 ORDER BY RAND() LIMIT 1"
    else:
        query = "SELECT yearID FROM teams ORDER BY RAND() LIMIT 1"
    return try_fetch(query)

def fetch_year_with_ws(difficulty="easy"):
    # Only select years that actually exist in the data with WSWin = 'Y'
    query = """
        SELECT yearID FROM teams
        WHERE WSWin = 'Y'
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_year_recent(difficulty="easy"):
    return fetch_year(difficulty)


# Random rank integer
def fetch_rank():
    return random.randint(1, 5)


# Hall of Fame name fetchers (using people table)
def fetch_hof_first_name():
    query = """
        SELECT p.nameFirst FROM people p
        JOIN halloffame h ON p.playerID = h.playerID
        WHERE h.inducted = 'Y' AND p.nameFirst IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_hof_last_name():
    query = """
        SELECT p.nameLast FROM people p
        JOIN halloffame h ON p.playerID = h.playerID
        WHERE h.inducted = 'Y' AND p.nameLast IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_full_hof_name():
    query = """
        SELECT p.nameFirst, p.nameLast FROM people p
        JOIN halloffame h ON p.playerID = h.playerID
        WHERE h.inducted = 'Y'
        ORDER BY RAND() LIMIT 1
    """
    with engine.connect() as conn:
        result = conn.execute(text(query)).first()
        return (result[0], result[1]) if result else (None, None)


# Team and location fetchers
def fetch_team_name():
    query = """
        SELECT DISTINCT team_name FROM teams
        WHERE team_name IS NOT NULL AND yearID >= 2000
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_team_city():
    query = """
        SELECT DISTINCT city FROM teams
        WHERE city IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_team_state():
    query = """
        SELECT DISTINCT state FROM teams
        WHERE state IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_multi_team_state():
    query = """
        SELECT state FROM teams
        GROUP BY state
        HAVING COUNT(DISTINCT name) > 1
        ORDER BY RAND() LIMIT 1
    """
    return try_fetch(query)

def fetch_year_with_wc():
    query = """
        SELECT DISTINCT yearID FROM teams
        WHERE WCWin = 'Y' AND yearID >= 1995
        ORDER BY RAND()
        LIMIT 1
    """
    return try_fetch(query)

FETCHER_MAP = {
    "fetch_year": fetch_year,
    "fetch_hof_first_name": fetch_hof_first_name,
    "fetch_hof_last_name": fetch_hof_last_name,
    "fetch_full_hof_name": fetch_full_hof_name,
    "fetch_team_name": fetch_team_name,
    "fetch_team_city": fetch_team_city,
    "fetch_team_state": fetch_team_state,
    "fetch_multi_team_state": fetch_multi_team_state,
    "fetch_year_with_ws": fetch_year_with_ws,
    "fetch_year_recent": fetch_year_recent,
    "fetch_rank": fetch_rank,
}
