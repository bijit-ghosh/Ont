# Enterprise evaluation results

Evaluated source: `6da1f9a1577c3e055801c640ad1703990fdc9ac7`. Profile: **deployment**. Working tree: clean. Source unchanged during execution.

Source fingerprint: `af6a4ee464872b87b0bb5d850464cc82eee6e8c62afee012a2d5c247d0a1fcfd`.

**21 passed · 0 failed · 7 blocked.** Automated profile gate passed; enterprise qualification remains blocked by the acceptance requirements below.

| Architecture layer | Passed | Failed | Blocked |
| --- | ---: | ---: | ---: |
| Factories As Code | 3 | 0 | 1 |
| Data And Evidence | 3 | 0 | 1 |
| Compute And Elasticity | 3 | 0 | 1 |
| Inference And Agents | 3 | 0 | 1 |
| Evaluation And Learning | 3 | 0 | 1 |
| Orchestration And Policy | 3 | 0 | 1 |
| Access And Delivery | 3 | 0 | 1 |

## Enterprise acceptance requirements

| Gate | Required evidence or implementation |
| --- | --- |
| FAC-E1 | Implement signed factory/version provenance and promotion authorization; demonstrate rollback. |
| DAT-E1 | Run deployed retention/deletion and backup restore with agreed RPO/RTO and residency requirements. |
| CMP-E1 | Connect isolated pool broker and exercise escape assessment, quotas, exhaustion and reset boundaries. |
| INF-E1 | Configure an authorized provider, reconcile invoiced usage, and implement hard provider budget controls. |
| EVA-E1 | Supply consented frozen task corpus with independent acceptance criteria; measure success, total cost and reviewer time. |
| ORC-E1 | Complete OIDC identity validation and durable scheduler; fault-inject restarts, revocation and cross-host retries. |
| ACC-E1 | Run browser/assistive checks and real authorized GitHub/Kubernetes acceptance tests. |

## Use the results

The executable scenarios cover controlled local behavior, mock adapter contracts, real local Git operations, Rust and frontend checks, and a real network-disabled Docker lifecycle/restart test. They do not establish live provider quality, infrastructure isolation certification or a production SLA.

[Run the same catalog](../evals/README.md) and retain the report, source/catalog hashes and per-case logs. CI publishes the evidence directory as an artifact. The [adoption guide](ENTERPRISE_EVALUATION.md) maps remaining gates to enterprise owners and rollout phases.
