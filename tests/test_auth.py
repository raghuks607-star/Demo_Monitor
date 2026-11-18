"""Unit tests for sign-in, logout, and route protection."""


def test_valid_login_redirects_to_dashboard(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "test-password"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_invalid_login_shows_error(client):
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    assert b"test-password" not in response.data
    assert b"wrong" not in response.data


def test_protected_dashboard_redirects_when_anonymous(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout_clears_session(client):
    client.post("/login", data={"username": "admin", "password": "test-password"})
    response = client.get("/dashboard")
    assert response.status_code == 200

    logout = client.get("/logout", follow_redirects=False)
    assert logout.status_code == 302

    blocked = client.get("/dashboard", follow_redirects=False)
    assert blocked.status_code == 302
    assert "/login" in blocked.headers["Location"]
