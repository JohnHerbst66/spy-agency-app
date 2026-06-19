import sqlite3
def get_db_connection():
    conn = sqlite3.connect('spy_Vault.db')
    conn.row_factory = sqlite3.Row
    return conn
def create_users_table():
    # This builds the columns inside our secret vault
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codename TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            pass_key TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'agent_default.png'
        )
    ''')
    conn.commit()
    conn.close()
    print("🔒 Spy Vault Database Initialized Successfully!")
