"""HTTP routes for the demo monitoring UI."""

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import (
    current_user,
    login_required,
    login_user,
    logout_user,
    verify_admin_password,
)
from app.metrics import collect_metrics
from app.servers import (
    create_server,
    delete_server,
    get_server,
    get_server_with_credential,
    list_servers,
    update_server,
)
from app.validators import validate_server_payload

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page (public, read-only shell)."""
    return render_template("index.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Sign in with the configured admin account."""
    if current_user() is not None:
        return redirect(url_for("main.dashboard"))

    error = None
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        expected = current_app.config["ADMIN_USERNAME"]

        if username == expected and verify_admin_password(password):
            login_user(username)
            next_url = request.args.get("next") or url_for("main.dashboard")
            if not next_url.startswith("/"):
                next_url = url_for("main.dashboard")
            return redirect(next_url)

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@bp.route("/logout", methods=["POST", "GET"])
def logout():
    """Clear session and return to home."""
    logout_user()
    flash("Signed out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@login_required
def dashboard():
    """List managed Linux servers (metrics remain read-only on detail pages)."""
    servers = list_servers()
    return render_template("dashboard.html", servers=servers)


@bp.route("/servers/new", methods=["GET", "POST"])
@login_required
def server_new():
    """Add a Linux server to the inventory."""
    errors: list[str] = []
    form = {
        "label": "",
        "hostname": "",
        "ssh_username": "",
        "ssh_port": "22",
        "auth_type": "password",
    }

    if request.method == "POST":
        form = {
            "label": request.form.get("label", ""),
            "hostname": request.form.get("hostname", ""),
            "ssh_username": request.form.get("ssh_username", ""),
            "ssh_port": request.form.get("ssh_port", "22"),
            "auth_type": request.form.get("auth_type", "password"),
        }
        cleaned, errors = validate_server_payload(
            label=form["label"],
            hostname=form["hostname"],
            ssh_username=form["ssh_username"],
            ssh_port=form["ssh_port"],
            auth_type=form["auth_type"],
            credential=request.form.get("credential", ""),
            require_credential=True,
        )
        if cleaned:
            server = create_server(
                label=cleaned["label"],
                hostname=cleaned["hostname"],
                ssh_username=cleaned["ssh_username"],
                ssh_port=cleaned["ssh_port"],
                auth_type=cleaned["auth_type"],
                credential=cleaned["credential"],
            )
            flash(f"Added server “{server['label']}”.", "info")
            return redirect(url_for("main.dashboard"))

    return render_template(
        "server_form.html",
        mode="create",
        form=form,
        errors=errors,
        server=None,
    )


@bp.route("/servers/<int:server_id>/edit", methods=["GET", "POST"])
@login_required
def server_edit(server_id: int):
    """Edit a server. Stored secrets are never echoed back to the browser."""
    server = get_server(server_id)
    if server is None:
        abort(404)

    errors: list[str] = []
    form = {
        "label": server["label"],
        "hostname": server["hostname"],
        "ssh_username": server["ssh_username"],
        "ssh_port": str(server["ssh_port"]),
        "auth_type": server["auth_type"],
    }

    if request.method == "POST":
        form = {
            "label": request.form.get("label", ""),
            "hostname": request.form.get("hostname", ""),
            "ssh_username": request.form.get("ssh_username", ""),
            "ssh_port": request.form.get("ssh_port", "22"),
            "auth_type": request.form.get("auth_type", "password"),
        }
        credential = request.form.get("credential", "")
        cleaned, errors = validate_server_payload(
            label=form["label"],
            hostname=form["hostname"],
            ssh_username=form["ssh_username"],
            ssh_port=form["ssh_port"],
            auth_type=form["auth_type"],
            credential=credential,
            require_credential=False,
        )
        if cleaned:
            update_server(
                server_id,
                label=cleaned["label"],
                hostname=cleaned["hostname"],
                ssh_username=cleaned["ssh_username"],
                ssh_port=cleaned["ssh_port"],
                auth_type=cleaned["auth_type"],
                credential=credential.strip() or None,
            )
            flash(f"Updated server “{cleaned['label']}”.", "info")
            return redirect(url_for("main.dashboard"))

    return render_template(
        "server_form.html",
        mode="edit",
        form=form,
        errors=errors,
        server=server,
    )


@bp.route("/servers/<int:server_id>/delete", methods=["POST"])
@login_required
def server_delete(server_id: int):
    """Delete a server after confirmation POST."""
    server = get_server(server_id)
    if server is None:
        abort(404)
    delete_server(server_id)
    flash(f"Deleted server “{server['label']}”.", "info")
    return redirect(url_for("main.dashboard"))


@bp.route("/servers/<int:server_id>")
@login_required
def server_detail(server_id: int):
    """Read-only live metrics snapshot with 10s auto-refresh."""
    server = get_server(server_id)
    if server is None:
        abort(404)

    full = get_server_with_credential(server_id)
    snapshot = collect_metrics(full) if full else None
    return render_template(
        "server_detail.html",
        server=server,
        metrics=snapshot.to_dict() if snapshot else {"ok": False, "error": "Unavailable"},
        refresh_seconds=10,
    )
