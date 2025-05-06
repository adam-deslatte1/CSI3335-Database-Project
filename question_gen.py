import json
import random
from sqlalchemy import create_engine, text
import importlib
from csi3335s2025 import mysql

# === Load fetch functions ===
fetch = importlib.import_module("fetch")

# === SQLAlchemy setup ===
engine = create_engine(f"mysql+mysqlconnector://{mysql['user']}:{mysql['password']}@{mysql['location']}/{mysql['database']}")


def get_question_by_id(qid):
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT * FROM trivia_questions WHERE id = :qid"
        ), {'qid': qid}).mappings().first()
        return dict(row) if row else None


def run_fetchers(fetchers):
    values = {}

    for fn_name in fetchers:
        fetch_fn = getattr(fetch, fn_name)
        result = None

        # Try multiple times in case of None results
        for _ in range(10):
            result = fetch_fn()
            if result:
                break

        if not result:
            print(f"⚠️ Failed to fetch value for {fn_name}")
            continue

        if fn_name in ["fetch_year", "fetch_year_with_ws", "fetch_year_recent"]:
            values["year"] = result

        elif fn_name == "fetch_team_name":
            values["team_name"] = result

        elif fn_name == "fetch_team_city":
            values["city"] = result

        elif fn_name in ["fetch_team_state", "fetch_multi_team_state"]:
            values["state"] = result

        elif fn_name == "fetch_hof_first_name":
            values["nameFirst"] = result

        elif fn_name == "fetch_hof_last_name":
            values["nameLast"] = result

        elif fn_name == "fetch_full_hof_name":
            try:
                first, last = result.strip().split(" ", 1)
                values["nameFirst"] = first
                values["nameLast"] = last
            except ValueError:
                print(f"⚠️ Invalid full name format: {result}")
                continue

        elif fn_name == "fetch_rank":
            values["rank"] = result

        else:
            key = fn_name.replace("fetch_", "")
            values[key] = result

    return values


def fill_placeholders(template, values):
    return template.format(**values)


def run_sql(sql_template, values):
    try:
        query = fill_placeholders(sql_template, values)
    except KeyError as e:
        print(f"⚠️ Missing key for SQL formatting: {e}")
        return [], None

    with engine.connect() as conn:
        return conn.execute(text(query)).scalars().all(), query


def generate_question_by_id(qid):
    q = get_question_by_id(qid)
    if not q:
        return {"valid": False, "reason": f"No question with ID {qid}"}

    fetchers = json.loads(q["fetchers"]) if q["fetchers"] else []
    max_retries = 5
    values = {}

    for _ in range(max_retries):
        values = run_fetchers(fetchers)

        try:
            template = fill_placeholders(q["template"], values)

            correct_answers, correct_sql = run_sql(q["sql_template"], values)
            wrong_answers, wrong_sql = run_sql(q["wrong_sql_template"], values)

            if not correct_answers or not wrong_answers:
                continue

            all_answers = list(set(correct_answers + wrong_answers))
            if len(all_answers) < 4:
                continue

            return {
                "valid": True,
                "id": qid,
                "question": template,
                "correct": correct_answers[0],
                "options": random.sample(all_answers, k=4)
            }

        except Exception as e:
            continue

    # Print debug info on failure
    try:
        template = fill_placeholders(q["template"], values)
    except Exception:
        template = q["template"]

    print(f"\n❌ [ID {qid}] {template.strip()}")
    print("  ✗ Failed after retries")
    print("\n--- Template ---")
    print(q["template"])

    print("\n--- Correct Answer SQL ---")
    try:
        print(fill_placeholders(q["sql_template"], values))
    except Exception as e:
        print(f"⚠️ Could not format correct SQL: {e}")

    print("\n--- Wrong Answers SQL ---")
    try:
        print(fill_placeholders(q["wrong_sql_template"], values))
    except Exception as e:
        print(f"⚠️ Could not format wrong SQL: {e}")

    print("\n--- Values Used ---")
    print(json.dumps(values, indent=2))

    return {
        "valid": False,
        "id": qid,
        "reason": "Failed after retries",
        "template": template,
        "values": values,
        "sql": q["sql_template"],
        "wrong_sql": q["wrong_sql_template"]
    }


# === MAIN LOOP ===
if __name__ == "__main__":
    with engine.connect() as conn:
        ids = [row[0] for row in conn.execute(text("SELECT id FROM trivia_questions")).fetchall()]

    for qid in ids:
        result = generate_question_by_id(qid)

        if result["valid"]:
            print(f"✅ [ID {result['id']}]")
