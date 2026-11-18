"""Unit tests for SSH metrics collection with mocked SSH (Phase 4)."""

from unittest.mock import MagicMock, patch

from app.metrics import MetricsSnapshot, collect_metrics


def _fake_exec(command, timeout=10):
    stdout = MagicMock()
    stderr = MagicMock()
    channel = MagicMock()
    channel.recv_exit_status.return_value = 0
    stdout.channel = channel

    if "proc/stat" in command:
        stdout.read.return_value = b"12.5"
        stderr.read.return_value = b""
    elif "meminfo" in command:
        stdout.read.return_value = b"1073741824 536870912"
        stderr.read.return_value = b""
    elif "net/dev" in command:
        stdout.read.return_value = b"2048 4096"
        stderr.read.return_value = b""
    elif "ss -tuln" in command:
        stdout.read.return_value = b"tcp 0.0.0.0:22\ntcp 127.0.0.1:80\n"
        stderr.read.return_value = b""
    else:
        stdout.read.return_value = b""
        stderr.read.return_value = b"unexpected"
        channel.recv_exit_status.return_value = 1

    return MagicMock(), stdout, stderr


def test_collect_metrics_success(app):
    server = {
        "id": 1,
        "hostname": "10.0.0.1",
        "ssh_port": 22,
        "ssh_username": "ops",
        "auth_type": "password",
        "credential": "x",
    }
    with app.app_context():
        with patch("app.metrics.paramiko.SSHClient") as client_cls:
            client = client_cls.return_value
            client.exec_command.side_effect = _fake_exec
            snap = collect_metrics(server)

    assert snap.ok is True
    assert snap.cpu_percent == 12.5
    assert snap.memory_used is not None
    assert snap.network_rx is not None
    assert "0.0.0.0:22" in snap.ports[0]


def test_collect_metrics_failure(app):
    server = {
        "id": 2,
        "hostname": "bad.host",
        "ssh_port": 22,
        "ssh_username": "ops",
        "auth_type": "password",
        "credential": "x",
    }
    with app.app_context():
        with patch("app.metrics.paramiko.SSHClient") as client_cls:
            client = client_cls.return_value
            client.connect.side_effect = OSError("Network unreachable")
            snap = collect_metrics(server)

    assert isinstance(snap, MetricsSnapshot)
    assert snap.ok is False
    assert "Network unreachable" in (snap.error or "")


def test_detail_page_requires_auth(client):
    response = client.get("/servers/1", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_detail_page_shows_error_when_collection_fails(auth_client, app):
    auth_client.post(
        "/servers/new",
        data={
            "label": "Failing",
            "hostname": "10.0.0.9",
            "ssh_username": "ops",
            "ssh_port": "22",
            "auth_type": "password",
            "credential": "x",
        },
    )
    with patch("app.routes.collect_metrics") as collect:
        collect.return_value = MetricsSnapshot(ok=False, error="SSH timed out")
        page = auth_client.get("/servers/1")
    assert page.status_code == 200
    assert b"Could not collect metrics" in page.data
    assert b"SSH timed out" in page.data
    assert b"http-equiv=\"refresh\"" in page.data
