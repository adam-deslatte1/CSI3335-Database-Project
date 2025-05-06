import pymysql
import json  # ← Add this

from questions import QUESTIONS

mysql = {
    'location': '127.0.0.1',
    'user': 'root',
    'password': 'cybears',
    'database': 'baseball'
}

conn = pymysql.connect(
    host=mysql['location'],
    user=mysql['user'],
    password=mysql['password'],
    database=mysql['database'],
    charset='utf8mb4'
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
