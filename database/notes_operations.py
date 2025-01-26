import sqlite3
from datetime import datetime
from utils import NoteStatus


def save_note_to_db(note, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO notes (username, title, content, status, created_date, issue_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    data = (
        note['username'],
        note['title'],
        note['content'],
        note['status'].name,
        datetime.strftime(note['created_date'], "%d-%m-%Y"),
        datetime.strftime(note['issue_date'], "%d-%m-%Y")
    )
    cursor.execute(insert_sql, data)
    conn.commit()
    conn.close()


def load_notes_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes;")
    rows = cursor.fetchall()
    if not rows:
        return []
    notes = []
    for row in rows:
        notes.append(
            {
                'id_' : row[0],
                'username' : row[1],
                'title' : row[2],
                'content' : row[3],
                'status' : NoteStatus[row[4]],
                'created_date' : datetime.strptime(row[5], "%d-%m-%Y").date(),
                'issue_date' : datetime.strptime(row[6], "%d-%m-%Y").date()
            }
        )
    conn.close()
    return notes