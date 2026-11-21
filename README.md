# Ont · Software Factory

Ont is an autonomous production software factory for managing and improving cloud-based coding agents at scale. Its architecture combines declarative factory definitions, recorded agent activity, sandboxed compute, swappable models and harnesses, and API-first orchestration.

This release is a runnable, single-tenant **control-plane MVP**. The production architecture and integration roadmap extend that foundation into a cloud execution platform.

## What works

- Responsive operator dashboard: work orders, activity, artifacts, approvals, factory configuration, stack view, and outcome metrics.
- Persistent SQLite storage; immutable configuration snapshots per run.
- Triage → spec → build → review → verify workflow, with configurable spec/review gates.
- Explicit demo mode; simulated artifacts never count as live completions.
- Worker claim/heartbeat/result API, exclusive leases, cancellation and expired-lease recovery.
- Required stage evidence; verification JSON required to complete live runs.
- Accounted cost limits, artifact SHA-256 hashes, and JSON workspace export.
- Factory definition import/export and machine-readable OpenAPI at `/openapi.json`.
- Docker Compose deployment and an external Docker harness bridge.

## Run locally

Requires Python 3.12+; Node is optional (only used for `npm run dev` convenience).

```bash
cd /workspace/ont
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock.txt
python -m uvicorn ont.app:app --host 127.0.0.1 --port 3000
```

Open `http://127.0.0.1:3000`. Without tokens this is a local development instance: the admin API is open and the worker API is disabled. Do not expose this mode publicly. The default repository identifier `bijit-ghosh/Ont` is a placeholder; the project has not created that GitHub repository.

Click **Explore a demo workflow**, simulate each stage, inspect artifacts, and approve spec and review. No model calls, repository changes, test execution, merges, or deployments happen in demo mode.

For a token-protected instance, set distinct `ONT_ADMIN_TOKEN` and `ONT_WORKER_TOKEN` environment variables before launching. Enter the admin token through **Workspace access**. The UI retains it in tab memory only. Worker setup is in [docs/WORKER.md](docs/WORKER.md).

## Docker deployment

```bash
# Set distinct strong ONT_ADMIN_TOKEN and ONT_WORKER_TOKEN values in your shell.
docker compose up --build -d
```

Compose binds to loopback and persists SQLite in a named volume. For remote access, terminate TLS at an authenticated reverse proxy. This MVP has shared operator/worker credentials, not individual identities or tenant isolation. Do not mount the Docker socket into the control-plane container. Run the worker on a separate trusted execution host.

## Validate

```bash
python -m unittest discover -s tests -v
node --check web/app.js
python -m compileall -q ont scripts
```

The suite verifies API authorization boundaries, concurrent claim exclusivity, state transitions, human gates, evidence requirements, stale-result rejection, budget accounting, cancellation, persistence, export, and demo/live separation. Browser preview attempted in the build environment, but the preview relay timed out; browser visual QA remains unverified. The Docker image built successfully and the same 12 tests passed inside the container. The build required the environment CA as a temporary BuildKit secret; TLS verification remained enabled. The external agent harness itself has not been exercised.

## What is not implemented

A coding agent/model provider, automatic GitHub pull requests, repository checkout provisioning, production deployment/rollback, multi-agent fan-out, semantic memory, MCP, connector OAuth, SSO/RBAC, tenant isolation, independent evidence verification, provider-side spending enforcement, and comparative evaluation infrastructure. Live work waits for a compatible external harness. The reference runner provides the transport and container boundary, not the agent itself.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the target production stack and phased build, [docs/PRODUCT.md](docs/PRODUCT.md) for the Ont product direction and evaluation strategy, and [docs/WORKER.md](docs/WORKER.md) for the execution protocol.

## Repository handoff

Source is ready as a new project at `/workspace/ont`. No existing GitHub repositories were modified. Once an empty `bijit-ghosh/Ont` repository exists, push this project using your usual Git credentials. The connected GitHub tools do not expose repository creation, and the authenticated CLI attempt was rejected with `Resource not accessible by integration (createRepository)`. An account credential with repository-creation permission or a pre-created empty repository is required. The included source archive can also be imported into your preferred IDE.

## License

MIT License. Copyright (c) 2026 Bijit Ghosh. See [LICENSE](LICENSE).
