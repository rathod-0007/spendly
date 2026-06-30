import os
import sys
import random
from datetime import datetime, timedelta

# Ensure the root directory is on the path so we can import database modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.db import get_db

# Category rules mapping as per specifications
CATEGORY_RULES = {
    "Food": {"min_amt": 50, "max_amt": 800, "weight": 0.35, "descriptions": [
        "Zomato dinner delivery", "Groceries from local market", 
        "Tea and snacks with colleagues", "Sunday brunch with family", 
        "Swiggy lunch order", "Cafe coffee and cookies", "Fruit market purchases"
    ]},
    "Transport": {"min_amt": 20, "max_amt": 500, "weight": 0.15, "descriptions": [
        "Uber ride to office", "Metro card recharge", "Auto-rickshaw fare", 
        "Petrol filling for vehicle", "Ola outstation ride", "Bus ticket fare"
    ]},
    "Bills": {"min_amt": 200, "max_amt": 3000, "weight": 0.15, "descriptions": [
        "Electricity bill payment", "Broadband internet subscription", 
        "Mobile prepaid recharge", "Piped gas utility bill", 
        "Water bill payment", "DTH television recharge"
    ]},
    "Shopping": {"min_amt": 200, "max_amt": 5000, "weight": 0.15, "descriptions": [
        "Winter jacket from store", "Sneakers and sports socks", "Office backpack", 
        "Kitchen utensils set", "Bed linen and pillow covers", "Electronic adapter accessories"
    ]},
    "Other": {"min_amt": 50, "max_amt": 1000, "weight": 0.10, "descriptions": [
        "Gifts for colleague birthday", "Laundry dry cleaning service", 
        "Donation to local charity", "Housekeeping supplies", "Courier shipping charges"
    ]},
    "Health": {"min_amt": 100, "max_amt": 2000, "weight": 0.05, "descriptions": [
        "Medicines from pharmacy", "Doctor consultation fee", "Dental checkup and cleaning", 
        "Multivitamin supplements", "Diagnostic blood tests"
    ]},
    "Entertainment": {"min_amt": 100, "max_amt": 1500, "weight": 0.05, "descriptions": [
        "Netflix monthly subscription", "Movie tickets at multiplex", 
        "Concert entrance fee", "Video game digital purchase", "Bowling alley game"
    ]}
}

def main():
    # 1. Parse arguments
    if len(sys.argv) < 4:
        print("Usage: python seed_expenses.py <user_id> <count> <months>")
        print("Example: python seed_expenses.py 1 50 6")
        sys.exit(1)
        
    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: python seed_expenses.py <user_id> <count> <months>")
        print("Error: All arguments must be valid integers.")
        sys.exit(1)
        
    # 2. Verify user exists
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?;", (user_id,))
    if cursor.fetchone() is None:
        print(f"No user found with id {user_id}.")
        conn.close()
        sys.exit(1)
        
    # 3. Generate and insert expenses
    categories = list(CATEGORY_RULES.keys())
    weights = [CATEGORY_RULES[cat]["weight"] for cat in categories]
    
    today = datetime.now()
    max_days_back = months * 30
    
    # Generate list of expenses
    expenses_to_insert = []
    for _ in range(count):
        # Pick a weighted category (Food most common, Health & Entertainment least)
        category = random.choices(categories, weights=weights, k=1)[0]
        rules = CATEGORY_RULES[category]
        
        # Determine randomized details
        amount = round(random.uniform(rules["min_amt"], rules["max_amt"]), 2)
        description = random.choice(rules["descriptions"])
        
        # Calculate randomized past date
        random_days_ago = random.randint(0, max_days_back)
        expense_date = today - timedelta(days=random_days_ago)
        date_str = expense_date.strftime("%Y-%m-%d")
        
        expenses_to_insert.append((category, amount, date_str, description))
        
    inserted_records = []
    
    # Insert inside a single transaction
    try:
        cursor.execute("BEGIN TRANSACTION;")
        for cat, amt, dt, desc in expenses_to_insert:
            cursor.execute("""
                INSERT INTO expenses (user_id, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?);
            """, (user_id, cat, amt, dt, desc))
            inserted_records.append({
                "id": cursor.lastrowid,
                "category": cat,
                "amount": amt,
                "date": dt,
                "description": desc
            })
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Database insertion failed: {e}. Transaction rolled back.")
        conn.close()
        sys.exit(1)
        
    conn.close()
    
    # 4. Print confirmation and stats
    dates = [datetime.strptime(item["date"], "%Y-%m-%d") for item in inserted_records]
    min_date = min(dates).strftime("%Y-%m-%d") if dates else "N/A"
    max_date = max(dates).strftime("%Y-%m-%d") if dates else "N/A"
    
    print(f"Successfully inserted: {len(inserted_records)} expenses.")
    print(f"Date range spanned: {min_date} to {max_date}")
    print("\nSample of 5 inserted records:")
    
    # Display 5 random sample inserts
    sample_records = random.sample(inserted_records, min(5, len(inserted_records)))
    for rec in sample_records:
        print(f" - ID: {rec['id']} | Date: {rec['date']} | Category: {rec['category']} | Amount: ₹{rec['amount']:.2f} | Desc: {rec['description']}")

if __name__ == "__main__":
    main()