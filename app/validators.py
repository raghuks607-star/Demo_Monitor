"""Input validation for server inventory forms."""

import re

_HOST_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
    r"|^(?:\d{1,3}\.){3}\d{1,3}$"
    r"|^\[[0-9A-Fa-f:]+\]$"
)


def validate_server_payload(
    *,
    label: str,
    hostname: str,
    ssh_username: str,
    ssh_port: str | int,
    auth_type: str,
    credential: str,
    require_credential: bool = True,
) -> tuple[dict | None, list[str]]:
    """
    Validate and normalize server form fields.
    Returns (cleaned_dict, errors). cleaned_dict is None when errors is non-empty.
    """
    errors: list[str] = []
    label = (label or "").strip()
    hostname = (hostname or "").strip()
    ssh_username = (ssh_username or "").strip()
    auth_type = (auth_type or "").strip().lower()
    credential = credential or ""

    if not label or len(label) > 120:
        errors.append("Label is required (max 120 characters).")
    if not hostname or len(hostname) > 253 or not _HOST_RE.match(hostname):
        errors.append("Enter a valid hostname or IPv4 address.")
    if not ssh_username or len(ssh_username) > 64 or "/" in ssh_username:
        errors.append("SSH username is required.")

    try:
        port = int(ssh_port)
        if port < 1 or port > 65535:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("SSH port must be an integer between 1 and 65535.")
        port = 22

    if auth_type not in ("password", "key"):
        errors.append("Auth type must be password or key.")

    if require_credential and not credential.strip():
        errors.append("SSH password or private key is required.")

    if errors:
        return None, errors

    return {
        "label": label,
        "hostname": hostname,
        "ssh_username": ssh_username,
        "ssh_port": port,
        "auth_type": auth_type,
        "credential": credential,
    }, []
