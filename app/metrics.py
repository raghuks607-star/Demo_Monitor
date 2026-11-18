"""Collect live Linux metrics over SSH. Allowlisted commands only; never logs secrets."""

from __future__ import annotations

import io
import logging
from dataclasses import asdict, dataclass, field
from typing import Any

import paramiko
from flask import current_app

logger = logging.getLogger(__name__)

# Fixed remote commands only — no free-form shell from the UI.
_CMD_CPU = (
    "grep 'cpu ' /proc/stat | awk '{u=$2+$4; t=$2+$4+$5; if (t>0) printf \"%.1f\", "
    "100*u/t; else print 0}'"
)
_CMD_MEM = (
    "awk '/MemTotal:/{t=$2} /MemAvailable:/{a=$2} END{"
    "used=(t-a)*1024; free=a*1024; "
    "printf \"%d %d\", used, free}' /proc/meminfo"
)
_CMD_NET = (
    "awk 'NR>2 {rx+=$2; tx+=$10} END {printf \"%d %d\", rx, tx}' /proc/net/dev"
)
_CMD_PORTS = (
    "ss -tuln 2>/dev/null | awk 'NR>1 {print $1, $5}' | head -n 40"
)


@dataclass
class MetricsSnapshot:
    ok: bool
    error: str | None = None
    cpu_percent: float | None = None
    memory_used: str | None = None
    memory_free: str | None = None
    network_rx: str | None = None
    network_tx: str | None = None
    ports: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_private_key(pem: str) -> paramiko.PKey:
    """Load RSA/ECDSA/Ed25519 private key material from PEM text."""
    errors: list[str] = []
    for key_cls in (paramiko.RSAKey, paramiko.ECDSAKey, paramiko.Ed25519Key):
        try:
            return key_cls.from_private_key(io.StringIO(pem))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{key_cls.__name__}: {exc}")
    raise ValueError("Could not parse private key (RSA/ECDSA/Ed25519 PEM expected).")


def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{n} B"


def _run(client: paramiko.SSHClient, command: str) -> str:
    _stdin, stdout, stderr = client.exec_command(command, timeout=10)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    code = stdout.channel.recv_exit_status()
    if code != 0 and not out:
        raise RuntimeError(err or f"Remote command failed (exit {code})")
    return out


def collect_metrics(server: dict[str, Any]) -> MetricsSnapshot:
    """
    SSH into server and return a live snapshot.
    `server` must include decrypted `credential` (backend-only).
    Never logs hostname credentials or private key material.
    """
    client = paramiko.SSHClient()
    if current_app.config.get("SSH_AUTO_ADD_HOST_KEYS"):
        # Demo convenience only — prefer known_hosts in real use.
        logger.warning(
            "SSH_AUTO_ADD_HOST_KEYS enabled: unknown hosts will be accepted (demo only)."
        )
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    else:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())

    connect_kwargs: dict[str, Any] = {
        "hostname": server["hostname"],
        "port": int(server["ssh_port"]),
        "username": server["ssh_username"],
        "timeout": current_app.config.get("SSH_CONNECT_TIMEOUT", 8),
        "allow_agent": False,
        "look_for_keys": False,
    }

    auth_type = server.get("auth_type")
    credential = server.get("credential") or ""
    try:
        if auth_type == "password":
            connect_kwargs["password"] = credential
        elif auth_type == "key":
            connect_kwargs["pkey"] = _load_private_key(credential)
        else:
            return MetricsSnapshot(ok=False, error="Unsupported SSH auth type.")

        client.connect(**connect_kwargs)

        cpu_raw = _run(client, _CMD_CPU)
        mem_raw = _run(client, _CMD_MEM)
        net_raw = _run(client, _CMD_NET)
        ports_raw = _run(client, _CMD_PORTS)

        used_b, free_b = (int(x) for x in mem_raw.split())
        rx_b, tx_b = (int(x) for x in net_raw.split())
        ports = [line.strip() for line in ports_raw.splitlines() if line.strip()]

        return MetricsSnapshot(
            ok=True,
            cpu_percent=float(cpu_raw),
            memory_used=_human_bytes(used_b),
            memory_free=_human_bytes(free_b),
            network_rx=_human_bytes(rx_b),
            network_tx=_human_bytes(tx_b),
            ports=ports,
        )
    except Exception as exc:  # noqa: BLE001 — surface any SSH/parse failure cleanly
        logger.info("Metrics collection failed for server id=%s", server.get("id"))
        return MetricsSnapshot(ok=False, error=str(exc) or "SSH collection failed.")
    finally:
        client.close()
