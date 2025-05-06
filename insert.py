import mysql.connector
import json
from csi3335s2025 import mysql as mysql_config

from questions import QUESTIONS

conn = mysql.connector.connect(
    host=mysql_config['location'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database']
)
cur = conn.cursor()

for q in QUESTIONS:
    cur.execute("""
        INSERT INTO app_trivia_questions (difficulty, template, fetchers, sql_template, wrong_sql_template)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        q["difficulty"],
        q["template"],
        json.dumps(q["fetchers"]) if q["fetchers"] is not None else None,  # ← fixed here
        q["sql_template"],
        q["wrong_sql_template"]
    ))

conn.commit()
cur.close()
conn.close()
