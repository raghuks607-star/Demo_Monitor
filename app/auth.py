"""Session auth helpers. Passwords are verified with a constant-time check."""

from functools import wraps

from flask import current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash


def verify_admin_password(password: str) -> bool:
    """Return True if password matches the configured admin hash (constant-time)."""
    password_hash = current_app.config["ADMIN_PASSWORD_HASH"]
    if not password_hash or password is None:
        return False
    return check_password_hash(password_hash, password)


def login_user(username: str) -> None:
    """Establish an authenticated session. Never store the password in the session."""
    session.clear()
    session["user"] = username
    session.permanent = False


def logout_user() -> None:
    """Clear the session."""
    session.clear()


def current_user() -> str | None:
    """Return the signed-in username, or None."""
    return session.get("user")


def login_required(view):
    """Redirect unauthenticated users to the login page."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped
