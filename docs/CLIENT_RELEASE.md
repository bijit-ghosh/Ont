# Ont presentation release verification

This report records the presentation gate before the subsequent packaging refinement. [VALIDATION.md](VALIDATION.md) records current checks.

## Decision

The local control-plane presentation is ready to rehearse using [PRESENTATION.md](PRESENTATION.md). It demonstrates actual workflow state, persistence, human approval gates, and artifacts through explicitly labeled demo orders. It is not qualification of a connected autonomous coding/deployment service.

## Swarm review

Four parallel reviews covered backend/authentication, integration delivery, frontend controls, and container operations. The combined gate passed 49 Python tests in three consecutive cycles (147 test executions), six-view frontend render/escaping/auth/error checks, Python and JavaScript syntax checks, native scheduling tests, and address/undefined-behavior sanitizer checks. Repeated runs establish stability on these fixtures, not independent proof of production capacity.

## Defects fixed

- Startup-validated API credentials stay fixed for the process instead of being reread from mutable environment state.
- Extremely large numeric Content-Length values return a bounded error instead of a conversion failure.
- Gateway authentication failures return 401; valid credentials with forbidden roles return 403.
- Draft PR delivery requires passing verification for the exact commit and rejects an unauthorized push remote.
- Verification rejects malformed image digests, and bearer authentication requires the proper scheme.
- OAuth PKCE preserves endpoint query settings while replacing reserved flow parameters.
- Protected OpenAPI downloads use the active credential; form submissions and malformed server responses fail cleanly.
- Container health probes use an allowed Host rather than requiring loopback in every allowlist.

## Runtime evidence

A fresh non-root image built and passed network-disabled production-configured HTTP checks. The smoke test exercised all five demo stages, rejection of attempted approval bypass, both approval gates, five artifacts, zero demo charges, and completed-record persistence after container restart. A separate health probe passed with only `ont.example` allowlisted. Compose configuration validated.

The build used a temporary session CA secret; TLS verification remained enabled and no credential or CA was committed. GitHub CI repeats the matching source's release gate, build and container smoke.

## Feature status for the meeting

| Area | Status |
| --- | --- |
| Work orders, lifecycle, approvals, demo evidence | API and container HTTP validated |
| Persistence, backup restore, restart recovery | Automated fixture and container checks passed |
| Tenant routing, roles, auth boundaries | Local regression tests passed |
| Six frontend views and controls | Node render/logic tests passed; browser interaction unverified |
| Native placement and capacity advice | Compiled, unit-tested, sanitizer-checked and microbenchmarked |
| Model, PR, Kubernetes, OAuth adapters | Contract tests passed; no real external-service qualification |
| SSO, hard provider quotas, elastic cloud broker | Not complete/live-qualified capabilities |

## Limits and required next validation

Managed preview could not start because its relay timed out; no visual/browser-interaction claim is made. Real model quality, provider billing, live PR creation, Kubernetes rollout, OIDC/SSO, complete OAuth exchange, production-scale load, and infrastructure isolation need an authorized configured environment. Refer to [INTEGRATIONS.md](INTEGRATIONS.md) before presenting any optional adapter as a connected service.

## Distribution follow-up

Installable wheel/source recipes, a packaged `ont` CLI and bundled UI were subsequently added. Packaging is validated with `scripts/package_smoke.py`; the matching CI result includes both distribution and container checks. Historical presentation counts above describe that earlier gate, not a fixed total for every later release.
