"""Encrypt SSH credentials at rest (Fernet, key derived from SECRET_KEY)."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


def _fernet() -> Fernet:
    digest = hashlib.sha256(current_app.config["SECRET_KEY"].encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a credential string for DB storage."""
    if plaintext is None:
        plaintext = ""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str:
    """Decrypt a stored credential. Returns empty string if missing/invalid."""
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        return ""
