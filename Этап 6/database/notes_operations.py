import sqlite3
from datetime import datetime
from utils import NoteStatus, DataIntegrityError, DatabaseError


def note_from_data(row):
    try:
        return {
            'id': row[0],
            'username': row[1],
            'title': row[2],
            'content': row[3],
            'status': NoteStatus[row[4]],
            'created_date': datetime.strptime(row[5], "%d-%m-%Y"),
            'issue_date': datetime.strptime(row[6], "%d-%m-%Y")
        }
    except (KeyError, ValueError) as e:
        raise DataIntegrityError(f"Data convertion error: {e}")


def data_from_note(note, note_id=None):
    is_add = len(note) == 6
    data = [note['title'], note['content'], note['status'].name]
    if is_add:
        data.insert(0, note['username'])
        data.append(datetime.strftime(note['created_date'].date(), "%d-%m-%Y"))
    data.append(datetime.strftime(note['issue_date'].date(), "%d-%m-%Y"))
    if not is_add:
        data.append(note_id)
    return data


def save_note_to_db(note, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO notes (username, title, content, status, created_date, issue_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, data_from_note(note))
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Note saving to db failed: {e}")


def load_notes_from_db(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes;")
            rows = cursor.fetchall()
        return [note_from_data(row) for row in rows] if rows else rows
    except (sqlite3.Error, DataIntegrityError) as e:
        raise DatabaseError(f"Loading notes from db failed: {e}")


def get_note_by_id(note_id, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?;", (note_id,))
            row = cursor.fetchone()
            return note_from_data(row) if row else None
    except (sqlite3.Error, DataIntegrityError) as e:
        raise DatabaseError(f"Getting note by id failed: {e}")


def update_note_in_db(note_id, updates, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, status = ?, issue_date = ? WHERE id = ?;",
                data_from_note(updates, note_id))
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Updating note in db failed: {e}")


def delete_note_from_db(note_id, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?;", (note_id,))
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Note deletion from db failed: {e}")


def search_notes_by_keyword(key, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?;""",
                (f"%{key}%", f"%{key}%")
            )
            rows = cursor.fetchall()
        return [note_from_data(row) for row in rows] if rows else rows
    except (sqlite3.Error, DataIntegrityError) as e:
        raise DatabaseError(f"Searching notes from db failed: {e}")


def filter_notes_by_status(status, db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM notes WHERE status = ?;""",
                (status.name,)
            )
            rows = cursor.fetchall()
        return [note_from_data(row) for row in rows] if rows else rows
    except (sqlite3.Error, DataIntegrityError) as e:
        raise DatabaseError(f"Filtering notes by status from db failed: {e}")
