# Dependency and tooling maintenance

## Updated baseline

The release resolves Python dependencies in a clean Python 3.12 virtual environment. The direct packages are FastAPI 0.165.0, Uvicorn 0.54.0, and HTTPX2 2.16.2. The first two were already current in the previous lock; their minimum versions now reflect the tested baseline. HTTPX2 replaces the deprecated HTTPX test-client transport. All transitive dependencies are pinned in `requirements.lock.txt`.

The frontend has no third-party runtime JavaScript dependencies. Node is used for syntax checks and development command convenience. CI uses Node 24 and Python 3.12; Python's minor version remains stable because changing runtime generations needs a separate compatibility matrix. The Docker image retains `python:3.12-slim` and installs the exact lockfile. Managed host/OS packages are outside the application's dependency scope.

GitHub Actions were checked against their published latest releases and updated to checkout 7.0.1, setup-python 7.1.0, setup-node 7.1.0, and upload-artifact 7.0.2. Release tags are version-pinned, not immutable SHA-pinned. Dependabot proposes weekly updates for pip, Docker, and workflow actions; repository settings determine whether those automated proposals can run. No automatic merge is configured.

## Update procedure

1. Create a fresh environment with `python -m venv .venv` and upgrade pip inside it.
2. Install `requirements.txt` using the configured trusted package index; retain TLS verification.
3. Resolve and inspect changes, then write `pip freeze` to `requirements.lock.txt`. Never generate the lock from a shared environment containing unrelated tools.
4. Run `python -m pip check` and `python scripts/validate.py --cycles 3` in the new environment.
5. Rebuild the container, validate its runtime, review advisories and licenses, then use the matching commit's CI results before release.

An outdated-package check is not a vulnerability audit. This release records compatibility evidence; no clean vulnerability-scan claim is made. Rebuild images for OS security fixes and use your deployment scanner for the actual built image.
