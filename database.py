"""
database.py
------------
SQLite persistence layer for VeriFied-AI.

Responsible for:
- Initializing the `compliance_audits` table
- Saving new audit results (anomalies are serialized to JSON)
- Retrieving all stored audits (with anomalies deserialized back to Python objects)
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Keep the DB file alongside this module so it works regardless of CWD.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verifed_ai.db")


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the compliance_audits table if it doesn't already exist."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                verdict TEXT NOT NULL,
                system_health_index INTEGER NOT NULL,
                summary_notes TEXT,
                anomalies_detected TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_audit(
    verdict: str,
    system_health_index: int,
    summary_notes: str,
    anomalies_detected: List[Dict[str, Any]],
) -> int:
    """
    Persist a new audit record.

    `anomalies_detected` is a list of dicts (e.g. [{"type": ..., "description": ...}, ...])
    and is stored as a JSON-encoded string in the database.

    Returns the id of the newly inserted row.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO compliance_audits
                (timestamp, verdict, system_health_index, summary_notes, anomalies_detected)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                verdict,
                system_health_index,
                summary_notes,
                json.dumps(anomalies_detected),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_audits() -> List[Dict[str, Any]]:
    """
    Return all audits, most recent first, with `anomalies_detected`
    deserialized back into a Python list of dicts.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM compliance_audits ORDER BY id DESC"
        ).fetchall()

        audits = []
        for row in rows:
            record = dict(row)
            try:
                record["anomalies_detected"] = json.loads(record["anomalies_detected"] or "[]")
            except (json.JSONDecodeError, TypeError):
                record["anomalies_detected"] = []
            audits.append(record)
        return audits
    finally:
        conn.close()


def get_latest_audit() -> Optional[Dict[str, Any]]:
    """Convenience helper: return only the most recent audit, or None if empty."""
    audits = get_all_audits()
    return audits[0] if audits else None
