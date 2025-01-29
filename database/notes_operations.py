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


def update_note_in_db(note_id, updates, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    update_sql = """
    UPDATE notes
    SET title = ?, content = ?, status = ?, issue_date = ?
    WHERE id = ?;
    """
    data = (
        updates['title'],
        updates['content'],
        updates['status'].name,
        datetime.strftime(updates['issue_date'], "%d-%m-%Y"),
        note_id
    )
    cursor.execute(update_sql, data)
    conn.commit()
    conn.close()


def delete_note_from_db(note_id, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?;", (note_id,))
    conn.commit()
    conn.close()


def search_notes_by_keyword(key, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?;""",
        (f"%{key}%", f"%{key}%")
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id_': row[0],
            'username': row[1],
            'title': row[2],
            'content': row[3],
            'status': NoteStatus[row[4]],
            'created_date': datetime.strptime(row[5], "%d-%m-%Y").date(),
            'issue_date' : datetime.strptime(row[6], "%d-%m-%Y").date()
        } for row in rows
    ]


def filter_notes_by_status(status, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM notes WHERE status = ?;""",
        (status.name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id_': row[0],
            'username': row[1],
            'title': row[2],
            'content': row[3],
            'status': NoteStatus[row[4]],
            'created_date': datetime.strptime(row[5], "%d-%m-%Y").date(),
            'issue_date' : datetime.strptime(row[6], "%d-%m-%Y").date()
        } for row in rows
    ]
