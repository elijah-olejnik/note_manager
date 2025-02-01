import sqlite3
from utils import DatabaseError


def setup_db(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                created_date TEXT NOT NULL,
                issue_date TEXT NOT NULL
                );
                """
            )
            conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Setup db failed: {e}")
