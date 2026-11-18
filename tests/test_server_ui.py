"""Integration tests for server management UI (Phase 3)."""


def test_add_edit_delete_server_via_client(auth_client):
    add = auth_client.post(
        "/servers/new",
        data={
            "label": "App DB",
            "hostname": "db.example.com",
            "ssh_username": "ops",
            "ssh_port": "22",
            "auth_type": "password",
            "credential": "demo-pass",
        },
        follow_redirects=True,
    )
    assert add.status_code == 200
    assert b"App DB" in add.data
    assert b"demo-pass" not in add.data

    # Discover id from detail link pattern /servers/<id>
    list_page = auth_client.get("/dashboard")
    assert b"db.example.com" in list_page.data

    edit_page = auth_client.get("/servers/1/edit")
    assert edit_page.status_code == 200
    assert b"App DB" in edit_page.data
    assert b"demo-pass" not in edit_page.data
    assert b"unchanged" in edit_page.data

    updated = auth_client.post(
        "/servers/1/edit",
        data={
            "label": "App DB 2",
            "hostname": "db.example.com",
            "ssh_username": "ops",
            "ssh_port": "22",
            "auth_type": "password",
            "credential": "",
        },
        follow_redirects=True,
    )
    assert b"App DB 2" in updated.data

    deleted = auth_client.post("/servers/1/delete", follow_redirects=True)
    assert deleted.status_code == 200
    assert b"No servers yet" in deleted.data
    assert b"db.example.com" not in deleted.data


def test_management_routes_require_login(client):
    for path in ("/dashboard", "/servers/new", "/servers/1", "/servers/1/edit"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_invalid_port_rejected(auth_client):
    response = auth_client.post(
        "/servers/new",
        data={
            "label": "Bad",
            "hostname": "host.local",
            "ssh_username": "u",
            "ssh_port": "99999",
            "auth_type": "password",
            "credential": "x",
        },
    )
    assert response.status_code == 200
    assert b"SSH port must be an integer" in response.data
