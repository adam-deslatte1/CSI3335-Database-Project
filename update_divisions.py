import pymysql
from csi3335s2025 import db_config
import sys

def ensure_yearid_column(cursor):
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = 'divisions' 
          AND column_name = 'yearID'
        """
    )
    if cursor.fetchone()[0] == 0:
        print("Adding yearID column to divisions table...")
        cursor.execute("ALTER TABLE divisions ADD yearID INT NOT NULL")

def update_divisions():
    try:
        # Connect to the database using pymysql
        conn = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.Cursor
        )
        cursor = conn.cursor()

        # Create divisions table if it doesn't exist (MySQL syntax)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS divisions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                yearID INT NOT NULL,
                lgID CHAR(2) NOT NULL,
                divID CHAR(1) NOT NULL,
                division_name VARCHAR(50) NOT NULL,
                division_active CHAR(1) NOT NULL,
                UNIQUE KEY unique_division (yearID, lgID, divID)
            )
        """)

        # Ensure yearID column exists (redundant here but kept for safety)
        ensure_yearid_column(cursor)

        # Clear existing data
        cursor.execute("TRUNCATE TABLE divisions")

        # Example: Insert historical division data
        divisions_data = [
            (1969, 'E', 'AL', 'American League East', 'Y'),
            (1969, 'W', 'AL', 'American League West', 'Y'),
            (1969, 'E', 'NL', 'National League East', 'Y'),
            (1969, 'W', 'NL', 'National League West', 'Y'),
            (1977, 'C', 'AL', 'American League Central', 'Y'),
            (1994, 'C', 'NL', 'National League Central', 'Y'),
        ]

        # Insert data using executemany
        cursor.executemany(
            """
            INSERT INTO divisions (yearID, divID, lgID, division_name, division_active)
            VALUES (%s, %s, %s, %s, %s)
            """,
            divisions_data
        )

        # Check if division_name column exists in teams table
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = 'teams'
              AND column_name = 'division_name'
        """)
        column_exists = cursor.fetchone()[0] > 0

        # Add division_name column if it doesn't exist
        if not column_exists:
            cursor.execute("""
                ALTER TABLE teams
                ADD division_name VARCHAR(50)
            """)

        # Update team divisions based on historical data
        cursor.execute("""
            UPDATE teams t
            JOIN divisions d
              ON t.yearID = d.yearID
             AND t.lgID = d.lgID
             AND t.divID = d.divID
            SET t.division_name = d.division_name
            WHERE t.yearID >= 1969
        """)

        conn.commit()
        print("Successfully updated divisions table and team divisions.")

    except pymysql.Error as err:
        print(f"Error: {err}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_divisions()
