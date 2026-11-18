# TODO: Demo Monitoring Infrastructure (Linux)

Small, AI-assisted increments for the local Flask demo described in [requirements.md](requirements.md).  
Check off items as you complete them. Keep each step mergeable and demo-safe.

---

## Phase 0 — Project initialization & basic UI

- [x] **0.1** Create project layout (`app/`, `tests/`, `docs/`, `templates/`, `static/`) and empty `__init__.py` files
- [x] **0.2** Add `requirements.txt` (Flask, pytest, and pinned deps only) plus `.gitignore` (venv, `__pycache__`, `.env`, secrets)
- [x] **0.3** Add minimal Flask app factory that serves a home/placeholder page
- [x] **0.4** Add basic attractive UI shell (layout template, CSS, nav placeholder) — **read-only** content only
- [x] **0.5** **Security:** Ensure no secrets in repo; document that `.env` is local-only
- [x] **0.6** **Docs:** Short “how to run” section in `README.md` (`venv` → `pip install` → `flask run`)

---

## Phase 1 — Sign-in & unit tests

- [x] **1.1** Add config for default username `admin` and a **hashed** password (env/config; never store plaintext)
- [x] **1.2** Implement login page (username + password form) and session-based sign-in
- [x] **1.3** Protect dashboard/routes: unauthenticated users redirect to login
- [x] **1.4** Add logout and clear session on logout
- [x] **1.5** **Security:** Use constant-time password verify; set `SECRET_KEY` from env; no password in logs/templates
- [x] **1.6** Unit tests: valid login, invalid login, protected route redirect, logout
- [x] **1.7** **Docs:** Document default admin setup and how to set `SECRET_KEY` / password hash in `README.md`

---

## Phase 2 — Persistence for server inventory

- [x] **2.1** Choose simple local store (SQLite preferred for demo) and add connection helpers
- [x] **2.2** Define server model/fields: label, hostname/IP, SSH username, SSH port, auth type, credential material
- [x] **2.3** Implement create / list / get / update / delete for servers (backend only)
- [x] **2.4** **Security:** Encrypt or otherwise avoid plaintext secrets in DB if practical for demo; never render SSH passwords/keys in HTML
- [x] **2.5** Unit tests for CRUD (happy path + missing server)
- [x] **2.6** **Docs:** Note where inventory is stored and that it is local-demo only

---

## Phase 3 — Server management UI (CRUD)

- [x] **3.1** Dashboard page: list servers (label, host, basic status placeholder) — metrics remain read-only
- [x] **3.2** Add-server form (required fields from PRD; default SSH port `22`)
- [x] **3.3** Edit-server form (pre-filled; do not echo stored secret back to the browser)
- [x] **3.4** Delete-server action with simple confirmation
- [x] **3.5** Wire nav links: Dashboard ↔ Add Server; require login on all management routes
- [x] **3.6** **Security:** CSRF protection on forms; validate/sanitize inputs (host, port range); authorize all mutating routes
- [x] **3.7** Unit/integration tests for add/edit/delete via app client
- [x] **3.8** **Docs:** Screenshot or short UI walkthrough for add/edit/delete in `README.md` or `docs/`

---

## Phase 4 — SSH metrics collection (backend)

- [x] **4.1** Add SSH client helper (connect with password or private key; short timeout)
- [x] **4.2** Collect CPU usage % via remote Linux commands
- [x] **4.3** Collect memory used/free (human-readable)
- [x] **4.4** Collect network RX/TX
- [x] **4.5** Collect open/listening ports
- [x] **4.6** Return structured result or clear error (do not crash app on SSH failure)
- [x] **4.7** **Security:** Disable unknown-host auto-accept in a documented demo way or warn; never log private keys/passwords; command allowlist only (no free-form remote shell from UI)
- [x] **4.8** Unit tests with mocked SSH (success + failure paths)
- [x] **4.9** **Docs:** List required remote Linux utilities and SSH reachability assumption

---

## Phase 5 — Server detail page & auto-refresh

- [x] **5.1** Server detail route/page: show label, host, and live snapshot fields
- [x] **5.2** Display CPU, memory, network, ports in a clear read-only layout
- [x] **5.3** Show visible error state when collection fails
- [x] **5.4** Auto-refresh every **10 seconds** (minimal JS or meta refresh)
- [x] **5.5** Dashboard: link each server row to its detail page; optional lightweight status
- [x] **5.6** **Security:** Detail view remains read-only; no shell/command input; keep auth required
- [x] **5.7** Tests: detail page authenticated access; error rendering when collector fails
- [x] **5.8** **Docs:** Update success criteria checklist in `README.md` (matches PRD §6)

---

## Phase 6 — CI/CD (GitHub Actions) & polish

- [x] **6.1** Add `.github/workflows/ci.yml`: install deps, run pytest on push/PR
- [x] **6.2** Pin Python version in CI to match local demo
- [x] **6.3** Fail CI on test failures; keep workflow minimal (no deploy — local-only app)
- [x] **6.4** **Security:** CI uses dummy env/`SECRET_KEY` and test password hash only; no real SSH secrets in Actions
- [x] **6.5** Final UI polish pass (spacing, empty states, consistent error messages)
- [x] **6.6** **Docs:** Document CI badge/status and “local run only” (no production deploy) in `README.md`
- [x] **6.7** Final demo smoke check against PRD success criteria

---

## Suggested order (do not skip ahead)

1. Phase 0 → runnable UI shell  
2. Phase 1 → sign-in + tests  
3. Phase 2 → data layer  
4. Phase 3 → server CRUD UI  
5. Phase 4 → SSH metrics  
6. Phase 5 → detail + 10s refresh  
7. Phase 6 → GitHub Actions + polish  

---

## Definition of done (each checkbox)

- Works locally with `venv` + `pip install -r requirements.txt` + `flask run`
- Includes the security note for that step
- Includes/updates the documentation for that step
- Adds or updates tests when the phase introduces logic
