from flask import Flask, render_template, request, redirect, url_for, session, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from datetime import date

# Import from your database structure
from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = "spendly_secret_key_change_in_production"

# ------------------------------------------------------------------ #
# Authentication Helpers                                             #
# ------------------------------------------------------------------ #

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        db.close()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view

# ------------------------------------------------------------------ #
# Basic Routes                                                       #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if g.user:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        error = None

        if not name or not email or not password:
            error = "All fields are required."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."

        if error is None:
            db = get_db()
            try:
                hashed_pw = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, hashed_pw)
                )
                db.commit()
                return redirect(url_for("login"))
            except db.IntegrityError:
                error = f"Email {email} is already registered."
            finally:
                db.close()

        return render_template("register.html", error=error)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        error = None

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Incorrect email or password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    
    # Capture optional dashboard filters from query arguments
    category = request.args.get("category", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    search = request.args.get("search", "")
    
    # 1. Fetch expenses dynamically applying parameterized filters
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [g.user["id"]]
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if search:
        query += " AND description LIKE ?"
        params.append(f"%{search}%")
        
    query += " ORDER BY date DESC, id DESC"
    expenses = db.execute(query, params).fetchall()
    
    # 2. Calculate dynamic sum of filtered expenses
    sum_query = "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?"
    sum_params = [g.user["id"]]
    
    if category:
        sum_query += " AND category = ?"
        sum_params.append(category)
    if start_date:
        sum_query += " AND date >= ?"
        sum_params.append(start_date)
    if end_date:
        sum_query += " AND date <= ?"
        sum_params.append(end_date)
    if search:
        sum_query += " AND description LIKE ?"
        sum_params.append(f"%{search}%")
        
    total_row = db.execute(sum_query, sum_params).fetchone()
    total_spending = total_row["total"] if total_row["total"] is not None else 0.0
    
    # 3. Calculate category totals dynamically for the filtered set
    cat_query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
    cat_params = [g.user["id"]]
    
    if category:
        cat_query += " AND category = ?"
        cat_params.append(category)
    if start_date:
        cat_query += " AND date >= ?"
        cat_params.append(start_date)
    if end_date:
        cat_query += " AND date <= ?"
        cat_params.append(end_date)
    if search:
        cat_query += " AND description LIKE ?"
        cat_params.append(f"%{search}%")
        
    cat_query += " GROUP BY category ORDER BY total DESC"
    category_rows = db.execute(cat_query, cat_params).fetchall()
    
    category_totals = {row["category"]: row["total"] for row in category_rows}
    db.close()
    
    return render_template(
        "dashboard.html",
        expenses=expenses,
        total_spending=total_spending,
        category_totals=category_totals,
        # Return filter parameters to populate inputs in HTML
        active_category=category,
        active_start_date=start_date,
        active_end_date=end_date,
        active_search=search
    )


@app.route("/terms")
def terms():
    """Renders the Terms and Conditions page."""
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    """Renders the Privacy Policy page."""
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# CRUD Routes                                                        #
# ------------------------------------------------------------------ #

@app.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        expense_date = request.form.get("date")
        description = request.form.get("description")
        error = None

        if not amount or not category or not expense_date:
            error = "Amount, Category, and Date are required."

        if error is None:
            db = get_db()
            db.execute("""
                INSERT INTO expenses (user_id, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?);
            """, (g.user["id"], category, float(amount), expense_date, description))
            db.commit()
            db.close()
            return redirect(url_for("dashboard"))

        return render_template("expense_form.html", title="Add Expense", error=error, today=date.today().isoformat())

    return render_template("expense_form.html", title="Add Expense", today=date.today().isoformat())


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    db = get_db()
    # Ensure the expense exists and belongs to the current user
    expense = db.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?", 
        (id, g.user["id"])
    ).fetchone()

    if expense is None:
        db.close()
        abort(404)

    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        expense_date = request.form.get("date")
        description = request.form.get("description")
        error = None

        if not amount or not category or not expense_date:
            error = "Amount, Category, and Date are required."

        if error is None:
            db.execute("""
                UPDATE expenses 
                SET category = ?, amount = ?, date = ?, description = ?
                WHERE id = ? AND user_id = ?;
            """, (category, float(amount), expense_date, description, id, g.user["id"]))
            db.commit()
            db.close()
            return redirect(url_for("dashboard"))

        db.close()
        return render_template("expense_form.html", title="Edit Expense", expense=expense, error=error)

    db.close()
    return render_template("expense_form.html", title="Edit Expense", expense=expense)


@app.route("/expenses/<int:id>/delete")
@login_required
def delete_expense(id):
    db = get_db()
    # Confirm security ownership before deletion
    expense = db.execute(
        "SELECT id FROM expenses WHERE id = ? AND user_id = ?", 
        (id, g.user["id"])
    ).fetchone()

    if expense:
        db.execute("DELETE FROM expenses WHERE id = ?", (id,))
        db.commit()
        
    db.close()
    return redirect(url_for("dashboard"))


# ------------------------------------------------------------------ #
# Profile Route                                                      #
# ------------------------------------------------------------------ #

@app.route("/profile")
@login_required
def profile():
    # Fetching simple profile information
    db = get_db()
    stats = db.execute(
        "SELECT COUNT(*) as count, SUM(amount) as total FROM expenses WHERE user_id = ?",
        (g.user["id"],)
    ).fetchone()
    db.close()
    return render_template("profile.html", stats=stats)


# ------------------------------------------------------------------ #
# Application Context Startup Block                                  #
# ------------------------------------------------------------------ #
with app.app_context():
    init_db()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)