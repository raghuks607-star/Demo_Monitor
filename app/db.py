"""SQLite connection helpers for local server inventory."""

import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a request-scoped SQLite connection."""
    if "db" not in g:
        path = Path(current_app.config["DATABASE_PATH"])
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_e=None) -> None:
    """Close the request-scoped connection."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            hostname TEXT NOT NULL,
            ssh_username TEXT NOT NULL,
            ssh_port INTEGER NOT NULL DEFAULT 22,
            auth_type TEXT NOT NULL CHECK(auth_type IN ('password', 'key')),
            credential_encrypted TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    db.commit()


def init_app(app) -> None:
    """Register DB teardown and ensure schema on startup."""
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
