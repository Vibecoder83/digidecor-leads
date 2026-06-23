"""
Run once to create data/leads.db from schema.sql.
Safe to re-run: uses CREATE TABLE IF NOT EXISTS throughout.

Usage:
    python src/db/init_db.py
"""

import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("DB_PATH", "data/leads.db"))
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init():
    db_file = ROOT / DB_PATH
    db_file.parent.mkdir(parents=True, exist_ok=True)

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(db_file) as conn:
        conn.executescript(schema)

    print(f"Database ready at: {db_file}")


if __name__ == "__main__":
    init()
