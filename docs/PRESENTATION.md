# Ont client walkthrough

## Start a repeatable presentation

Use Python 3.12, install `requirements.lock.txt` and the local project (`python -m pip install --no-deps .`), then run `ont demo`. The source-checkout equivalent is:

```bash
python -m scripts.presentation
```

This prepares a separate `data/presentation.sqlite3` database and serves the application on `http://127.0.0.1:3000`. The fixture contains queued work, two human review checkpoints, and a completed demonstration, all explicitly labeled **demo**. It refuses to overwrite a previous database; use `--db data/presentation-next.sqlite3` for a fresh session. Your normal database is separate.

For preparation without starting a server, use `python -m scripts.presentation --prepare-only`. To reopen a prepared fixture:

```bash
ONT_DB=data/presentation.sqlite3 python -m uvicorn ont.app:app --host 127.0.0.1 --port 3000
```

On PowerShell, set `$env:ONT_DB='data/presentation.sqlite3'` before the uvicorn command. This local launch does not publish a public service. If tokens are configured, enter the admin token through Workspace access. Never show credentials during screen sharing.

## Five-minute walkthrough

1. **Overview:** explain the console, work orders, and why demo activity is excluded from live-delivery metrics.
2. **Work order:** open “Review a proposed implementation plan.” Inspect the brief, activity trail, and illustrative spec artifact.
3. **Approval:** approve the spec. Simulate the next stage and inspect the resulting artifact. Pause at the review gate and show that work cannot advance without approval.
4. **Completion:** inspect “Inspect a completed demonstration.” Show the trace and artifacts while keeping the demo label visible.
5. **Configuration and architecture:** inspect repository, budget and review gates; explain that new runs snapshot these settings. Show the stack and integration capability guide.

## What this presentation proves

The local product can create and persist work orders, advance its workflow, enforce human gates, inspect artifacts, import/export factory definitions, and report control-plane metrics. Automated tests cover authorization, tenants, concurrency, recovery, and integration contracts. The Docker smoke test exercises real HTTP and restart persistence.

## What requires separate qualification

The sample does not call a model, write code, create PRs, or deploy software. Live coding, authenticated external integrations, independent verification policy, SSO, provider quotas, and cloud elasticity require explicit configuration and live validation. Present optional adapters as integration code, not as already connected services. Browser validation status is recorded in the release report; passing API tests is not a substitute for a browser walkthrough.

## Recovery during the meeting

- If a port is occupied, use `--prepare-only` and launch uvicorn with a different `--port`.
- If an order is cancelled or rejected, create a new demo order rather than altering its history.
- If a presentation fixture already exists, reopen it or choose a new database path.
- If the application cannot connect, verify the process is running and `/health/ready` responds; check Workspace access if the API requires a token.
- Keep the factory-stack graphic and GitHub CI results available as a fallback. Do not describe a screenshot or diagram as live execution.
