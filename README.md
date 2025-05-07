# CSI3335-Database-Project
Baseball-themed trivia game

How to run:

**Create virtual environment**

For Windows:
```bash
python -m venv project_env
```
For MacOS:
```bash
python3 -m venv project_env
```



**Activate venv**

For Windows:
```bash
.\project_env\Scripts\activate
```
For MacOS:
```bash
source project_env/bin/activate
```



**Install the dependencies**
```bash
pip install -r requirements.txt
```



**Edit Database Credentials as Needed**
```bash
edit csi3335s2025.py as needed
```



**Import the New Table Changes**
Create a new table to house the trivia questions called app_trivia_questions
```bash
CREATE TABLE app_trivia_questions ( id INT AUTO_INCREMENT PRIMARY KEY, difficulty VARCHAR(20), template TEXT, fetchers TEXT, sql_template TEXT, wrong_sql_template TEXT);
```



**Then import relevant tables**

For Windows:
```bash
python insert.py
python import_no_hitters.py
```
For MacOS:
```bash
python3 insert.py
python3 import_no_hitters.py
```



**To run the project**
```bash
export FLASK_APP=app.py
export PYTHONPATH=.
flask run
```



**Admin Account Login Info:**
```bash
user: admin
pass: admin123
```