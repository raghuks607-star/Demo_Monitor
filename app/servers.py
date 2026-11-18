"""CRUD for Linux server inventory. Credentials stored encrypted; never returned to templates."""

from __future__ import annotations

from typing import Any

from app.crypto import decrypt_secret, encrypt_secret
from app.db import get_db


def _row_public(row) -> dict[str, Any]:
    """Public view of a server row — no decrypted secrets."""
    return {
        "id": row["id"],
        "label": row["label"],
        "hostname": row["hostname"],
        "ssh_username": row["ssh_username"],
        "ssh_port": row["ssh_port"],
        "auth_type": row["auth_type"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_servers() -> list[dict[str, Any]]:
    rows = get_db().execute(
        "SELECT * FROM servers ORDER BY label COLLATE NOCASE ASC"
    ).fetchall()
    return [_row_public(r) for r in rows]


def get_server(server_id: int) -> dict[str, Any] | None:
    row = get_db().execute(
        "SELECT * FROM servers WHERE id = ?", (server_id,)
    ).fetchone()
    return _row_public(row) if row else None


def get_server_with_credential(server_id: int) -> dict[str, Any] | None:
    """Backend-only: includes decrypted credential for SSH collection."""
    row = get_db().execute(
        "SELECT * FROM servers WHERE id = ?", (server_id,)
    ).fetchone()
    if row is None:
        return None
    data = _row_public(row)
    data["credential"] = decrypt_secret(row["credential_encrypted"])
    return data


def create_server(
    *,
    label: str,
    hostname: str,
    ssh_username: str,
    ssh_port: int,
    auth_type: str,
    credential: str,
) -> dict[str, Any]:
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO servers (
            label, hostname, ssh_username, ssh_port, auth_type, credential_encrypted
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            label,
            hostname,
            ssh_username,
            ssh_port,
            auth_type,
            encrypt_secret(credential),
        ),
    )
    db.commit()
    return get_server(cur.lastrowid)  # type: ignore[arg-type]


def update_server(
    server_id: int,
    *,
    label: str,
    hostname: str,
    ssh_username: str,
    ssh_port: int,
    auth_type: str,
    credential: str | None = None,
) -> dict[str, Any] | None:
    """Update fields. If credential is None/empty, keep the existing encrypted value."""
    existing = get_db().execute(
        "SELECT * FROM servers WHERE id = ?", (server_id,)
    ).fetchone()
    if existing is None:
        return None

    if credential:
        enc = encrypt_secret(credential)
    else:
        enc = existing["credential_encrypted"]

    db = get_db()
    db.execute(
        """
        UPDATE servers SET
            label = ?,
            hostname = ?,
            ssh_username = ?,
            ssh_port = ?,
            auth_type = ?,
            credential_encrypted = ?,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (label, hostname, ssh_username, ssh_port, auth_type, enc, server_id),
    )
    db.commit()
    return get_server(server_id)


def delete_server(server_id: int) -> bool:
    db = get_db()
    cur = db.execute("DELETE FROM servers WHERE id = ?", (server_id,))
    db.commit()
    return cur.rowcount > 0
