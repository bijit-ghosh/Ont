# Ont integration setup and status

## Capability inventory

| Requested capability | Implemented code | Activation and remaining validation |
| --- | --- | --- |
| Coding agent/model | HTTPS allowlisted model client produces structured patch proposals; review-first coding workflow applies allowed-path patches and creates a verified local commit | Supply a compatible chat endpoint, model, credential, allowed repository/paths and verifier image. No iterative agent tool loop or real provider execution is validated. |
| Automatic PRs | Explicit delivery function pushes an `ont/` branch and creates a draft PR, reconciling existing head/base PRs | Trusted GitHub credential and repository authorization required. It never merges. Concurrent PR creation can still race; production needs an external-action ledger. |
| Checkout provisioning | Allowlisted GitHub clone and exact 40-character detached commit | Needs network and trusted Git credentials on execution host. No recursive submodule initialization. |
| Deployment/rollback | Allowlisted Kubernetes target, digest-pinned image rollout, status check, undo and readiness on failure | Supply kubectl context and independently approved release. Rollback errors propagate. No deployment has been performed. |
| Multi-agent fan-out | Bounded thread-pool helper, maximum 16 workers and 100 tasks, exceptions propagate | Configure actual worker functions. Not a durable distributed child-workflow scheduler. |
| Semantic memory | Tenant-scoped SQLite storage and cosine ranking of caller-supplied embeddings | Supply trusted tenant identity and an embedding function. No extraction, expiry, quotas, or production vector index yet. |
| MCP | Local stdio initialize, ping, tool listing and read-only capability tool | Run `python -m ont.integrations.mcp`. No authenticated remote MCP or run-control tools yet. |
| Connector OAuth | PKCE challenge and one-use five-minute state transaction | Provider-specific token exchange, encrypted refresh-token storage and callbacks still required. In-memory state is process-local. |
| SSO/RBAC | Role-based bearer gateway; separate reader/admin/worker roles | OIDC ingress and verified token exchange still required for SSO. Do not trust raw identity headers or call PKCE a complete SSO integration. |
| Tenant isolation | Gateway routes trusted principals to separate tenant database files; tenant cannot be selected by request data | Run the gateway entry point. Default app remains single-tenant. Files share one host process; this is not hard infrastructure isolation. |
| Independent verification | Operator-supplied checks run in separate no-network resource-limited Docker container against a clean exact commit | Actual Docker integration and trusted test policy required. Current workflow server still accepts worker evidence; separate verifier identity and signed receipts are not enforced there. |
| Spending enforcement | Transactional local reservations and usage settlement; failures keep reservations until reconciled | This is local admission accounting, not provider-side hard spending enforcement. Configure provider quotas; the model client is not automatically coupled to the ledger or provider invoice reconciliation. |
| Comparative evaluation | Paired holdout evaluator, task-level bootstrap bounds, continuous dataset reports and UCB primitive | Trusted real task labels and sealed datasets required. No neural trainer or automatic policy deployment. |

## Tenant gateway

Set `ONT_PRINCIPALS` to a JSON map of distinct 32+ character external tokens to objects containing `tenant` (alphanumeric identifier) and `role` (`admin`, `reader`, or `worker`). Keep this configuration in a secret store. Set distinct internal `ONT_ADMIN_TOKEN` and `ONT_WORKER_TOKEN` and `ONT_TENANT_DATA` to the persistent tenant directory.

Launch `python -m uvicorn ont.gateway:application --factory --host 127.0.0.1 --port 3000`. Production also requires `ONT_ENV=production` and explicit `ONT_ALLOWED_HOSTS`. The gateway maps credentials to tenants before routing protected API calls. Each tenant gets its own database; external requests cannot supply a tenant override. Reader writes and admin access to worker claims are rejected. The UI/static assets are shared and carry no tenant records.

Rotate external keys through a gateway restart. The current audit trail identifies role operations through shared tenant credentials, not individual OIDC subjects. Per-user immutable audit identity, API rate limits and production tenant lifecycle management remain required.

## Coding and delivery path

Use `ont.integrations.coding.build_change` from a trusted worker adapter. It checks out an allowed immutable commit, calls a configured model for a patch, applies it without a shell, restricts changed paths, rejects changed symlinks, creates a local commit with hooks disabled, and invokes separate container verification. It returns evidence and usage. `publish_draft` is a separate explicit step; it requires an unchanged commit and an authorized repository. Never run this workflow against an untrusted checkout on a privileged control-plane host.

Provider calls, GitHub access, and Kubernetes control need separate least-privilege identities. Keep model keys outside sandbox execution. The offline Docker reference runner does not gain internet access just because these adapters exist. Deploy adapters through a broker with explicit network and credential policy.

## Live qualification checklist

Use a disposable authorized repository, provider quota, pinned verifier image, and test namespace. Confirm exact checkout, allowed-path patching, verification failure blocking, repeated PR reconciliation, cancellation, usage reconciliation, and rollout failure/undo. Test actual SSO issuer/audience/signature/expiry validation at the identity ingress before relying on it. Record these outcomes separately from mocked adapter tests.

No external provider credentials or release targets were configured during this implementation. Live publication or deployment is therefore not evidence established by the current test suite.
