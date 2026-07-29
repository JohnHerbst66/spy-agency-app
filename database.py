import sqlite3
import os

def get_db_connection():
    # If DATABASE_PATH is set (e.g. a Render persistent disk mount like
    # /var/data/spy_vault.db), store the database there so it survives restarts.
    # Otherwise fall back to a file next to this script — good for local dev.
    db_path = os.environ.get('DATABASE_PATH')
    if not db_path:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'spy_vault.db')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    # Bou die tabel met die korrekte spy_email kolom
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codename TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            spy_email TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'agent_default.png'
        )
    ''')
    conn.commit()
    conn.close()
