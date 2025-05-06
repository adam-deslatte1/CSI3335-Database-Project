from sqlalchemy import create_engine, text
import random

# === SQLAlchemy Setup ===
engine = create_engine("mysql+pymysql://root:cybears@127.0.0.1/baseball")


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
    if difficulty == "easy":
        query = "SELECT yearID FROM teams WHERE WSWin = 'Y' AND yearID >= YEAR(CURDATE()) - 20 ORDER BY RAND() LIMIT 1"
    elif difficulty == "medium":
        query = "SELECT yearID FROM teams WHERE WSWin = 'Y' AND yearID >= YEAR(CURDATE()) - 40 ORDER BY RAND() LIMIT 1"
    else:
        query = "SELECT yearID FROM teams WHERE WSWin = 'Y' ORDER BY RAND() LIMIT 1"
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
        return f"{result[0]} {result[1]}" if result else None


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
