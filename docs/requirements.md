# PRD: Demo Monitoring Infrastructure (Linux Servers)

## 1. Overview

Local demo web app for internal teams (L1, L2, L3, infrastructure, application development) to view **live** Linux server metrics without SSH login for routine checks.

**Problem:** Operators must log into each server to inspect CPU, memory, network, and port usage.

**Goal:** A read-only Flask UI that lists managed Linux servers and shows live snapshots collected over SSH.

**Audience:** Internal demo only. Deploy on the machine where Cursor is running.

---

## 2. Goals & Non-Goals

### Goals

- Sign in as a single admin user
- Add, edit, and delete Linux servers to monitor
- Show a dashboard of all servers
- Open a server detail page with live CPU, memory, network, and open ports
- Auto-refresh metrics every 10 seconds
- Attractive, simple, read-only metrics UI

### Non-Goals (out of scope)

- Alerts / notifications
- L1 / L2 / L3 role differences
- Windows hosts
- Historical charts or long-term metric retention
- Multi-user accounts
- Docker Compose
- Change-password UI

---

## 3. Users & Access

| Role  | Access                                      |
|-------|---------------------------------------------|
| Admin | Only account. Full access to UI and server CRUD. Metrics views are read-only. |

- Default username: `admin`
- Password: stored as a **hash** in config or environment variables
- No self-service password change screen

---

## 4. Features

### 4.1 Sign in

- Login page with username and password
- Validate against configured `admin` credentials (hashed password)
- Unauthenticated users cannot view dashboard or server pages

### 4.2 Server management

Users can manage the list of Linux hosts to monitor.

**Fields when adding / editing a server:**

| Field            | Required | Notes                                      |
|------------------|----------|--------------------------------------------|
| Label            | Yes      | Friendly display name                      |
| Hostname / IP    | Yes      | Target host                                |
| SSH username     | Yes      | Remote login user                          |
| SSH port         | Yes      | Default `22`                               |
| Auth             | Yes      | SSH password **or** private key (demo OK)  |

**Actions:** Add, Edit, Delete.

Credentials are used only by the backend to collect metrics. The UI does not expose live shell access.

### 4.3 Dashboard (server list)

- Lists all configured servers (label, host, status if available)
- Click a server to open its detail page
- Read-only for metrics; management actions limited to add/edit/delete servers

### 4.4 Server detail (live snapshot)

On open and every **10 seconds**, collect and display:

| Metric   | Display                                      |
|----------|----------------------------------------------|
| CPU      | Usage %                                      |
| Memory   | Used and free (human-readable, e.g. MB/GB)   |
| Network  | RX / TX (e.g. bytes or rates as available)   |
| Ports    | Open / listening ports                       |

- Live snapshot only — **no** historical charts or stored time series
- Collection via **SSH** into the remote Linux host using saved credentials
- Show a clear error state if SSH or remote commands fail

### 4.5 UI principles

- User-friendly, attractive layout (Flask-rendered pages + CSS; light JS for auto-refresh)
- Metrics and detail views are **read-only**
- Suitable for a local demo (not production hardening)

---

## 5. Technical requirements

| Item        | Choice                                                                 |
|-------------|------------------------------------------------------------------------|
| Language    | Python                                                                 |
| Web         | Flask                                                                  |
| UI          | Server-rendered templates + CSS (and minimal JS for 10s refresh)       |
| Collection  | SSH to remote Linux hosts                                              |
| Auth store  | Hashed admin password in config / env                                  |
| Persistence | Simple local store for server inventory (e.g. SQLite or JSON)          |
| Deploy      | Local only                                                             |

### Local run (minimal)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run
```

Open the app in a browser at the local Flask URL (default `http://127.0.0.1:5000`).

---

## 6. Success criteria (demo)

1. Admin can sign in with configured credentials  
2. Admin can add, edit, and delete a Linux server entry  
3. Dashboard lists all servers; clicking one opens details  
4. Detail page shows CPU %, memory used/free, network RX/TX, and open ports  
5. Detail metrics refresh automatically every 10 seconds  
6. Failed SSH/collection shows a visible error without crashing the app  
7. App runs locally via venv + pip + `flask run`

---

## 7. Assumptions

- Target hosts are Linux and reachable via SSH from the Cursor machine
- Demo may use password or key-based SSH auth
- Metric commands on the remote host are standard Linux utilities (implementation detail)
- Security is demo-grade (local use); not a hardened production monitoring platform
