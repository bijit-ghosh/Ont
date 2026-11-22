# Contributing to Ont

Start with an issue that names the user problem, affected component, expected behavior, and a reproducible check. Keep fixes small enough to review. Treat prompts, repository files and retrieved content as untrusted data; authorization belongs in trusted code.

Create a virtual environment, install `requirements.lock.txt`, then install the project with `python -m pip install --no-deps .`. For the full gate, install Node.js 24 and a C++20 compiler with sanitizer support, then run `python scripts/validate.py --cycles 3`. Docker changes require a rebuilt image and `python scripts/container_smoke.py` against it.

Add targeted regression coverage for behavior and failure recovery. Document whether provider results are mocked, synthetic, or live. Never commit secrets, customer data, local databases, generated credentials, or unreviewed external output. Update relevant setup and architecture guides when contracts change.

Integration changes must preserve tenant boundaries, exact-commit evidence, least-privilege credentials, cancellation, usage accounting, and idempotency/reconciliation. Changes to policy, authentication, verifier checks, or release behavior deserve focused review.

Source is MIT-licensed. Preserve notices and verify the licenses of new dependencies. Contributions should be original or include appropriate provenance and licensing.
