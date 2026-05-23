# Setup Guide

## Prerequisites

- Python 3.10 or later
- pip

SQLite is included in Python's standard library — no database server required.

## Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd "healthtech_sql"

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize the database
python cli.py setup
```

Expected output:

```
Setting up HEALTHTECH DR demo database...
  Database created: healthtech_dr.db
  Schema:  patients, providers, encounters, lab_results, orders
  Seeded:  10 patients | 5 providers | 20 encounters | 30 labs | 25 orders
```

## Verifying the Installation

```bash
# Run all validation checks
python cli.py troubleshoot

# Run a sample analytics query
python cli.py query patient_census

# Export a billing extract
python cli.py extract billing_extract
```

## Switching to PostgreSQL

The SQL schema and queries use standard ANSI SQL with minor SQLite-specific calls (`julianday`, `date('now')`). To migrate to PostgreSQL:

1. Replace `julianday(d1) - julianday(d2)` with `d1::date - d2::date`
2. Replace `date('now')` with `CURRENT_DATE`
3. Update `db.py`: swap `sqlite3.connect(DB_PATH)` for a `psycopg2` or `asyncpg` connection
4. Update named parameter syntax from `:param` to `%(param)s` (psycopg2) or `$1` (asyncpg)

## Resetting the Database

```bash
rm healthtech_dr.db
python cli.py setup
```
