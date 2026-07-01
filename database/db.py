import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from werkzeug.security import generate_password_hash

def get_db():
    """
    Opens a connection to the PostgreSQL database.
    Railway automatically provides the DATABASE_URL environment variable.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Local development fallback connection string
        database_url = "postgresql://postgres:postgres@localhost:5432/spendly"
    
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """
    Creates the users and expenses tables safely using PostgreSQL syntax.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        amount NUMERIC(12, 2) NOT NULL,
        category VARCHAR(100) NOT NULL,
        date VARCHAR(100) NOT NULL,
        description VARCHAR(500),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    cursor.execute("SELECT COUNT(*) as count FROM users;")
    user_count = cursor.fetchone()['count']
    
    if user_count > 0:
        conn.close()
        return

    # Insert demo user: demo@spendly.com / demo123
    hashed_password = generate_password_hash("demo123")
    cursor.execute("""
        INSERT INTO users (name, email, password_hash) 
        VALUES (%s, %s, %s) RETURNING id;
    """, ("Demo User", "demo@spendly.com", hashed_password))
    
    user_id = cursor.fetchone()['id']
    
    # Get current year and month dynamically (YYYY-MM) for seeding inside the current month
    current_year_month = datetime.now().strftime("%Y-%m")
    
    # 8 sample expenses covering all categories:
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
        VALUES (%s, %s, %s, %s, %s);
    """, sample_expenses)
    
    conn.commit()
    conn.close()

def create_user(name, email, password):
    """
    Hashes the password with generate_password_hash,
    runs a parameterised INSERT into users,
    commits and closes the connection,
    and returns the last inserted id.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    hashed_password = generate_password_hash(password)
    
    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s) RETURNING id;
    """, (name, email, hashed_password))
    
    user_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email):
    """
    Opens get_db(), runs a parameterised SELECT * FROM users WHERE email = %s,
    and returns the corresponding user row or None if not found.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM users WHERE email = %s;
    """, (email,))
    row = cursor.fetchone()
    
    conn.close()
    return row

if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully.")