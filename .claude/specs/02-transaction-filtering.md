# Spec: Transaction Filtering and Search

## Overview
This feature adds interactive filtering (by category, custom date ranges) and text search on the main user dashboard. It allows users to quickly isolate specific transactions, search past notes, and view dynamic recalculations of their totals without leaving the dashboard view.

## Depends on
Step 01 (Relational Database Implementation & Seeding) is fully complete and verified.

## Routes
- `GET /dashboard` - Modify existing route to accept query parameters: `category` (string), `start_date` (string), `end_date` (string), and `search` (string) - logged-in access level.

## Database changes
No database changes are needed. This feature uses the existing columns in the `expenses` table.

## Templates
- **Modify:** `templates/dashboard.html` to add a responsive filtering bar form above the transaction table containing controls for category selection, date bounds, description keyword search, and a clear/reset action.

## Files to change
- `app.py` (Update `/dashboard` route logic to dynamically append filter clauses to SQL queries securely).
- `templates/dashboard.html` (Update to include the search form elements and preserve active filter values inside inputs on page refresh).

## Files to create
No new files are required.

## New dependencies
No new pip dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only (use dynamic SQL list generation with `?` placeholders).
- Passwords hashed with werkzeug.
- Use CSS variables — never hardcode hex values.
- All templates extend base.html.

## Definition of done
- [ ] Dashboard displays an interactive filter form with Category, Start Date, End Date, and Description Search inputs.
- [ ] Filtering by a selected Category displays only transactions belonging to that category.
- [ ] Specifying a start and/or end date dynamically limits the transactions strictly within that date window.
- [ ] Typing a search keyword returns only transactions where the description matches the term.
- [ ] All active filters can be combined simultaneously (e.g. Category + Date Range + Search) yielding correct intersection query results.
- [ ] The "All-time Spending" metric card and progress bars dynamically update to reflect only the currently filtered subset of expenses.
- [ ] Clear/Reset filters button clears all parameters and returns to the full transaction list.