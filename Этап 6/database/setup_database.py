import sqlite3


def setup_db():
    conn = sqlite3.connect('data/notes.db')
    cursor = conn.cursor()

    create_table_sql = """
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

    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()
