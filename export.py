import mysql.connector
from csi3335s2025 import mysql

conn = mysql.connector.connect(
    host=mysql['location'],
    user=mysql['user'],
    password=mysql['password'],
    database=mysql['database']
)
cur = conn.cursor()

cur.execute("SELECT difficulty, template, fetchers, sql_template, wrong_sql_template FROM trivia_questions")
rows = cur.fetchall()

with open("questions.py", "w", encoding="utf-8") as f:
    f.write("QUESTIONS = [\n")
    for row in rows:
        difficulty, template, fetchers, sql_template, wrong_sql_template = row

        # Sanitize string content
        fetchers_repr = fetchers if fetchers else 'None'
        sql_template = sql_template.strip().replace("'''", "\\'\\'\\'")
        wrong_sql_template = wrong_sql_template.strip().replace("'''", "\\'\\'\\'")

        f.write("    {\n")
        f.write(f"        \"difficulty\": \"{difficulty}\",\n")
        f.write(f"        \"template\": {repr(template)},\n")
        f.write(f"        \"fetchers\": {fetchers_repr},\n")
        f.write(f"        \"sql_template\": '''\n{sql_template}\n''',\n")
        f.write(f"        \"wrong_sql_template\": '''\n{wrong_sql_template}\n'''\n")
        f.write("    },\n")
    f.write("]\n")

cur.close()
conn.close()
