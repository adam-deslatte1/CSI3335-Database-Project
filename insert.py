import mysql.connector
import json
from csi3335s2025 import mysql

from questions import QUESTIONS

conn = mysql.connector.connect(
    host=mysql['location'],
    user=mysql['user'],
    password=mysql['password'],
    database=mysql['database']
)
cur = conn.cursor()

for q in QUESTIONS:
    cur.execute("""
        INSERT INTO trivia_questions (difficulty, template, fetchers, sql_template, wrong_sql_template)
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
