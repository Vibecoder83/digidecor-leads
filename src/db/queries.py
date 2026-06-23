"""
Reusable read/write helpers for leads.db.
All functions accept an open sqlite3.Connection.
"""

import json
import sqlite3
from typing import Optional


# ── businesses ────────────────────────────────────────────────

def insert_business(conn: sqlite3.Connection, name: str, source: str, **kwargs) -> int:
    """Insert a business and return its new id."""
    fields = ["name", "source"] + list(kwargs.keys())
    placeholders = ", ".join("?" * len(fields))
    values = [name, source] + list(kwargs.values())
    cur = conn.execute(
        f"INSERT INTO businesses ({', '.join(fields)}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
    return cur.lastrowid


def get_businesses_without_crawl(conn: sqlite3.Connection) -> list[dict]:
    """Return businesses that have never been crawled."""
    rows = conn.execute("""
        SELECT b.* FROM businesses b
        LEFT JOIN crawl_results c ON c.business_id = b.id
        WHERE c.id IS NULL AND b.website_url IS NOT NULL
    """).fetchall()
    return [dict(r) for r in rows]


# ── crawl_results ─────────────────────────────────────────────

def insert_crawl(conn: sqlite3.Connection, business_id: int, **kwargs) -> int:
    """Insert a crawl result and return its new id."""
    fields = ["business_id"] + list(kwargs.keys())
    placeholders = ", ".join("?" * len(fields))
    values = [business_id] + list(kwargs.values())
    cur = conn.execute(
        f"INSERT INTO crawl_results ({', '.join(fields)}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
    return cur.lastrowid


# ── signals ───────────────────────────────────────────────────

def insert_signal(conn: sqlite3.Connection, crawl_id: int, key: str,
                  value: Optional[str] = None, weight: float = 1.0) -> None:
    conn.execute(
        "INSERT INTO signals (crawl_id, signal_key, signal_value, weight) VALUES (?,?,?,?)",
        (crawl_id, key, value, weight),
    )
    conn.commit()


# ── scores ────────────────────────────────────────────────────

def upsert_score(conn: sqlite3.Connection, business_id: int,
                 total_score: float, breakdown: dict) -> None:
    conn.execute(
        "INSERT INTO scores (business_id, total_score, score_breakdown) VALUES (?,?,?)",
        (business_id, total_score, json.dumps(breakdown)),
    )
    conn.commit()


def get_top_leads(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    """Return top-scored leads with business name and latest score."""
    rows = conn.execute("""
        SELECT b.id, b.name, b.city, b.website_url, s.total_score, s.scored_at
        FROM scores s
        JOIN businesses b ON b.id = s.business_id
        ORDER BY s.total_score DESC
        LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]


def get_db(db_path: str) -> sqlite3.Connection:
    """Open a database connection with row_factory set."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
