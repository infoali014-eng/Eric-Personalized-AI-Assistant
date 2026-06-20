import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eric_memory.db")

def init_db():
    """Initializes the database and creates tables if they do not exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL, -- 'preference', 'contact', 'note', 'command'
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing SQLite database: {e}", file=sys.stderr)

def insert_memory(category, content):
    """Inserts a new memory record."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO long_term_memory (category, content) VALUES (?, ?)",
            (category, content)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving to database: {e}", file=sys.stderr)
        return False

def get_all_memories():
    """Retrieves all memories from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT category, content, timestamp FROM long_term_memory ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error reading from database: {e}", file=sys.stderr)
        return []

def search_memories(keywords):
    """
    Searches memories matching any of the specified keywords.
    """
    if not keywords:
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Build query using LIKE operator for each keyword
        query = "SELECT category, content FROM long_term_memory WHERE "
        conditions = []
        params = []
        for kw in keywords:
            conditions.append("content LIKE ? OR category LIKE ?")
            params.extend([f"%{kw}%", f"%{kw}%"])
        
        query += " OR ".join(conditions)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error searching database: {e}", file=sys.stderr)
        return []

# Initialize database on module load
init_db()
