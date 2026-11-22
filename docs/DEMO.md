# Explore the Ont workflow

## Launch

After installing Ont, run:

```bash
ont demo
```

Open `http://127.0.0.1:3000`. Ont creates an isolated database with four sample work orders: queued work, a specification awaiting approval, a build awaiting review, and a completed demonstration.

Demo orders are labeled in the interface and excluded from live completion and spending metrics. They use illustrative artifacts to exercise workflow controls without external service configuration.

## Workflow

1. Open **Work orders** and select a sample.
2. Inspect its brief, stage, activity trail and artifacts.
3. Approve the specification to advance the workflow.
4. Use **Simulate stage** to generate the next demo artifact.
5. Review the build evidence and approve the review gate.
6. Inspect the completed order and its history.

Factory configuration controls repository identity, accounted budget and review gates. New orders retain a snapshot of these settings.

## Separate workspaces

The default demo database is `data/presentation.sqlite3`. Ont preserves existing databases. To create a fresh workspace:

```bash
ont demo --db data/demo-workspace.sqlite3
```

Prepare data without starting the service:

```bash
ont demo --db data/demo-workspace.sqlite3 --prepare-only
```

Reopen that workspace from Bash:

```bash
ONT_DB=data/demo-workspace.sqlite3 ont serve
```

In PowerShell, set `$env:ONT_DB='data/demo-workspace.sqlite3'` before running `ont serve`. Use `ont serve --port 3001` when another application occupies the default port.

## Authentication and integrations

If an admin token is configured, enter it through **Workspace access**. The health endpoint is `/health/ready`. See [configuration](CONFIGURATION.md) for server settings, [operations](OPERATIONS.md) for recovery, and [integrations](INTEGRATIONS.md) to configure a live execution path.
