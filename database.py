import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('biopulse.db')
    c = conn.cursor()
    # Users table with is_admin column
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  weight REAL, is_admin INTEGER DEFAULT 0)''')
    # Health/Weight logs
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, activity TEXT, metric REAL)''')
    # Strength Training table
    c.execute('''CREATE TABLE IF NOT EXISTS workouts 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, 
                  exercise TEXT, sets INTEGER, reps INTEGER, weight_lifted REAL)''')
    conn.commit()
    conn.close()

def add_user(username, password, weight, is_admin=0):
    try:
        conn = sqlite3.connect('biopulse.db')
        c = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, weight, is_admin) VALUES (?, ?, ?, ?)", 
                  (username, hashed_pw, weight, is_admin))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    conn = sqlite3.connect('biopulse.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user