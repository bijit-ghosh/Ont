# Ont validation report

## Current release checks

The source gate is `python scripts/validate.py --cycles 3`. The source suite contains **51 Python tests**. Three cycles execute 153 tests, alongside six-view frontend render/escaping/auth/error checks, JavaScript syntax, Python compilation, whitespace checks, native scheduler tests and Rust formatting and Clippy checks. The machine-readable report is `validation-report.json`. Repeated cycles test fixture stability; they are not independent evidence of real-service quality.

| Area | Evidence |
| --- | --- |
| Workflow | Human gates, demo/live separation, rejection, cancellation, required artifacts, budgets and immutable snapshots |
| Worker consistency | Exclusive claims, heartbeat, lease expiry/recovery and stale-result rejection |
| Access | Production credential/host checks, startup credential stability, role separation, tenant database isolation and request limits |
| Persistence | Concurrent 100-run fixture, backup/restore integrity, artifact hashes, export and container restart |
| Integrations | Controlled model, PR, rollback, OAuth, memory, MCP and spending-contract tests; local Git patch/commit tests |
| Demo workspace | Isolated fixture states, completed demo and protection against accidental overwrite |
| Frontend | Six views, escaped output, authenticated API download, login/error behavior and syntax |
| Native code | Resource fit, scaling bounds, forecast invariants, lint checks and synthetic placement timing |
| Documentation | Local links/assets exist; README badges and repository identity point to Ont |
| Distribution | Wheel/sdist build; isolated install loads bundled assets, prepares demo and reports CLI version |

## Runtime and packaging

CI builds the exact dependency lock into a non-root Docker image. The HTTP smoke covers static assets, health, authentication, all five demo stages, both review gates and bypass rejection, five artifacts, zero demo cost and completion persistence after restart. A separate health probe was tested with only an application hostname allowlisted.

The wheel smoke installs outside the checkout and imports its own bundled `ont/static/` assets. It does not rely on the source `web/` directory. Build artifacts and the validation report are retained by CI. Use the result for the exact source commit being presented or deployed.

## Measured evidence boundaries

Adapter tests use mocks where external services are involved. They do not establish live model quality/billing, actual PR publication, Kubernetes behavior, complete OAuth, SSO, provider-enforced spending or production rollout reliability. The isolated Docker checks have networking disabled and exercise the demo lifecycle.

The native microbenchmark is a resident-memory placement scan, not sandbox provisioning or end-to-end task latency. The local 100-run fixture is not a capacity or soak benchmark.

Browser interaction, responsive visual checks, and accessibility testing are separate environment-validation steps; see [deployment requirements](READINESS.md).

## Reproduce

Install `requirements.lock.txt` and compatible Node/Rust tools; run the complete source gate. For packages, install `requirements-build.txt`, run `python -m build --no-isolation` and `python scripts/package_smoke.py`. For Docker, build `ont-control-plane:validated` and run `python scripts/container_smoke.py ont-control-plane:validated`.

A failed check stops the loop. Fix the cause before rerunning; do not suppress failures or reinterpret retries as success. Build/deployment tooling can require the environment's CA bundle; keep TLS verification enabled and credentials out of artifacts.

## Native Rust migration

The migrated scheduler passes six library tests and two CLI integration tests in both debug and release profiles, including parity with the previous scheduling fixtures and capacity invariants across varied workloads. The gate also checks rustfmt and Clippy with warnings denied. Rust code forbids unsafe blocks; the native source distribution uses a committed Cargo lockfile with no third-party crate dependencies. Current performance must be taken from the Rust benchmark output rather than earlier native timing records.
