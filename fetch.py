from sqlalchemy import create_engine, text
import random

# === SQLAlchemy Setup ===
engine = create_engine("mysql+pymysql://root:cybears@127.0.0.1/baseball")

# === Helper ===
def fetch_one(query):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.scalar()

# === Fetch Functions ===

# Year-based
def fetch_year():
    return fetch_one("SELECT yearID FROM teams ORDER BY RAND() LIMIT 1")

def fetch_year_with_ws():
    return fetch_one("SELECT yearID FROM teams WHERE WSWin = 'Y' ORDER BY RAND() LIMIT 1")

def fetch_year_recent():
    return fetch_one("SELECT yearID FROM teams WHERE yearID >= 2005 ORDER BY RAND() LIMIT 1")

# Rank (random integer)
def fetch_rank():
    return random.randint(1, 5)

# Hall of Fame names
def fetch_hof_first_name():
    query = """
        SELECT p.first_name FROM player p
        JOIN halloffame h ON p.id = h.playerID
        WHERE h.inducted = 'Y' AND p.first_name IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """
    return fetch_one(query)

def fetch_hof_last_name():
    query = """
        SELECT p.last_name FROM player p
        JOIN halloffame h ON p.id = h.playerID
        WHERE h.inducted = 'Y' AND p.last_name IS NOT NULL
        ORDER BY RAND() LIMIT 1
    """
    return fetch_one(query)

def fetch_full_hof_name():
    query = """
        SELECT p.first_name, p.last_name FROM player p
        JOIN halloffame h ON p.id = h.playerID
        WHERE h.inducted = 'Y'
        ORDER BY RAND() LIMIT 1
    """
    with engine.connect() as conn:
        result = conn.execute(text(query)).first()
        return f"{result[0]} {result[1]}" if result else None

# Team and location
def fetch_team_name():
    return fetch_one("SELECT DISTINCT team_name FROM teams WHERE team_name IS NOT NULL ORDER BY RAND() LIMIT 1")

def fetch_team_city():
    return fetch_one("SELECT DISTINCT city FROM team WHERE city IS NOT NULL ORDER BY RAND() LIMIT 1")

def fetch_team_state():
    return fetch_one("SELECT DISTINCT state FROM team WHERE state IS NOT NULL ORDER BY RAND() LIMIT 1")

def fetch_multi_team_state():
    query = """
        SELECT state FROM team
        GROUP BY state
        HAVING COUNT(DISTINCT name) > 1
        ORDER BY RAND() LIMIT 1
    """
    return fetch_one(query)
