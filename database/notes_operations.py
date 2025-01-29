import sqlite3
from datetime import datetime
from utils import NoteStatus


def notes_from_data(rows):
    return [
        {
            'id_': row[0],
            'username': row[1],
            'title': row[2],
            'content': row[3],
            'status': NoteStatus[row[4]],
            'created_date': datetime.strptime(row[5], "%d-%m-%Y").date(),
            'issue_date': datetime.strptime(row[6], "%d-%m-%Y").date()
        } for row in rows
    ]


def data_from_note(note, note_id = None):
    is_add = len(note) == 6
    data = [note['title'], note['content'], note['status']]
    if is_add:
        data.insert(0, note['username'])
        data.append(note['created_date'])
    data.append(note['issue_date'])
    if not is_add:
        data.append(note_id)
    return data


def save_note_to_db(note, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO notes (username, title, content, status, created_date, issue_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, data_from_note(note))
        conn.commit()


def load_notes_from_db(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes;")
        rows = cursor.fetchall()
    return notes_from_data(rows) if rows else rows


def update_note_in_db(note_id, updates, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE notes SET title = ?, content = ?, status = ?, issue_date = ? WHERE id = ?;""",
        data_from_note(updates, note_id))
        conn.commit()


def delete_note_from_db(note_id, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?;", (note_id,))
        conn.commit()


def search_notes_by_keyword(key, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?;""",
            (f"%{key}%", f"%{key}%")
        )
        rows = cursor.fetchall()
    return notes_from_data(rows) if rows else rows


def filter_notes_by_status(status, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM notes WHERE status = ?;""",
            (status.name,)
        )
        rows = cursor.fetchall()
    return notes_from_data(rows) if rows else rows
