import pymssql
from csi3335s2025 import db_config
import sys


def ensure_yearid_column(cursor):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'divisions' AND column_name = 'yearID'")
    if cursor.fetchone()[0] == 0:
        print("Adding yearID column to divisions table...")
        cursor.execute("ALTER TABLE divisions ADD yearID INT NOT NULL")


def update_divisions():
    try:
        # Connect to the database using pymssql
        conn = pymssql.connect(
            server=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor()

        # Ensure yearID column exists
        ensure_yearid_column(cursor)

        # Create divisions table if it doesn't exist
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='divisions' AND xtype='U')
            CREATE TABLE divisions (
                id INT IDENTITY(1,1) PRIMARY KEY,
                yearID INT NOT NULL,
                lgID CHAR(2) NOT NULL,
                divID CHAR(1) NOT NULL,
                division_name VARCHAR(50) NOT NULL,
                division_active CHAR(1) NOT NULL,
                CONSTRAINT unique_division UNIQUE (yearID, lgID, divID)
            )
        """)

        # Clear existing data
        cursor.execute("TRUNCATE TABLE divisions")

        # Example: Insert historical division data (expand as needed)
        divisions_data = [
            # yearID, divID, lgID, division_name, division_active
            (1969, 'E', 'AL', 'American League East', 'Y'),
            (1969, 'W', 'AL', 'American League West', 'Y'),
            (1969, 'E', 'NL', 'National League East', 'Y'),
            (1969, 'W', 'NL', 'National League West', 'Y'),
            (1977, 'C', 'AL', 'American League Central', 'Y'),  # Example for expansion
            (1994, 'C', 'NL', 'National League Central', 'Y'),  # Example for expansion
            # Add more years/divisions as needed...
        ]

        # Insert data using pymssql's executemany
        cursor.executemany(
            "INSERT INTO divisions (yearID, divID, lgID, division_name, division_active) VALUES (%d, %s, %s, %s, %s)",
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
                       UPDATE teams
                       SET division_name = d.division_name FROM teams t
            JOIN divisions d
                       ON t.yearID = d.yearID
                           AND t.lgID = d.lgID
                           AND t.divID = d.divID
                       WHERE t.yearID >= 1969
                       """)

        # Commit the changes
        conn.commit()
        print("Successfully updated divisions table and team divisions.")

    except pymssql.Error as err:
        print(f"Error: {err}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    update_divisions()