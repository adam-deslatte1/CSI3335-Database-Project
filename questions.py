#Force Commit by adding a change

QUESTIONS = [
    {
        "difficulty": "easy",
        "template": 'What is the last name of the Hall of Fame player named {nameFirst}?',
        "fetchers": ["fetch_hof_first_name"],
        "sql_template": '''
SELECT nameLast FROM people
            WHERE nameFirst = '{nameFirst}'
              AND playerID IN (
                  SELECT playerID FROM halloffame WHERE inducted = 'Y'
              )
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT nameLast FROM people
            WHERE nameFirst != '{nameFirst}'
              AND playerID IN (
                  SELECT playerID FROM halloffame WHERE inducted = 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'What is the first name of the Hall of Fame player with last name {nameLast}?',
        "fetchers": ["fetch_hof_last_name"],
        "sql_template": '''
SELECT nameFirst FROM people
            WHERE nameLast = '{nameLast}'
              AND playerID IN (
                  SELECT playerID FROM halloffame WHERE inducted = 'Y'
              )
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT nameFirst FROM people
            WHERE nameLast != '{nameLast}'
              AND playerID IN (
                  SELECT playerID FROM halloffame WHERE inducted = 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which Hall of Fame player shares a last name with {nameLast}?',
        "fetchers": ["fetch_hof_last_name"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM people
            WHERE nameLast = '{nameLast}'
              AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT CONCAT(nameFirst, ' ', nameLast) FROM people
            WHERE nameLast != '{nameLast}'
              AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which Hall of Fame player was born in the same state as {nameFirst} {nameLast}?',
        "fetchers": ["fetch_full_hof_name"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM people
WHERE birthState = (
    SELECT birthState FROM people
    WHERE nameFirst = '{nameFirst}' AND nameLast = '{nameLast}' AND birthState IS NOT NULL
)
AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT CONCAT(nameFirst, ' ', nameLast) FROM people
WHERE birthState NOT IN (
    SELECT birthState FROM people
    WHERE nameFirst = '{nameFirst}' AND nameLast = '{nameLast}' AND birthState IS NOT NULL
)
AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which of these first names belongs to a Hall of Fame player?',
        "fetchers": ["fetch_hof_first_name"],
        "sql_template": '''
SELECT nameFirst FROM people
            WHERE nameFirst = '{nameFirst}'
              AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT nameFirst FROM people
            WHERE nameFirst != '{nameFirst}'
              AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which of these last names belongs to a Hall of Fame player?',
        "fetchers": ["fetch_hof_last_name"],
        "sql_template": '''
SELECT nameLast FROM people
            WHERE nameLast = '{nameLast}'
              AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT nameLast FROM people
            WHERE nameLast != '{nameLast}'
              AND playerID IN (SELECT playerID FROM halloffame WHERE inducted = 'Y')
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team has the most World Series wins of all time?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
WHERE franchID = (
    SELECT franchID FROM teams
    WHERE WSWin = 'Y'
    GROUP BY franchID
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
AND team_name IS NOT NULL
GROUP BY team_name
ORDER BY COUNT(*) DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
WHERE WSWin = 'Y'
  AND franchID != (
    SELECT franchID FROM teams
    WHERE WSWin = 'Y'
    GROUP BY franchID
    ORDER BY COUNT(*) DESC
    LIMIT 1
  )
  AND team_name IS NOT NULL
GROUP BY team_name
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team has the fewest World Series wins (among teams that have won)?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y'
            GROUP BY team_name
            ORDER BY COUNT(*) ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y'
            GROUP BY team_name
            HAVING COUNT(*) > 1
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team won the World Series most recently?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y'
            ORDER BY yearID DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT team_name FROM teams
            WHERE WSWin = 'Y'
              AND yearID < (SELECT MAX(yearID) FROM teams WHERE WSWin = 'Y')
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team has won the most World Series titles since 2005?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y' AND yearID >= 2005
            GROUP BY team_name
            ORDER BY COUNT(*) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y' AND yearID >= 2005
            GROUP BY team_name
            HAVING COUNT(*) < (
                SELECT COUNT(*) FROM teams
                WHERE WSWin = 'Y' AND yearID >= 2005
                GROUP BY team_name
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": "Which team hasn't won a World Series in the past 20 years?",
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE team_name NOT IN (
                SELECT DISTINCT team_name FROM teams
                WHERE WSWin = 'Y' AND yearID >= YEAR(CURDATE()) - 20
            )
            AND team_name IS NOT NULL
            GROUP BY team_name
            ORDER BY RAND()
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE team_name IN (
                SELECT DISTINCT team_name FROM teams
                WHERE WSWin = 'Y' AND yearID >= YEAR(CURDATE()) - 20
            )
            GROUP BY team_name
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team won the World Series in {year}?',
        "fetchers": ["fetch_year_with_ws"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y' AND yearID = {year}
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year}
              AND WSWin != 'Y'
              AND team_name IS NOT NULL
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team has the most World Series **appearances** since 1990?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID >= 1990 AND WSWin = 'Y'
            GROUP BY team_name
            ORDER BY COUNT(*) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID >= 1990 AND WSWin = 'Y'
            GROUP BY team_name
            HAVING COUNT(*) < (
                SELECT COUNT(*) FROM teams
                WHERE WSWin = 'Y' AND yearID >= 1990
                GROUP BY team_name
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which of these teams has **never** won a World Series?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE team_name NOT IN (
                SELECT DISTINCT team_name FROM teams WHERE WSWin = 'Y'
            )
            AND team_name IS NOT NULL
            GROUP BY team_name
            ORDER BY RAND()
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT team_name FROM teams
            WHERE WSWin = 'Y'
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team has the most World Series **losses** on record?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'N'
            GROUP BY team_name
            ORDER BY COUNT(*) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'N'
            GROUP BY team_name
            HAVING COUNT(*) < (
                SELECT COUNT(*) FROM teams
                WHERE WSWin = 'N'
                GROUP BY team_name
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team has only won a single World Series title?',
        "fetchers": [],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y'
            GROUP BY team_name
            HAVING COUNT(*) = 1
            ORDER BY RAND()
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE WSWin = 'Y'
            GROUP BY team_name
            HAVING COUNT(*) > 1
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which park did the {team_name} play in during {year}?',
        "fetchers": ["fetch_team_name", "fetch_year_recent"],
        "sql_template": '''
SELECT park_name FROM teams
            WHERE team_name = '{team_name}' AND yearID = {year} AND yearID >= 2005
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT DISTINCT park_name FROM teams
            WHERE team_name != '{team_name}' AND park_name IS NOT NULL AND yearID = {year} AND yearID >= 2005
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "easy",
        "template": 'Which team hit the most home runs in {year}?',
        "fetchers": ["fetch_year_recent"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 2005
            ORDER BY team_HR DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 2005
              AND team_HR < (
                  SELECT MAX(team_HR) FROM teams WHERE yearID = {year} AND yearID >= 2005
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most wins but did not win the World Series in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND WSWin != 'Y'
            ORDER BY team_W DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND WSWin != 'Y'
              AND team_W < (
                  SELECT MAX(team_W) FROM teams
                  WHERE yearID = {year} AND yearID >= 1985 AND WSWin != 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the best ERA in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_ERA IS NOT NULL
            ORDER BY team_ERA ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_ERA IS NOT NULL
              AND team_ERA > (
                  SELECT MIN(team_ERA) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team hit the most home runs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_HR DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_HR < (
                  SELECT MAX(team_HR) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the lowest fielding percentage in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_FP IS NOT NULL
            ORDER BY team_FP ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_FP IS NOT NULL
              AND team_FP > (
                  SELECT MIN(team_FP) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the highest run differential in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY (team_R - team_RA) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND (team_R - team_RA) < (
                  SELECT MAX(team_R - team_RA) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most stolen bases in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_SB DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_SB < (
                  SELECT MAX(team_SB) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": "Which team had the most home runs but didn't make the playoffs in {year}?",
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
            ORDER BY team_HR DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
              AND team_HR < (
                  SELECT MAX(team_HR) FROM teams
                  WHERE yearID = {year} AND yearID >= 1985
                    AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the best strikeout-to-walk ratio in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND team_BB > 0
            ORDER BY (team_SO / team_BB) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND team_BB > 0
              AND (team_SO / team_BB) < (
                  SELECT MAX(team_SO / team_BB)
                  FROM teams
                  WHERE yearID = {year} AND yearID >= 1985 AND team_BB > 0
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team gave up the fewest home runs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_HRA ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_HRA > (
                  SELECT MIN(team_HRA) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team walked the most batters in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_BBA DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_BBA < (
                  SELECT MAX(team_BBA) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most complete games in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_CG DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_CG < (
                  SELECT MAX(team_CG) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team committed the fewest errors in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_E ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_E > (
                  SELECT MIN(team_E) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the best winning percentage in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_G > 0
            ORDER BY (team_W / team_G) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_G > 0
              AND (team_W / team_G) < (
                  SELECT MAX(team_W / team_G) FROM teams WHERE yearID = {year} AND yearID >= 1985 AND team_G > 0
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the fewest strikeouts at the plate in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_SO ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_SO > (
                  SELECT MIN(team_SO) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team gave up the most home runs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_HRA DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_HRA < (
                  SELECT MAX(team_HRA) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the fewest double plays in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_DP ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_DP > (
                  SELECT MIN(team_DP) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most complete games but still missed the playoffs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
            ORDER BY team_CG DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
              AND team_CG < (
                  SELECT MAX(team_CG) FROM teams
                  WHERE yearID = {year} AND yearID >= 1985
                    AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most intentional walks in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_BB DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_BB < (
                  SELECT MAX(team_BB) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most double plays turned in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_DP DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_DP < (
                  SELECT MAX(team_DP) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the highest win total but did not win their division in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND DivWin != 'Y'
            ORDER BY team_W DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND DivWin != 'Y'
              AND team_W < (
                  SELECT MAX(team_W) FROM teams
                  WHERE yearID = {year} AND yearID >= 1985 AND DivWin != 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team hit into the most double plays in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_DP DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_DP < (
                  SELECT MAX(team_DP) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the highest batting average (H/AB) in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND team_AB > 0
            ORDER BY (team_H / team_AB) DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND team_AB > 0
              AND (team_H / team_AB) < (
                  SELECT MAX(team_H / team_AB) FROM teams
                  WHERE yearID = {year} AND yearID >= 1985 AND team_AB > 0
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the most walks in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_BB DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_BB < (
                  SELECT MAX(team_BB) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the lowest on-base plus slugging factor (BPF + PPF) in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_BPF IS NOT NULL AND team_PPF IS NOT NULL
            ORDER BY (team_BPF + team_PPF) ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_BPF IS NOT NULL AND team_PPF IS NOT NULL
              AND (team_BPF + team_PPF) > (
                  SELECT MIN(team_BPF + team_PPF)
                  FROM teams
                  WHERE yearID = {year} AND yearID >= 1985
                    AND team_BPF IS NOT NULL AND team_PPF IS NOT NULL
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team allowed the fewest home runs per game in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND team_G > 0
            ORDER BY (team_HRA / team_G) ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985 AND team_G > 0
              AND (team_HRA / team_G) > (
                  SELECT MIN(team_HRA / team_G) FROM teams
                  WHERE yearID = {year} AND yearID >= 1985 AND team_G > 0
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Which team had the fewest games played at home in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
            ORDER BY team_G_home ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND yearID >= 1985
              AND team_G_home > (
                  SELECT MIN(team_G_home) FROM teams WHERE yearID = {year} AND yearID >= 1985
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who was the all-time home run leader at the end of {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_HR) AS total_HR
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_HR DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_HR) AS total_HR
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_HR DESC
            LIMIT 10
        ) AS top10
        WHERE total_HR < (
            SELECT MAX(total_HR) FROM (
                SELECT SUM(b_HR) AS total_HR FROM batting
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most RBIs in MLB history through {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_RBI) AS total_RBI
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_RBI DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_RBI) AS total_RBI
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_RBI DESC
            LIMIT 10
        ) AS top10
        WHERE total_RBI < (
            SELECT MAX(total_RBI) FROM (
                SELECT SUM(b_RBI) AS total_RBI FROM batting
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most career hits in MLB history as of {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_H) AS total_hits
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_hits DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_H) AS total_hits
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_hits DESC
            LIMIT 10
        ) AS top10
        WHERE total_hits < (
            SELECT MAX(total_hits) FROM (
                SELECT SUM(b_H) AS total_hits FROM batting
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who walked the most times in MLB history by {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_BB) AS total_bb
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_bb DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_BB) AS total_bb
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_bb DESC
            LIMIT 10
        ) AS top10
        WHERE total_bb < (
            SELECT MAX(total_bb) FROM (
                SELECT SUM(b_BB) AS total_bb FROM batting
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who stole the most bases in MLB history through {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_SB) AS total_sb
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_sb DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(b_SB) AS total_sb
            FROM batting
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_sb DESC
            LIMIT 10
        ) AS top10
        WHERE total_sb < (
            SELECT MAX(total_sb) FROM (
                SELECT SUM(b_SB) AS total_sb FROM batting
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most career strikeouts as a pitcher by the end of {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_SO) AS total_so
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_so DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_SO) AS total_so
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_so DESC
            LIMIT 10
        ) AS top10
        WHERE total_so < (
            SELECT MAX(total_so) FROM (
                SELECT SUM(p_SO) AS total_so FROM pitching
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most complete games in MLB history by {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_CG) AS total_cg
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_cg DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_CG) AS total_cg
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_cg DESC
            LIMIT 10
        ) AS top10
        WHERE total_cg < (
            SELECT MAX(total_cg) FROM (
                SELECT SUM(p_CG) AS total_cg FROM pitching
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most saves in MLB history as of {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_SV) AS total_sv
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_sv DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_SV) AS total_sv
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_sv DESC
            LIMIT 10
        ) AS top10
        WHERE total_sv < (
            SELECT MAX(total_sv) FROM (
                SELECT SUM(p_SV) AS total_sv FROM pitching
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most pitching wins in MLB history through {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_W) AS total_w
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_w DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_W) AS total_w
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_w DESC
            LIMIT 10
        ) AS top10
        WHERE total_w < (
            SELECT MAX(total_w) FROM (
                SELECT SUM(p_W) AS total_w FROM pitching
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "medium",
        "template": 'Who had the most pitching losses in MLB history by {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_L) AS total_l
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_l DESC
            LIMIT 1
        ) AS leader
''',
        "wrong_sql_template": '''
SELECT playerID FROM (
            SELECT playerID, SUM(p_L) AS total_l
            FROM pitching
            WHERE yearID <= {year}
            GROUP BY playerID
            ORDER BY total_l DESC
            LIMIT 10
        ) AS top10
        WHERE total_l < (
            SELECT MAX(total_l) FROM (
                SELECT SUM(p_L) AS total_l FROM pitching
                WHERE yearID <= {year}
                GROUP BY playerID
            ) AS totals
        )
        ORDER BY RAND()
        LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the lowest ERA but finished with a losing record in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND team_W < team_L AND team_ERA IS NOT NULL
            ORDER BY team_ERA ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND team_W < team_L AND team_ERA IS NOT NULL
              AND team_ERA > (
                  SELECT MIN(team_ERA) FROM teams WHERE yearID = {year} AND team_W < team_L
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team gave up the most runs but still made the playoffs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year}
              AND (DivWin = 'Y' OR WCWin = 'Y' OR LgWin = 'Y')
            ORDER BY team_RA DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year}
              AND (DivWin = 'Y' OR WCWin = 'Y' OR LgWin = 'Y')
              AND team_RA < (
                  SELECT MAX(team_RA) FROM teams
                  WHERE yearID = {year}
                    AND (DivWin = 'Y' OR WCWin = 'Y' OR LgWin = 'Y')
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the lowest batting average (H/AB) but still won the World Series in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
WHERE yearID = {year} AND WSWin = 'Y' AND team_AB > 0
ORDER BY (team_H / team_AB) ASC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
WHERE yearID = {year} AND WSWin != 'Y' AND team_AB > 0
ORDER BY (team_H / team_AB) DESC
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the highest win total and did not make the postseason in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
            ORDER BY team_W DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year}
              AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
              AND team_W < (
                  SELECT MAX(team_W) FROM teams
                  WHERE yearID = {year}
                    AND WCWin != 'Y' AND DivWin != 'Y' AND LgWin != 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the most home runs but failed to make the World Series in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND LgWin != 'Y' AND team_HR IS NOT NULL
            ORDER BY team_HR DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND LgWin != 'Y' AND team_HR IS NOT NULL
              AND team_HR < (
                  SELECT MAX(team_HR) FROM teams WHERE yearID = {year} AND LgWin != 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the lowest winning percentage but still won their division in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND DivWin = 'Y' AND team_G > 0
            ORDER BY (team_W / team_G) ASC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND DivWin = 'Y' AND team_G > 0
              AND (team_W / team_G) > (
                  SELECT MIN(team_W / team_G) FROM teams
                  WHERE yearID = {year} AND DivWin = 'Y' AND team_G > 0
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the most losses and still won the Wild Card in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND WCWin = 'Y'
            ORDER BY team_L DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND WCWin = 'Y'
              AND team_L < (
                  SELECT MAX(team_L) FROM teams WHERE yearID = {year} AND WCWin = 'Y'
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team had the highest team ERA and still made it to the League Championship?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
WHERE yearID = {year} AND LgWin = 'Y'
ORDER BY team_ERA DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
WHERE yearID = {year}
  AND LgWin != 'Y'
  AND team_ERA IS NOT NULL
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which team led the league in errors but still had a winning record in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND team_W > team_L
            ORDER BY team_E DESC
            LIMIT 1
''',
        "wrong_sql_template": '''
SELECT team_name FROM teams
            WHERE yearID = {year} AND team_W > team_L
              AND team_E < (
                  SELECT MAX(team_E) FROM teams WHERE yearID = {year} AND team_W > team_L
              )
            ORDER BY RAND()
            LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player hit the most home runs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year}
ORDER BY b_HR DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_HR < (
    SELECT MAX(b_HR) FROM batting WHERE yearId = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player had the highest batting average in {year} (min 400 AB)?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_AB >= 400
ORDER BY (b_H / b_AB) DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_AB >= 400
  AND (b_H / b_AB) < (
    SELECT MAX(b_H / b_AB) FROM batting WHERE yearId = {year} AND b_AB >= 400
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which pitcher had the most strikeouts in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM pitching
JOIN people ON pitching.playerID = people.playerID
WHERE yearID = {year}
ORDER BY p_SO DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM pitching
JOIN people ON pitching.playerID = people.playerID
WHERE yearID = {year} AND p_SO < (
    SELECT MAX(p_SO) FROM pitching WHERE yearID = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player had the most stolen bases in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year}
ORDER BY b_SB DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_SB < (
    SELECT MAX(b_SB) FROM batting WHERE yearId = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which pitcher had the lowest ERA in {year} (min 100 IP)?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM pitching
JOIN people ON pitching.playerID = people.playerID
WHERE yearID = {year} AND p_IPOuts >= 300
ORDER BY p_ERA ASC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM pitching
JOIN people ON pitching.playerID = people.playerID
WHERE yearID = {year} AND p_IPOuts >= 300 AND p_ERA > (
    SELECT MIN(p_ERA) FROM pitching WHERE yearID = {year} AND p_IPOuts >= 300
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player had the most RBIs in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year}
ORDER BY b_RBI DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_RBI < (
    SELECT MAX(b_RBI) FROM batting WHERE yearId = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player drew the most walks in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year}
ORDER BY b_BB DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_BB < (
    SELECT MAX(b_BB) FROM batting WHERE yearId = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which pitcher had the most shutouts in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM pitching
JOIN people ON pitching.playerID = people.playerID
WHERE yearID = {year}
ORDER BY p_SHO DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM pitching
JOIN people ON pitching.playerID = people.playerID
WHERE yearID = {year} AND p_SHO < (
    SELECT MAX(p_SHO) FROM pitching WHERE yearID = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player led the league in strikeouts at the plate in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year}
ORDER BY b_SO DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_SO < (
    SELECT MAX(b_SO) FROM batting WHERE yearId = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
    {
        "difficulty": "hard",
        "template": 'Which player had the most sacrifice flies in {year}?',
        "fetchers": ["fetch_year"],
        "sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year}
ORDER BY b_SF DESC
LIMIT 1
''',
        "wrong_sql_template": '''
SELECT CONCAT(nameFirst, ' ', nameLast) FROM batting
JOIN people ON batting.playerID = people.playerID
WHERE yearId = {year} AND b_SF < (
    SELECT MAX(b_SF) FROM batting WHERE yearId = {year}
)
ORDER BY RAND()
LIMIT 3
'''
    },
]
