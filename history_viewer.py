import sqlite3

DB_FILE = "jarvis_history.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

def show_history():
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    for row in rows:
        print(f"[{row[1]}] Prompt: {row[2]}")
        print(f"   AI Reply: {row[3]}")
        print(f"   Search Reply: {row[4]}")
        print("-"*50)

if __name__ == "__main__":
    show_history()