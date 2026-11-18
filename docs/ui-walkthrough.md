# UI walkthrough — server inventory

Local demo only. Sign in first (`admin` / `admin` unless you overrode the hash).

## Add a server

1. Open **Dashboard** → **Add server** (or nav **Add server**).
2. Fill **Label**, **Hostname / IP**, **SSH username**, **SSH port** (default `22`).
3. Choose auth type: **password** or **private key (PEM)**.
4. Paste the SSH password or PEM key (stored encrypted; never shown again).
5. Submit → returns to the dashboard list.

## Edit a server

1. On the dashboard row, click **Edit**.
2. Change label/host/user/port/auth as needed.
3. Leave the credential field blank to keep the existing secret; fill it only to replace.
4. Save → dashboard.

## Delete a server

1. Click **Delete** on the row.
2. Confirm the browser dialog.
3. The host is removed from local SQLite inventory.

## View live metrics

1. Click the server **label** or **View**.
2. Read-only CPU, memory, network, and ports refresh every **10 seconds**.
3. SSH failures show an error panel without crashing the app.
