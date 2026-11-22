# Release readiness

Readiness is assessed per capability, deployment, and exact source revision. An architecture diagram or adapter class does not establish live operation.

| Area | Current evidence | Remaining gate |
| --- | --- | --- |
| Local workflow | API tests and full five-stage container demonstration | Real repository task acceptance |
| Operator console | Six-view Node render/logic checks | Browser interaction, mobile visual and accessibility checks; preview relay previously failed |
| Persistence | Backup/restore, concurrent run creation and container restart | Restore rehearsal and disk/retention policy in deployment |
| Tenant roles | Cross-tenant and role regression tests | Individual identity, tenant lifecycle and deployed isolation review |
| Delivery | Local Git patch tests and mocked PR/rollout contracts | Authorized live PR and deployment/rollback qualification |
| Model execution | Structured-response and endpoint contract tests | Provider credentials, real quality/billing evidence and adapter wiring |
| Learning | Paired evaluator, held-out gates, idempotent watcher and UCB tests | Trusted real outcomes, candidate generation and controlled promotion |
| Native scheduling | C++ checks, sanitizers and resident-memory microbenchmark | Broker integration, warm pools, forecast error and realistic concurrency |
| Packaging | Wheel/sdist recipes and isolated install smoke | Matching build/CI results; no public registry release claimed |

[CLIENT_RELEASE.md](CLIENT_RELEASE.md) records the presentation gate. [VALIDATION.md](VALIDATION.md) records historical evidence and limits. Always use the workflow result for the commit being presented or deployed.
