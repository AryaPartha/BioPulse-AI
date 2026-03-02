import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('biopulse.db')
    c = conn.cursor()
    # Users table: Stores credentials and profile data
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, weight REAL)''')
    conn.commit()
    conn.close()

def add_user(username, password, weight):
    try:
        conn = sqlite3.connect('biopulse.db')
        c = conn.cursor()
        # Simple hash for security (Better for your project demo!)
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, weight) VALUES (?, ?, ?)", 
                  (username, hashed_pw, weight))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists

def verify_user(username, password):
    conn = sqlite3.connect('biopulse.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user