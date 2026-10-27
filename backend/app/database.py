import sqlite3
from contextlib import contextmanager
from .config import DATA_DIR, DB_PATH

def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS credentials (
          id INTEGER PRIMARY KEY AUTOINCREMENT, credential_id TEXT UNIQUE NOT NULL,
          student_name TEXT, university TEXT, degree TEXT, graduation_year TEXT,
          certificate_hash TEXT NOT NULL, original_filename TEXT, extracted_text TEXT,
          extraction_json TEXT, status TEXT NOT NULL DEFAULT 'ACTIVE',
          issued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, revoked_at TEXT)''')
        con.execute('''CREATE TABLE IF NOT EXISTS verification_logs (
          id INTEGER PRIMARY KEY AUTOINCREMENT, credential_id TEXT, uploaded_hash TEXT NOT NULL,
          result TEXT NOT NULL, details TEXT, checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        con.commit()

@contextmanager
def connect():
    init_db()
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()
