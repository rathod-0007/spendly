import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def get_db():
    """
    Opens a connection to spendly.db at the project root using os.path
    to resolve the path relative to this database/db.py file.
    Sets row_factory and enables foreign key constraints.
    """
    db_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.normpath(os.path.join(db_dir, "..", "spendly.db"))
    
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Creates the users and expenses tables safely.
    Uses 'localtime' modifiers on default datetime queries to record local timezone.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Users table with local timezone default
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    );
    """)
    
    # Create Expenses table with local timezone default
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

def seed_db():
    """
    Seeds the database with a test user and 8 sample expenses.
    Prevents duplicate inserts by returning early if users already exist.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if the users table already contains data to prevent duplication
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    
    if user_count > 0:
        conn.close()
        return

    # Insert demo user: demo@spendly.com / demo123
    hashed_password = generate_password_hash("demo123")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash) 
        VALUES (?, ?, ?);
    """, ("Demo User", "demo@spendly.com", hashed_password))
    
    user_id = cursor.lastrowid
    
    # Get current year and month dynamically (YYYY-MM) for seeding inside the current month
    current_year_month = datetime.now().strftime("%Y-%m")
    
    # 8 sample expenses covering all categories exactly as specified:
    # Food, Transport, Bills, Health, Entertainment, Shopping, Other
    sample_expenses = [
        (user_id, "Bills", 4500.0, f"{current_year_month}-01", "Monthly electricity bill"),
        (user_id, "Food", 3200.0, f"{current_year_month}-03", "Weekly grocery provisions"),
        (user_id, "Health", 2050.0, f"{current_year_month}-04", "Pharmacy and checkup"),
        (user_id, "Transport", 1800.0, f"{current_year_month}-05", "Monthly metro travel pass"),
        (user_id, "Entertainment", 1500.0, f"{current_year_month}-08", "Movie ticket and snacks"),
        (user_id, "Shopping", 3500.0, f"{current_year_month}-10", "Casual wear purchase"),
        (user_id, "Other", 1200.0, f"{current_year_month}-12", "Repairs and miscellaneous"),
        (user_id, "Food", 850.0, f"{current_year_month}-15", "Team lunch at cafe")
    ]
    
    cursor.executemany("""
        INSERT INTO expenses (user_id, category, amount, date, description)
        VALUES (?, ?, ?, ?, ?);
    """, sample_expenses)
    
    conn.commit()
    conn.close()

def create_user(name, email, password):
    """
    Hashes the password with generate_password_hash,
    runs a parameterised INSERT into users,
    commits and closes the connection,
    and returns the cursor's lastrowid.
    sqlite3.IntegrityError bubbles up naturally (caller handles it).
    """
    conn = get_db()
    cursor = conn.cursor()
    
    hashed_password = generate_password_hash(password)
    
    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?);
    """, (name, email, hashed_password))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    """
    Opens get_db(), runs a parameterised SELECT * FROM users WHERE email = ?,
    and returns the corresponding user row or None if not found.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    row = cursor.execute("""
        SELECT * FROM users WHERE email = ?;
    """, (email,)).fetchone()
    
    conn.close()
    return row

if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully.")