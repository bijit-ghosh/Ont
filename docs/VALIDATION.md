# Ont validation report

## Current checks

The release gate runs `python scripts/validate.py --cycles 3`. All 24 tests pass per cycle, for 72 successful test executions. Python compilation, browser JavaScript syntax, and diff whitespace checks also pass. The machine-readable result is written to `validation-report.json` and retained by GitHub CI.

| Area | Evidence |
| --- | --- |
| Workflow correctness | Human gates, demo/live separation, rejection, cancellation, required evidence, budgets, immutable snapshots |
| Worker consistency | Exclusive concurrent claims, lease expiry/recovery, stale-result rejection, heartbeat |
| Production boundary | Fail-closed secrets/hosts, auth separation, health, malformed and streamed request limits, pagination bounds |
| Storage | Persistence, artifact hashes, JSON export, consistent online backup, restored record count and SQLite integrity check |
| Synthetic load | 100 concurrent run creations across eight threads; unique IDs, successful responses, two complete pages, successful restore |
| Improvement | Held-out paired gains, safety/quality vetoes, minimum sample gate, duplicate/unpaired rejection, bounded-reward UCB selection |
| Continuous evaluation | Two scans of identical evidence produce one content-addressed report and no production promotion |

Synthetic load and reward tests validate implementation behavior; they do not establish real deployment capacity or software-generation quality. The measured local workload duration varies by machine and is not an SLA.

## Historical and current evidence boundaries

The earlier container build and 12-test container run passed. The subsequent 16-test GitHub CI release passed. The current changes require their own CI run. No updated container build, real model execution, external PR automation, neural RL training, or production rollout is claimed from these local checks.

Managed browser preview previously failed because the environment relay did not become ready. JavaScript syntax checks are not browser interaction tests. Browser/accessibility, real-world load/soak, provider cost reconciliation, independent exact-commit verification, sandbox assessment, TLS/monitoring, and deployed restore rehearsal remain explicit release gates in [OPERATIONS.md](OPERATIONS.md).

## Reproduce

Install `requirements.lock.txt`, run the release gate, inspect the report, and review CI output for the matching commit. A failed check stops the loop. Fix the cause before rerunning; do not suppress failed checks or count retries as additional independent evidence.
