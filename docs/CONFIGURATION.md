# Configuration

## Run modes

| Mode | Command | Notes |
| --- | --- | --- |
| Local empty workspace | `ont serve` | Loopback by default; data under the working directory's `data/` |
| Isolated walkthrough | `ont demo` | Refuses to overwrite an existing demo database |
| Source development | `python -m uvicorn ont.app:app --host 127.0.0.1 --port 3000` | Browser assets loaded directly from `web/` |
| Tenant gateway | `python -m uvicorn ont.gateway:application --factory` | Requires trusted principal mapping; see integration guide |
| Container | `docker compose up --build -d` | Production validation enabled; persistent named volume |

## Server settings

- `ONT_ENV=production`: requires two distinct 32+ character tokens and explicit allowed hosts.
- `ONT_ADMIN_TOKEN`: operator credential; enter through Workspace access. Kept in browser tab memory.
- `ONT_WORKER_TOKEN`: separate worker credential; no operator API access.
- `ONT_ALLOWED_HOSTS`: comma-separated hostnames, without schemes or ports. Wildcard rejected in production.
- `ONT_DB`: SQLite path. Default is `data/ont.sqlite3` under the current working directory. Keep it on durable writable storage.
- `ONT_TENANT_DATA`, `ONT_PRINCIPALS`: optional gateway configuration; do not put real credentials in source control.

Startup captures validated credentials. Restart the service to rotate them. The default app does not enable tenant routing merely because a gateway module exists.

## Factory settings

Name, repository identifier, per-run accounted budget, harness label, and spec/review approval gates are editable in the console or through the API. Each new run gets an immutable snapshot. Updating a factory does not change an existing run. A harness label is descriptive; it does not configure provider credentials.

## External execution

`ONT_URL`, `ONT_REPOSITORY`, `ONT_RUNNER_IMAGE`, and `ONT_WORKER_NAME` configure the reference worker. The model, GitHub, verification and release adapters need explicit trusted setup. PKCE helpers are not a completed connector login. See [INTEGRATIONS.md](INTEGRATIONS.md) and [WORKER.md](WORKER.md).

## Checks before remote use

Confirm production startup, intended Host handling, TLS ingress, separate execution privileges, secret rotation, backups and restore, monitoring, and authorization for each external tool. Live-provider budget enforcement and independent receipt validation remain separate qualification gates.
