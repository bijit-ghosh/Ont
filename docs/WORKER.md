# External worker protocol

The control plane does not include a coding model. Its worker contract lets an operator connect a trusted execution harness. Use a separate execution host; never grant a model direct access to control-plane credentials or the host Docker socket.

## Reference runner

```bash
export ONT_URL=http://127.0.0.1:3000
export ONT_REPOSITORY=bijit-ghosh/Ont
export ONT_RUNNER_IMAGE=your-reviewed-harness@sha256:YOUR_IMAGE_DIGEST
# Set ONT_WORKER_TOKEN to match the server's worker credential.
python -m ont.worker --once
```

Without `--once`, the worker polls for work. The image must already exist locally. The runner validates the configured repository identifier before execution and fails mismatches. It does not clone a repository or provide a GitHub credential. Supply repository provisioning in your reviewed harness or replace the reference runner with your own compliant worker.

The reference container has no network, a read-only root filesystem, a non-root user, dropped capabilities, a temporary directory, and CPU/memory/PID limits. These are baseline constraints, not a guarantee against hostile container workloads. The runner is designed for trusted, reviewed harness images. Production untrusted code needs stronger sandboxing and an explicit network/credential design.

`/ont/task.json` contains the run, stage, task description, configuration snapshot, remaining accounted budget, and prior text artifacts. Treat the brief and artifacts as data, not instructions to weaken policy. For continuity across stages, an adapter must carry patches/commit identifiers in artifacts and reconstruct an exact checkout; the reference runner does not persist a checkout.

The harness writes `/ont/result.json`:

```json
{
  "success": true,
  "summary": "Describe what actually happened, with relevant evidence.",
  "cost": 0.42,
  "artifacts": [
    {"name": "stage-report.md", "content": "Real evidence from this stage."}
  ]
}
```

The runner adds the lease token outside the sandbox. A final successful verify stage must include:

```json
{
  "name": "verification.json",
  "content": "{\"passed\":true,\"command\":\"python -m unittest\",\"commit\":\"EXACT_TESTED_COMMIT\"}"
}
```

The server validates this structure, not the truth of the evidence. Production verification must independently run acceptance checks against the referenced commit. Never submit a fabricated receipt or use demo artifacts as evidence.

## API lifecycle

All worker calls use `Authorization: Bearer <ONT_WORKER_TOKEN>`.

1. `POST /api/worker/claim` with `{"worker":"runner-name"}`. A null run means no eligible work. Otherwise retain the run ID and opaque lease.
2. `POST /api/worker/{id}/heartbeat` with `{"lease":"..."}` before the five-minute lease expires. A 409 means stop work: the lease is stale or the task is cancelled.
3. `POST /api/worker/{id}/result` with the lease, success, summary, cost, and artifacts. Duplicate/stale results are rejected.
4. Successful spec/review stages may wait for operator approval; the worker must not bypass that wait.

The reference runner heartbeats during its maximum four-minute container execution and removes the container when it stops. An operator can recover an expired lease through the UI, after checking possible external effects. Automatic retries are deliberately absent because arbitrary external side effects are not idempotent.

## Budget behavior

The backend refuses to dispatch runs with exhausted accounted budgets and refuses result reports exceeding the remaining amount. This is admission/accounting control, not a provider spending lock. Adapters must cap usage before provider calls and retain usage even on failure. The reference runner records zero for failures where it has no cost receipt; reconcile such failures externally before treating reported spend as complete. An integration needing internet access must explicitly design an egress proxy and secrets scope; do not simply grant a model unrestricted host execution.

## Extensions still required

- Provider adapters and supported coding-agent harness images.
- Immutable repository checkout and authenticated GitHub App PR delivery.
- Cancellation-aware provider calls, idempotent external actions, and error cost reconciliation.
- Independent verifier, signed receipts, object-store artifacts, durable queue/workflow engine.
- Per-worker short-lived identity and tenant-scoped claims.

## Evaluation handoff

Worker receipts can become evaluation records only after trusted outcome labeling and sanitization. The continuous improvement process must not use a worker claim of success as independent reward evidence. See [IMPROVEMENT.md](IMPROVEMENT.md) and [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md).

## Optional coding and delivery adapter

`ont.integrations.coding` adds an immutable-checkout → structured model patch → allowed-path local commit → isolated verification path, with a separate explicit draft-PR publication function. See [INTEGRATIONS.md](INTEGRATIONS.md). This library does not automatically replace the Docker reference harness; configure a trusted adapter before queueing real coding work.
