# Deployment requirements

Use the checks below to prepare an environment for its intended workload. Run the release workflow against the exact source revision being deployed.

| Area | Current evidence | Remaining gate |
| --- | --- | --- |
| Local workflow | API tests and full five-stage container demonstration | Real repository task acceptance |
| Operator console | Six-view Node render/logic checks | Browser interaction, mobile visual and accessibility checks |
| Persistence | Backup/restore, concurrent run creation and container restart | Restore rehearsal and disk/retention policy in deployment |
| Tenant roles | Cross-tenant and role regression tests | Individual identity, tenant lifecycle and deployed isolation review |
| Delivery | Local Git patch tests and mocked PR/rollout contracts | Authorized live PR and deployment/rollback qualification |
| Model execution | Structured-response and endpoint contract tests | Provider credentials, real quality/billing evidence and adapter wiring |
| Learning | Paired evaluator, held-out gates, idempotent watcher and UCB tests | Trusted real outcomes, candidate generation and controlled promotion |
| Native scheduling | C++ checks, sanitizers and resident-memory microbenchmark | Broker integration, warm pools, forecast error and realistic concurrency |
| Packaging | Wheel/sdist recipes and isolated install smoke | Matching build/CI results and artifact integrity |

[VALIDATION.md](VALIDATION.md) describes the release checks and measurement boundaries.
