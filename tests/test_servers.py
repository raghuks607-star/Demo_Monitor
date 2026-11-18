"""Unit tests for server inventory CRUD (Phase 2)."""

from app.servers import (
    create_server,
    delete_server,
    get_server,
    get_server_with_credential,
    list_servers,
    update_server,
)


def test_create_list_get_server(app):
    with app.app_context():
        created = create_server(
            label="Web-1",
            hostname="10.0.0.5",
            ssh_username="monitor",
            ssh_port=22,
            auth_type="password",
            credential="s3cret",
        )
        assert created["label"] == "Web-1"
        assert "credential" not in created

        listed = list_servers()
        assert len(listed) == 1
        assert listed[0]["hostname"] == "10.0.0.5"

        fetched = get_server(created["id"])
        assert fetched["ssh_username"] == "monitor"

        with_cred = get_server_with_credential(created["id"])
        assert with_cred["credential"] == "s3cret"


def test_update_and_delete_server(app):
    with app.app_context():
        created = create_server(
            label="Old",
            hostname="host.local",
            ssh_username="u",
            ssh_port=22,
            auth_type="password",
            credential="one",
        )
        updated = update_server(
            created["id"],
            label="New",
            hostname="host.local",
            ssh_username="u",
            ssh_port=2222,
            auth_type="password",
            credential=None,
        )
        assert updated["label"] == "New"
        assert updated["ssh_port"] == 2222
        assert get_server_with_credential(created["id"])["credential"] == "one"

        assert delete_server(created["id"]) is True
        assert get_server(created["id"]) is None


def test_missing_server_returns_none(app):
    with app.app_context():
        assert get_server(9999) is None
        assert delete_server(9999) is False
