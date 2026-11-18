"""Application configuration. Secrets come from environment variables."""

import os
from pathlib import Path

# Demo default: username admin / password admin (hash only — never plaintext in repo).
_DEFAULT_ADMIN_PASSWORD_HASH = (
    "scrypt:32768:8:1$aXULgBTb1xMM1GYk$"
    "f4265fa8dc96049090fba6e5a3aae6342cd08c9b9679c22f945402d3b1e4351c"
    "d4954b5be816966e8a71466dbbae88b79472e6c1bb5aa57745c74b2901242b15"
)

_BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base config for the local demo app."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = os.environ.get(
        "ADMIN_PASSWORD_HASH", _DEFAULT_ADMIN_PASSWORD_HASH
    )
    # Local SQLite inventory (gitignored *.db)
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH", str(_BASE_DIR / "instance" / "servers.db")
    )
    # SSH: reject unknown hosts by default. Set to "1" only for local demo convenience.
    SSH_AUTO_ADD_HOST_KEYS = os.environ.get("SSH_AUTO_ADD_HOST_KEYS", "0") == "1"
    SSH_CONNECT_TIMEOUT = int(os.environ.get("SSH_CONNECT_TIMEOUT", "8"))
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
