# Validation record

- Python application and worker compile successfully.
- Browser JavaScript passes `node --check`.
- All 12 API tests pass on the workspace runtime.
- Docker image `ont-control-plane:0.1` builds successfully using the normal Dockerfile with a session-only CA secret added to a temporary Dockerfile. The source Dockerfile was not changed to disable TLS or embed the CA.
- All 12 API tests also pass in that non-root container with networking disabled.
- `requirements.lock.txt` captures the dependency versions installed in the successful container build. It does not include cryptographic package hashes.
- CI configuration is included but has not run on GitHub.
- Managed browser preview failed because its relay did not become ready. No browser visual or interaction test is claimed.
- GitHub repository creation was attempted through the authenticated CLI and rejected: `Resource not accessible by integration (createRepository)`. No remote was created and no code was pushed.
- Product direction incorporates the supplied platform requirements. Full video analysis was unavailable.
- Real agent execution, model billing, PR delivery, and production deployment remain unverified and need external integrations.

## Hardening validation

Added four production regression tests covering fail-closed credentials/host configuration, health/auth boundaries, chunked request limits, and pagination validation. All 16 tests passed in three consecutive cycles (48 test executions); Python compilation, JavaScript syntax, and diff checks also passed. The new validation loop emits a JSON report and is wired into CI. These results are local; the updated container and external execution harness require separate verification.
