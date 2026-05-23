"""Database connection and query execution layer."""

import csv
import os
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "healthtech_dr.db"
SCHEMA_DIR = Path(__file__).parent / "schema"
QUERY_DIR = Path(__file__).parent / "queries"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def setup_database() -> None:
    """Create tables and load seed data from SQL files."""
    conn = get_connection()
    with conn:
        conn.executescript((SCHEMA_DIR / "create_tables.sql").read_text())
        conn.executescript((SCHEMA_DIR / "seed_data.sql").read_text())
    conn.close()


_SAFE_NAME = re.compile(r"^[a-zA-Z0-9_]+$")


def _find_query_file(name: str) -> Path:
    """Search all subdirectories under queries/ for <name>.sql."""
    if not _SAFE_NAME.match(name):
        raise ValueError(
            f"Invalid query name '{name}'. Use only letters, digits, and underscores."
        )
    matches = list(QUERY_DIR.rglob(f"{name}.sql"))
    if not matches:
        raise FileNotFoundError(
            f"Query '{name}.sql' not found under {QUERY_DIR}.\n"
            f"Available queries: {_list_queries()}"
        )
    return matches[0]


def _list_queries() -> list[str]:
    return sorted(p.stem for p in QUERY_DIR.rglob("*.sql"))


def run_named_query(name: str, params: dict) -> tuple[list[str], list[tuple]]:
    """Execute a named query file and return (column_names, rows)."""
    sql = _find_query_file(name).read_text()

    # data_validation.sql contains multiple statements — handle each separately
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    conn = get_connection()
    all_columns: list[str] = []
    all_rows: list[tuple] = []

    def _is_select(stmt: str) -> bool:
        stripped = "\n".join(
            line for line in stmt.splitlines()
            if not line.strip().startswith("--")
        ).strip()
        return stripped.upper().startswith("SELECT")

    with conn:
        for stmt in statements:
            if not _is_select(stmt):
                continue
            cursor = conn.execute(stmt, params)
            rows = cursor.fetchall()
            if rows:
                cols = [d[0] for d in cursor.description]
                if not all_columns:
                    all_columns = cols
                all_rows.extend([tuple(r) for r in rows])

    conn.close()
    return all_columns, all_rows


def export_to_csv(name: str, params: dict, output_path: Path) -> int:
    """Run a named query and write results to a CSV file. Returns row count."""
    columns, rows = run_named_query(name, params)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows)


def list_queries() -> list[str]:
    return _list_queries()
