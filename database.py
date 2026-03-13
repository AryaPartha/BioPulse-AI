import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('biopulse.db')
    c = conn.cursor()
    # Users table with Admin flag (0 = regular, 1 = admin)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  weight REAL, is_admin INTEGER DEFAULT 0)''')
    # Health and Weight logs
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, activity TEXT, metric REAL)''')
    # Strength Training table: Stores exercise, sets, reps, and weight
    c.execute('''CREATE TABLE IF NOT EXISTS workouts 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, 
                  exercise TEXT, sets INTEGER, reps INTEGER, weight_lifted REAL)''')
    conn.commit()
    conn.close()

def add_user(username, password, weight):
    try:
        conn = sqlite3.connect('biopulse.db')
        c = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, weight) VALUES (?, ?, ?)", (username, hashed_pw, weight))
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

if __name__ == "__main__":
    init_db()
    print("Database Synced.")