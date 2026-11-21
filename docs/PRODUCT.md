# Ont product direction

Ont is an autonomous production software factory that manages and improves cloud-based coding agents at scale. Teams define how software should be built, run agents in controlled environments, retain evidence of the work, and use measured outcomes to improve the factory.

## Platform principles

### Factories as code

Declare workflows, agent roles, policies, budgets, review gates, and triggers in versioned configuration. Support branching, validation, dry runs, and promotion of configurations through review. Every execution references an immutable factory version.

### Data and context

Record agent actions, conversations, tool calls, generated artifacts, screenshots, and videos with run and stage attribution. Retain source provenance, access policies, and retention controls. This activity becomes the evidence for debugging, evaluation, and improvement. The current release stores text artifacts, run metadata, and lifecycle events; full multimodal recording is planned.

### Compute

Execute tasks in sandboxed, repeatable environments with declared dependencies, resource limits, scoped credentials, and controlled network access. Separate execution infrastructure from the control plane. The current release includes an external Docker runner contract; stronger isolation and cloud provisioning are planned.

### Inference

Treat models and agent harnesses as replaceable components. Evaluate quality, latency, and total cost on representative tasks before changing routing policy. Support provider choice and explicit usage accounting. The current release accepts external harness results; provider integrations and model routing are planned.

### Orchestration and APIs

Move tasks through defined stages with durable state, explicit permissions, human checkpoints, and observable failures. Expose operations through APIs and MCP so teams can use Ont from GitHub, Slack, Linear, and other engineering tools. The current release provides REST/OpenAPI and a worker lifecycle; MCP and service adapters are planned.

## Improvement loop

Record → evaluate → propose → benchmark → review → promote → observe.

Make every accepted change explainable: task and acceptance criteria, configuration version, model/harness identity, supporting evidence, approvals, total cost, and production outcome. Improvements remain hypotheses until measured on representative tasks.

| Outcome | Measurement |
| --- | --- |
| Quality | Acceptance-check success and post-release regressions |
| Economics | Total billed cost per accepted change, including retries and failed attempts |
| Review effort | Human minutes spent understanding and approving evidence |
| Reliability | Recovery success without duplicate external actions |
| Context quality | Stale-context failures and provenance coverage |
| Delivery speed | End-to-end latency, including queues and review waits |

## Evaluation strategy

1. Build a consented task set from selected repositories with immutable starting commits, acceptance checks, and difficulty/risk labels. Keep a held-out split.
2. Compare factory configurations on the same tasks with equivalent compute, budgets, tool access, and intervention policy.
3. Record acceptance outcomes, review minutes, actual billed costs, latency, and regressions. Keep demo activity out of these measurements.
4. Repeat runs and report uncertainty. Blind reviewers to configuration when practical.
5. Require agreed quality and cost thresholds before promoting a configuration; preserve rollback to the previous version.

The current release establishes workflow and evidence capture. Production throughput and quality improvements require real integrations and measured deployment outcomes.

## Improvement implementation

The release includes paired held-out evaluation, task-level uncertainty estimation, a bounded-reward UCB selector, and an idempotent continuous dataset watcher. Candidate generation, real provider learning, canary deployment, and automatic rollback remain integration work. See [IMPROVEMENT.md](IMPROVEMENT.md).
