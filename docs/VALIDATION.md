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
- Full video access was throttled. Research is limited to the supplied slide and linked official documentation.
- Real agent execution, model billing, PR delivery, and production deployment remain unverified and need external integrations.
