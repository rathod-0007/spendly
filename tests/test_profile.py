import os
import sys
import pytest

# Inject the project root directory into Python's system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as client:
        yield client

def test_profile_redirects_when_logged_out(client):
    """
    1. Visiting /profile without being logged in redirects to /login (302)
    """
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_profile_returns_200_when_logged_in(client):
    """
    2. Visiting /profile while logged in returns HTTP 200
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/profile")
    assert response.status_code == 200

def test_profile_shows_user_info(client):
    """
    3. The page displays a user info card with name and email
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/profile")
    html = response.data.decode()
    assert "Nitish Singh" in html
    assert "nitish@spendly.com" in html

def test_profile_shows_stats(client):
    """
    4. The page displays stats totals including outflow and top category
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/profile")
    html = response.data.decode()
    assert "₹3,800.00" in html
    assert "Bills" in html

def test_profile_shows_transactions(client):
    """
    5. The page displays a transaction table with recently hardcoded records
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/profile")
    html = response.data.decode()
    assert "Lunch with colleagues" in html
    assert "New earphones" in html
    assert "Movie tickets" in html

def test_profile_shows_category_breakdown(client):
    """
    6. The page displays category breakdown items with active percentages
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/profile")
    html = response.data.decode()
    assert "Shopping" in html
    assert "Transport" in html
    assert "Entertainment" in html