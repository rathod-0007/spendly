import os
import sys
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

# Ensure the root directory is on the path so we can import database modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.db import get_db

def generate_indian_user():
    """
    Generates a random realistic Indian name and derives an email address
    with a random 2-3 digit numeric suffix.
    """
    first_names = [
        "Amit", "Rahul", "Priya", "Sunita", "Vijay", "Deepak", "Siddharth", 
        "Ananya", "Rajesh", "Vikram", "Suresh", "Karan", "Aditya", "Neha", 
        "Pooja", "Rohan", "Arjun", "Sneha", "Kavita", "Sanjay", "Nisha",
        "Harish", "Preeti", "Manish", "Divya", "Abhishek", "Kiran"
    ]
    last_names = [
        "Sharma", "Kumar", "Singh", "Patel", "Joshi", "Gupta", "Mehta", 
        "Verma", "Nair", "Iyer", "Reddy", "Choudhury", "Banerjee", "Rao", 
        "Das", "Sen", "Mishra", "Gill", "Bose", "Kulkarni", "Deshmukh",
        "Pillai", "Menon", "Naidu", "Roy", "Saxena", "Pandey"
    ]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"
    
    # Generate random 2-3 digit number suffix
    suffix = str(random.randint(10, 999))
    email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"
    
    return name, email

def seed_single_user():
    conn = get_db()
    cursor = conn.cursor()
    
    # Loop to ensure the email is globally unique in our database
    while True:
        name, email = generate_indian_user()
        cursor.execute("SELECT id FROM users WHERE email = ?;", (email,))
        if cursor.fetchone() is None:
            break
            
    hashed_password = generate_password_hash("password123")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?);
    """, (name, email, hashed_password, created_at))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Print the exact confirmation details requested
    print(f"id: {user_id}")
    print(f"name: {name}")
    print(f"email: {email}")

if __name__ == "__main__":
    seed_single_user()