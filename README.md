# Server Monitor (Demo)

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Local-only Flask demo for viewing **live** Linux server metrics (CPU, memory, network, ports) in a read-only UI.  
**Not for production deploy** — run on the machine where Cursor is running.

See [docs/requirements.md](docs/requirements.md), [docs/TODO.md](docs/TODO.md), and [docs/ui-walkthrough.md](docs/ui-walkthrough.md).

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
flask run
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Optional local env

```bash
cp .env.example .env
# edit SECRET_KEY / ADMIN_PASSWORD_HASH / SSH_AUTO_ADD_HOST_KEYS
set -a && source .env && set +a
flask run
```

## Admin sign-in

| Setting | Default (demo) |
|---------|----------------|
| Username | `admin` |
| Password | `admin` (stored only as a **hash**) |

Env overrides: `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`.

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
```

## Server inventory & UI

1. Sign in → **Dashboard**
2. **Add server** (label, host, SSH user/port, password or PEM key)
3. **Edit** / **Delete** from the list (credentials never echoed back)
4. Open a server for a live snapshot (auto-refresh every 10s)

Inventory is stored in local SQLite: `instance/servers.db` (gitignored). Demo-only.

SSH credentials are **encrypted at rest** (Fernet key derived from `SECRET_KEY`). They are never rendered in HTML.

## SSH metrics (remote hosts)

- Collection uses Paramiko with **allowlisted** remote commands only (no free-form shell from the UI).
- Unknown host keys are **rejected** by default. For a local demo you may set `SSH_AUTO_ADD_HOST_KEYS=1` (warns in logs; demo convenience only).
- Target hosts must be Linux and reachable via SSH from this machine.
- Useful remote utilities: `/proc` (`stat`, `meminfo`, `net/dev`) and `ss` (iproute2).

## Tests & CI

```bash
source .venv/bin/activate
pytest -q
```

GitHub Actions (`.github/workflows/ci.yml`) runs pytest on push/PR with Python **3.10** and dummy env only — **no deploy**, no real SSH secrets.

Replace `OWNER/REPO` in the badge URL above with your GitHub path when you publish the repo.

## Success criteria (PRD §6)

- [x] Admin can sign in with configured credentials
- [x] Admin can add, edit, and delete a Linux server entry
- [x] Dashboard lists servers; clicking one opens details
- [x] Detail page shows CPU %, memory used/free, network RX/TX, and open ports
- [x] Detail metrics refresh automatically every 10 seconds
- [x] Failed SSH/collection shows a visible error without crashing
- [x] App runs locally via venv + pip + `flask run`

## Security (local demo)

- Do not commit `.env` or `*.db`
- Passwords verified with constant-time Werkzeug check
- CSRF protection on forms (Flask-WTF)
- Mutating routes require login
- No passwords/keys in logs or templates
