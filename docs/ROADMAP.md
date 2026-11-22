# Ont delivery roadmap

## Connected repository workflow

Wire one configured model and harness to authorized immutable checkout, allowed-path patches, independent acceptance checks, and idempotent draft-PR delivery. Acceptance: a real disposable task completes with exact-commit evidence; repeats do not create duplicate external changes.

## Identity and operational reliability

Complete verified OIDC integration, connector exchange/refresh, individual actor audit, quotas, bounded retention, and deployment backup recovery. Acceptance: issuer/audience/signature and tenant-denial tests pass against the actual service; restoration is rehearsed.

## Durable distributed execution

Separate storage/domain boundaries, add durable workflow/outbox coordination and a warm-sandbox broker, and connect the native planner to atomic leases. Acceptance: fault injection establishes recovery and external-action reconciliation under representative load without bypassing quotas or isolation.

## Outcome-driven improvement

Collect consented verified outcomes, seal evaluation datasets, generate versioned candidate changes, and introduce reviewed canaries with rollback. Acceptance: measurable held-out quality/cost benefit without safety regressions. Model-weight training requires separate data rights, compute and evaluation; no neural trainer is currently bundled.

Sequence work by observed failure modes and customer tasks. Do not introduce services or additional languages without a measured need.
