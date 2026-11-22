# Ont performance, elasticity, and stack boundaries

## Repository review

| Existing path | Responsibility | Decision |
| --- | --- | --- |
| `web/` | Browser console, forms, REST client, rendering | Keep JavaScript/CSS/HTML independent of backend execution. No heavy UI framework is needed for current screens. Add typed API generation before expanding the console. |
| `ont/app.py` | Authentication, workflow state, approvals, artifacts | Keep Python for control-plane productivity. Split storage and domain services before adding tenants. SQLite's serialized writers make this a single-workspace deployment. |
| `ont/worker.py` | Docker launch, heartbeat, result transport | Reference integration only. Its polling and fresh-container startup are incompatible with microsecond end-to-end latency. Replace provisioning with a warm-pool broker for low-latency assignment. |
| `ont/improvement.py` | Statistical evaluation and policy learning | Keep Python for evaluation and future ML libraries. Run outside request paths. |
| `native/scheduler/` | Placement and capacity recommendations | New dependency-free Rust component for predictable local decision overhead. |
| `scripts/`, `tests/` | Release gates and operations | Validate both Python and native paths, including debug/release tests and Clippy checks. |

Adding a language is justified by a measured hot path, not by a blanket rewrite. The frontend already uses JavaScript; Python owns control and evaluation; Rust now implements native scheduling decisions. No new distributed service is required just to call the planner.

## Native planner contract

`native/scheduler/src/lib.rs` exposes:

- `select`: scans ready, unleased slots and returns the index of a fitting slot with minimum normalized-free resource score. The current score is a simple sum of spare CPU millicores and memory MiB; production profiles need workload-specific weighting. It is not a global bin-packing optimum.
- `Forecast.observe`: EWMA of observed arrivals per second. It smooths rate estimates but does not infer seasonality or claim prediction accuracy.
- `desired`: calculates capacity from arrivals, service time, queued work and drain horizon, then applies utilization/headroom, minimum/maximum limits, busy-job protection, and maximum change per decision.

The default policy is 1–100 slots, at most 10 changed per decision, 70% target utilization, a 10-second backlog drain horizon, and 20% headroom. Inputs must be finite, nonnegative, and internally consistent. A real controller must add cooldown, readiness/failure accounting, hysteresis, per-tenant quotas, and measured provider startup times. The component does not reserve resources, authorize tasks, launch containers, or persist decisions.

Build with `cargo build --locked --offline --release --manifest-path native/scheduler/Cargo.toml`. The CLI accepts lines of `arrival_rate service_seconds queued busy current` and returns desired capacity as JSON. It uses the supplied arrival rate; callers can supply EWMA output from the library. Run `bash native/scheduler/check.sh` for formatting, Clippy, debug/release tests, and a local placement benchmark.

## Latency classes

| Operation | Initial engineering target | Measurement boundary |
| --- | --- | --- |
| In-process placement decision | p99 below 10 microseconds for 256 ready-slot records | Native call only, no lock, network, allocation/provisioning, or database transaction |
| Warm sandbox assignment | p95 below 20 milliseconds within one region | Admission through exclusive lease acknowledgement; requires a ready pool |
| Warm worker start | p95 below 100 milliseconds | Assignment to harness task acknowledgement, excluding checkout/download |
| Cold sandbox provisioning | Provider-specific milliseconds to seconds | Includes VM/container startup, image pull, mount and isolation setup |
| Coding task completion | Seconds to minutes or longer | Includes model/tool calls, builds, tests, and human gates |

Only the first operation has a benchmark in this repository. It is a synthetic resident-memory scan, not a guarantee of sandbox latency. Network round trips, storage durability, isolation, and scheduler contention require separate latency budgets.

## Elastic sandbox integration design

1. Keep the Python control plane authoritative for authorization and durable stage state.
2. Introduce a broker with an inventory of warm slots grouped by image digest, region, trust boundary, CPU, memory, and network profile.
3. Feed arrival windows, service-time distributions, queue depth, busy slots, and cold-start lead time into the capacity controller. Benchmark forecast error before enabling predictive prewarming.
4. Use the native planner inside the broker process. Atomically lease the selected slot in a transactional store; if the lease loses a race, select again. A vector index is never authorization or a reservation.
5. Reset or destroy each sandbox after use. Do not reuse writable state or credentials across trust boundaries. Reserve fresh or snapshot-restored pools for different tenants.
6. Scale out before predicted demand reaches ready capacity. Scale in only after cooldown and after checking active leases. Respect hard quota and budget ceilings even when the backlog grows.
7. Record assignment latency, queue age, cold/warm ratio, startup failures, CPU/memory pressure, forecast error, and wasted warm-slot minutes.
8. Fall back to explicit queued state on pool exhaustion. Do not silently weaken isolation or exceed spending limits to satisfy latency targets.

MicroVM snapshots, gVisor runtimes, or equivalent isolation providers are adapter choices requiring deployment-specific validation. Kubernetes HPA alone does not implement ready-sandbox inventory or per-job reset.

## Current boundary

The native module is independently buildable and tested. Its output is advisory and is not connected to the existing Docker worker. Warm-pool provisioning and predictive autoscaling belong to the broker integration. Use integration fault tests, representative mixed workloads, provider quotas, and real cold/warm timing before enabling the broker in production.

## Rust implementation

The scheduler is a dependency-free Rust crate with `#![forbid(unsafe_code)]` in both library and CLI. Planning functions use typed inputs and return errors for invalid demand or resource requests. Resource scores use widened arithmetic; capacity changes use saturating arithmetic. Release builds retain overflow checks.

`bash native/scheduler/check.sh` checks formatting, runs Clippy with warnings denied, executes library and CLI tests in debug and release modes, and runs the optimized placement microbenchmark. Cargo uses the committed lockfile and offline mode after toolchain installation. The benchmark uses `std::hint::black_box` to keep the measured scan from being optimized away. Tests cover parity fixtures, capacity invariants over multiple workloads, invalid samples, stable tie-breaking, extreme counters, and streamed CLI requests.

This replaces the prior native implementation without changing the Python worker protocol or activating a sandbox broker. Rust source is included in the source distribution; the Python wheel does not embed a scheduler binary.
