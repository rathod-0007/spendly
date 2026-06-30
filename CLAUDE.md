# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Commands

### Setup & Installation

```bash
# Install dependencies (use the venv)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Run the Application

```bash
# Run the dev server (port 5001)
python app.py
```

### Testing

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_foo.py

# Run a single test by name
pytest -k "test_name"
```

---

## Architecture

Spendly is a Flask + SQLite personal expense tracker application.

- **Routing Structure (`app.py`):** Handles user authentication, registration, dashboard queries, profile statistics, legal documents, and CRUD operations for managing expenses.
- **Database Layer (`database/db.py`):** Connects to the local SQLite database (`spendly.db`), sets up custom Row structures, handles cascade operations on deletion, and seeds initial mock data.
- **Template Structure (`templates/`):** Built with standard Jinja2 inheritance templates extending from `base.html` (which holds the global navigation header and centralized footer).
- **Static Assets (`static/`):** Comprises a unified stylesheet (`static/css/style.css`) and a client-side execution script (`static/js/main.js`).

---

## Constraints

- Use vanilla JavaScript only for any interactive front-end elements (no heavy external libraries).
- Keep styles organized inside `static/css/style.css` rather than scattered inside multiple files, except for custom responsive viewport setups scoped in templates.

---

## Project Progress and State Tracker

This section documents the features implemented, UI styling updates, and configuration status of the Spendly application to synchronize context across sessions.

### Project Summary

Spendly is a functional Python-based web app using Flask and SQLite to allow users to securely register accounts, sign in, log transactions across categories, view spending statistics, and delete or edit transactional records.

---

## Updates Implemented

1. **Global Stylesheet Integration (`static/css/style.css`)**
   - Configured custom CSS variables (design tokens) for a consistent dark-ink on warm-paper color palette.
   - Styled cards, lists, layout sections, forms, global responsive navigation, and transaction status badges.
   - Integrated custom responsive configurations.

2. **Dashboard Layout Update (`templates/dashboard.html`)**
   - Cleaned up inline grid styling constraints.
   - Introduced a responsive container that presents a multi-column view on desktop viewports and safely stacks cards vertically on mobile screens.

3. **Landing Page Aesthetic Fix (`templates/landing.html`)**
   - Implemented mock window headers inside the simulated browser visual.
   - Added mock interactive dots (red, yellow, green) inside the hero area to align with standard web presentation wireframes.

4. **Legal Document Flow (`templates/terms.html` & `templates/privacy.html`)**
   - Created standalone static views for both "Terms & Conditions" and the "Privacy Policy".
   - Routed these templates securely via `/terms` and `/privacy` in `app.py`.
   - Updated the global footer navigation links within `base.html` using Flask `url_for` route bindings.

---

## Verification Checklist

- [x] Application routing is active on port `5001`.
- [x] Responsive layout is handled globally.
- [x] Database initializations are handled on startup.
- [x] Deletion operations include a client-side warning dialogue.
- [x] Legal pages resolve without infinite loops or returning to `#`.
