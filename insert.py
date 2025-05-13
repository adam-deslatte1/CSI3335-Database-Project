import pymysql
import json
from csi3335s2025 import mysql as mysql_config

from questions import QUESTIONS

# Connect using PyMySQL
conn = pymysql.connect(
    host=mysql_config['location'],
    user=mysql_config['user'],
    password=mysql_config['password'],
    database=mysql_config['database'],
    charset='utf8mb4',  # Optional: supports full Unicode
    cursorclass=pymysql.cursors.Cursor  # Default, but can be set explicitly
)

cur = conn.cursor()

for q in QUESTIONS:
    cur.execute("""
        INSERT INTO app_trivia_questions (difficulty, template, fetchers, sql_template, wrong_sql_template)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        q["difficulty"],
        q["template"],
        json.dumps(q["fetchers"]) if q["fetchers"] is not None else None,
        q["sql_template"],
        q["wrong_sql_template"]
    ))

conn.commit()
cur.close()
conn.close()
