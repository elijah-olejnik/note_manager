import sqlite3


def save_note_to_db(note, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO notes (username, title, content, status, created_date, issue_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    data = (
        note.username,
        note.title,
        note.content,
        note.status.name,
        note.created_date.isoformat(),
        note.issue_date.isoformat()
    )
    cursor.execute(insert_sql, data)
    conn.commit()
    conn.close()
