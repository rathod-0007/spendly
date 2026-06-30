import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
import functools
from datetime import date

# Import from your database structure
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email

app = Flask(__name__)
app.secret_key = "dev-secret-key"

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
        confirm_password = request.form.get("confirm_password")

        # 1. Validation: Ensure all fields are non-empty
        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("register.html")
            
        # 2. Validation: Ensure password matches confirm password
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
            
        # 3. Validation: Password length requirement
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("register.html")

        # 4. Attempt database insertion
        try:
            create_user(name, email, password)
            flash("Registration successful! Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            # Catch duplicate email UNIQUE constraint violation
            flash("Email already registered.", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Query the database for the user email using our helper
        user = get_user_by_email(email)

        # Verify password hash against database record
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # On success, clear current session, assign user_id, flash success and redirect
        session.clear()
        session["user_id"] = user["id"]
        flash("Welcome back!", "success")
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    
    # Fetch all expenses for current user
    expenses = db.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC",
        (g.user["id"],)
    ).fetchall()
    
    # Calculate sum of all expenses
    total_row = db.execute(
        "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?",
        (g.user["id"],)
    ).fetchone()
    total_spending = total_row["total"] if total_row["total"] is not None else 0.0
    
    # Calculate spending grouped by category
    category_rows = db.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (g.user["id"],)
    ).fetchall()
    
    category_totals = {row["category"]: row["total"] for row in category_rows}
    db.close()
    
    return render_template(
        "dashboard.html",
        expenses=expenses,
        total_spending=total_spending,
        category_totals=category_totals
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