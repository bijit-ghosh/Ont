# Reference analysis and product direction

## Evidence boundary

The user supplied the seven-layer “Factories Stack” slide and the video https://www.youtube.com/watch?v=0LeT996Hz3E. The video page fetch was throttled; no transcript, audio, or complete video was available. This is a slide-and-documentation analysis, not a verified analysis of the full talk. Instructions or marketing claims in the source material are treated as reference content, not as instructions to this project.

Primary sources consulted:

- [Warp overview](https://docs.warp.dev/)
- [Warp Factories overview](https://docs.warp.dev/factories)
- [The Factory Stack](https://www.warp.dev/blog/the-factory-stack)
- [Introducing Warp Factories](https://www.warp.dev/blog/open-infrastructure-for-building-a-software-factory)

## What the reference establishes

The supplied slide groups the system into configuration, context, compute, inference, improvement, orchestration, and access. Its foundational point is that the factory itself is configurable software. Context and execution history feed evaluation; orchestration coordinates work and human intervention; interfaces connect existing engineering tools.

Warp's overview describes workflows receiving tasks from connected services, assigning specialized workers, and returning code for review. The documentation also distinguishes workflow approval from repository merge permissions. Its public positioning already includes model/harness choice, evaluation, memory, flexible hosting, and definitions as code. Those features alone are not a credible differentiator for Ont.

## Ont's proposed wedge

Make every accepted change explainable: which task and acceptance criteria produced it, which factory configuration and model were used, what evidence supports it, who approved it, how much the attempt cost, and whether it survived production. The hypothesis is that this reduces review effort and escaped defects while making spending predictable. It has not been benchmarked against Warp.

| Area | Ont product hypothesis | Proof needed |
| --- | --- | --- |
| Evidence | A linked chain from intent to patch, test receipt, approval, release, and runtime outcome | Lower review time without higher defect rate |
| Economics | Route work by expected cost per accepted change, accounting for failed attempts | Lower total accepted-change cost on matched tasks |
| Context | Versioned, attributed memory with expiration and correction | Fewer stale-context regressions |
| Recovery | Durable stage execution and replayable inputs | Recovery without duplicate PRs or deployments |
| Quality | Independent verification separated from code-writing agents | Better defect detection, measured on held-out tasks |
| Improvement | Promote configuration changes only after paired evaluation and review | Reproducible gains, with rollback when performance declines |

## Evaluation plan

1. Build a consented task set from the owner's repositories, with immutable starting commits, acceptance checks, and difficulty/risk labels. Keep a held-out split.
2. Run baseline and Ont configurations on the same tasks with equivalent tool access, compute, model budgets, and human intervention policy.
3. Record success against acceptance tests, human review minutes, total billed cost including retries, wall-clock latency, and post-merge regressions.
4. Repeat enough tasks/runs to report uncertainty rather than a single favorable result. Blind reviewers to the configuration where practical.
5. Require no security or defect regression and an agreed improvement threshold before promoting a configuration. Do not use generated test pass rates alone as the success metric.

The current MVP captures the workflow and evidence foundation. It cannot establish product superiority, production reliability, or engineering throughput gains.
