# Production operations and release gates

## Validated deployment scope

This release hardens the single-workspace control plane. Autonomous coding still requires an external harness and repository delivery integration. Passing control-plane tests does not verify those external systems.

## Configuration knobs

| Setting | Validation and operation |
| --- | --- |
| ONT_ENV | Set to `production` to enable fail-closed startup checks. Compose sets this. |
| ONT_ADMIN_TOKEN | Required in production, at least 32 characters; keep in a secret manager. |
| ONT_WORKER_TOKEN | Required in production, at least 32 characters, distinct from admin token. Rotate by restarting server and workers together. |
| ONT_ALLOWED_HOSTS | Explicit comma-separated hostnames without schemes or ports; wildcard forbidden in production. The Compose health probe sends a configured allowed Host; use the actual ingress hostname. |
| ONT_DB | Persistent writable SQLite path. Keep database, WAL, and SHM together. Use one control-plane deployment per database. |
| ONT_URL | Worker control-plane URL; use TLS across hosts. |
| ONT_REPOSITORY | Reference worker repository allowlist. A mismatch fails the stage. |
| ONT_RUNNER_IMAGE | Reviewed locally available harness image; pin by digest. |
| ONT_WORKER_NAME | Human-readable worker identity; this is not a separate authentication identity. |
| Factory budget | Accounted worker spend per run, positive and at most $1,000. Provider limits must enforce real spending. |
| Approval stages | Spec/review gates; changes apply only to new runs. |
| Overview limit/offset | API list defaults to 100 runs; maximum page size 500. UI currently displays the first page. |

Terminate HTTPS at the ingress. Trust forwarded headers only from that ingress, preserve the original Host, and impose connection/request rate limits there. Shared bearer credentials suit one trusted operator group; the optional tenant gateway supplies logical database separation and roles, while individual SSO and stronger multi-tenant guarantees require additional implementation.

## Health and recovery

`/health/live` checks process responsiveness. `/health/ready` checks database access. Compose probes readiness and limits memory, CPU, and process count. Readiness failure marks a container unhealthy; it does not itself restart an otherwise running process. Alert on unhealthy status, API errors, queue age, expired leases, disk utilization, and missing backups using deployment monitoring.

Expired leases require operator inspection and explicit recovery in the console. Do not requeue external side effects until checking whether they already happened. Cancellation rejects late results, but a provider or external operation must also support cancellation in its adapter.

## Consistent backup and restore

Run `python scripts/backup.py data/ont.sqlite3 /secure-backups/ont-backup.sqlite3` with an existing writable backup directory. The helper refuses to overwrite an existing backup and checks database integrity. Encrypt and restrict backups because they contain prompts, artifacts, and workflow history.

To restore: stop the service and workers, retain the current database directory for rollback, restore the backup as ONT_DB with the service user's ownership, and start with readiness checks. Do not combine a restored database with WAL/SHM files from a different database. Reconcile in-flight work and external side effects before recovering leases. Rehearse this procedure on a separate deployment before release.

## Test and repair loop

`python scripts/validate.py --cycles 3` runs the complete API suite, Python compilation, JavaScript syntax validation, and whitespace checks repeatedly. It stops on the first failure and writes a machine-readable report. Fix the cause before rerunning; retries never turn a failing test into success. CI runs the same gate on pushes, pull requests, and manual dispatch and retains the report. This is a bounded validation loop, not an unattended agent modifying production indefinitely.

## Remaining production gates

- Real browser interaction and accessibility testing, including mobile and authenticated UI.
- Workload-based load/soak tests, disk quotas, artifact retention, bounded export, and overview UI pagination.
- Dependency vulnerability scanning and dependency update policy.
- Harness sandbox escape assessment, real model cost reconciliation, repository provisioning, and end-to-end PR delivery.
- Independent verification against exact repository commits and realistic acceptance tests.
- TLS ingress, abuse controls, monitoring/alert delivery, secret rotation, and backup restoration in the actual deployment.
- Individual SSO identity, stronger audit integrity, deployed tenant-isolation review, and durable cloud execution before offering a multi-tenant service.

These are release gates to validate, not claims that those integrations are already operational.

## Improvement process operations

Run the dataset watcher as a separate unprivileged process with read-only dataset access and a writable report directory. Give it no admin token, provider keys, or deployment permission. Use your process supervisor to restart on failure; SIGTERM stops cleanly. Monitor rejected datasets and report age. Do not interpret a quiet inbox as evidence of ongoing model improvement.

## Native planner operations

Run the complete release gate on a build host with C++20 tooling. The native planner is a pure advisory component; deploying the existing Compose recipe does not enable warm pools or autoscaling. Before connecting its recommendations, implement atomic leases, cooldown, ready-capacity telemetry, quota enforcement, and provider failure recovery as specified in [PERFORMANCE.md](PERFORMANCE.md).

## Container release smoke test

Build `ont-control-plane:validated` and run `python scripts/container_smoke.py ont-control-plane:validated`. The script requires Docker at the managed/local Unix socket and creates a disposable isolated container and volume. It tests production credentials, assets, health, workflow HTTP, and restart persistence, then cleans up resources. It does not expose ports or exercise external integrations.
