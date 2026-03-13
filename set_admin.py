import sqlite3

def promote_to_admin(username):
    # Connect to your project database
    conn = sqlite3.connect('biopulse.db')
    cursor = conn.cursor()

    try:
        # Update the is_admin flag from 0 to 1 for the specific user
        cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"🚀 Success! '{username}' has been promoted to System Admin.")
            print("Restart your Streamlit app and log in to see the Admin Dashboard.")
        else:
            print(f"⚠️ Error: User '{username}' not found in the database.")
            print("Make sure you have already registered this username in the app first.")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # REPLACE 'Mukesh' with your actual username from the app
    my_username = "Mukesh" 
    promote_to_admin(my_username)