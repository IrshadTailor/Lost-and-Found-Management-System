import sqlite3
import datetime
from pathlib import Path

def init_database(db_path):
    # Ensure the folder exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # -------------------------
    # Users table
    # -------------------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # -------------------------
    # Items table
    # -------------------------
    # Added: location, date
    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        description TEXT,
        location TEXT,
        date TEXT,
        image TEXT,
        status TEXT CHECK(status IN ('lost','found')) NOT NULL,
        reporter_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reporter_id) REFERENCES users(id)
    );
    """)

    # -------------------------
    # Notifications table
    # -------------------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_id INTEGER,
        message TEXT,
        read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized at", db_path)


# -------------------------
# Run directly
# -------------------------
if __name__ == "__main__":
    db_file = Path(__file__).resolve().parent / "instance" / "lostfound.db"
    init_database(str(db_file))
