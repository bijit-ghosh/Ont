# Enterprise evaluation and adoption

## Purpose

Evaluate Ont against engineering controls and an enterprise's intended workload. The suite separates automated component evidence from live-service qualification. It is an acceptance framework, not certification or a claim that every planned cloud capability is implemented.

Run the [evaluation suite](../evals/README.md) and retain its JSON report, scorecard and evidence logs alongside the exact source revision and deployment configuration.

## Architecture-layer acceptance matrix

| Layer | Executable scenarios | Enterprise acceptance gate | Enterprise owner |
| --- | --- | --- | --- |
| Factories as code | Schema rejection, configuration/budget snapshots, demo separation | Signed version provenance, reviewed promotion and rollback | Platform engineering / release governance |
| Data & evidence | Artifact history/export, scoped retrieval, concurrent write + backup/restore | Residency, retention/deletion, deployed RPO/RTO and integrity controls | Data platform / security / operations |
| Compute & elasticity | Rust placement/capacity checks, verifier guardrails, real container lifecycle/restart | Sandbox isolation assessment, ready-pool provisioning, quotas, reset and failure recovery | Infrastructure / SRE / security |
| Inference & agents | Endpoint/output contracts, budget reservation concurrency, real Git patch boundaries | Authorized model performance, invoice reconciliation and hard provider spending limits | AI platform / finance / engineering |
| Evaluation & learning | Safety/quality vetoes, paired holdout integrity, idempotent reports and bounded rewards | Consented representative corpus and independent outcome labeling | Engineering quality / evaluation owners |
| Orchestration & policy | Approval/evidence gates, replay/cancellation/lease races, cross-tenant role denial | Verified identity, revocation, durable cross-host execution and retry reconciliation | Identity / platform / SRE |
| Access & delivery | Frontend logic, exact-commit PR guards, rollback contracts and PKCE replay | Real browser/accessibility checks and authorized PR/release delivery | Developer experience / release engineering |

## Adoption ladder

### 1. Isolated evaluation

Install from source in a disposable workspace. Run the core profile and inspect all negative scenarios. Agree on data classification and repository permissions. Exit criterion: automated core scenarios pass, and all blocked gates have named owners and acceptance artifacts.

### 2. Internal control-plane pilot

Deploy with production credentials, TLS ingress, persistent storage, monitoring and backup policy. Run the deployment profile. Rehearse operator approval, cancellation, backup restore and restart recovery. Exit criterion: deployment checks pass in the target environment and identity/data boundaries meet the pilot's access model.

### 3. Connected repository pilot

Use a disposable authorized repository, a capped provider account, fixed verification image and non-production release target. Run real task-to-PR acceptance checks and deliberately fail verification/rollout paths. Reconcile billed usage and ambiguous network outcomes. Exit criterion: independent evidence for exact commits, no duplicate external changes in retry tests, and approved spending/access controls.

### 4. Workload qualification

Evaluate a frozen task set drawn from actual engineering work. Include bug fixes, tests, refactoring, dependency changes, configuration and infrastructure tasks, plus adversarial context and permission-denial cases. Separate training from held-out evaluation and count independent tasks rather than repeated seeds. Measure acceptance success, reviewer minutes, full billed cost, latency, revert rate and incidents. Agree thresholds before executing; this repository supplies no universal SLA.

### 5. Controlled expansion

Expand repositories and task risk only after incident recovery and access reviews. Introduce distributed execution, warm pools or model/policy changes through reviewed canaries with rollback. Maintain a baseline and rerun acceptance after every material configuration change.

## Enterprise contribution opportunities

- Supply consented task corpora, immutable starting commits, and independently owned acceptance checks.
- Provide scoped test accounts for model, GitHub, OIDC and non-production Kubernetes qualification.
- Implement missing controls: signed provenance, verified SSO, durable scheduling, sandbox broker, hard provider quotas and independent receipt enforcement.
- Define retention, residency, audit, recovery, accessibility and workload objectives with accountable owners.
- Return reproducible failures as regression scenarios rather than modifying expected outcomes to force a pass.

## Required evidence package

Archive source/catalog hashes, trusted build identity, exact environment configuration without secrets, scenario logs, test receipts, provider usage records, approval decisions, restore results and exception expiry. Distinguish mock/fixture evidence from live deployment evidence. A blocked requirement remains blocked until a trusted producer can demonstrate the corresponding control.

## Current evaluation boundary

The automated profiles exercise local fixtures and controlled adapter contracts across every layer, including a real network-disabled Docker demo. They do not train a model, certify isolation, complete SSO, enforce provider billing limits, or qualify a connected elastic service. `--require-enterprise` returns a non-success exit while those acceptance gates remain incomplete.
