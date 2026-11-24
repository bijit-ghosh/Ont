# Ont enterprise stack evaluations

A reproducible evaluation catalog mapped to all seven Ont architecture layers. It runs existing behavior checks as named acceptance scenarios, preserves per-scenario evidence, and reports enterprise integration gaps separately.

## Run

Install the runtime lock, Node.js 24, Git and a Rust toolchain with rustfmt/Clippy, then run from the source checkout:

```bash
python -m evals.run --out evals/reports/core-001
```

For the complete local deployment profile, build the image first:

```bash
docker build -t ont-control-plane:validated .
python -m evals.run --profile deployment --out evals/reports/deployment-001
```

Reports are written to a **new** output directory; previous evidence is preserved. Docker uses the local managed Unix socket. The container scenario creates and removes disposable resources and makes no external service calls. This suite runs from the repository/source distribution; the runtime wheel deliberately excludes developer test infrastructure.

## Results and gates

Each case is `passed`, `failed`, or `blocked`. The catalog labels tests as local, mocked contract, local Git with mocked verifier, frontend, Rust, container, or enterprise gate. A mock is never reported as a real provider test.

- `automated_gate` covers executable scenarios required by the selected profile.
- `enterprise_gate` includes all enterprise acceptance gates. It remains blocked until the listed services, implementations and datasets are qualified.
- Exit **0**: required automated scenarios pass. This does not mean enterprise qualification passed.
- Exit **1**: an executed automated scenario failed.
- Exit **2**: a required scenario is blocked, or `--require-enterprise` was requested and enterprise qualification is incomplete.

Use `--require-enterprise` when a deployment policy requires complete enterprise evidence. The current suite intentionally cannot claim full qualification: seven gates identify external environment, dataset or implementation work. Those gates are specifications, not fake executable checks. No option accepts manually entered pass flags for them.

A missing tool, missing container image or unselected deployment scenario is blocked. A timeout, failed command, missing test selector, zero discovered tests or skipped tests cannot produce a pass.

## Evidence

`report.json` includes the catalog hash, relevant source-file fingerprint, Git revision, working-tree state, UTC execution timestamps, scenario status, commands, durations, test counts and log hashes. `scorecard.md` presents the layer summary and required actions. Per-case logs contain the actual test output. Archive the complete directory, not only the scorecard.

The source hash covers implementation, test and evaluation inputs while excluding databases, dependencies, build products and report outputs. It does not sign provenance or establish producer identity. Use trusted CI artifacts and your enterprise's attestation process when consuming results as release evidence.

## Catalog and coverage

`catalog.json` contains **28 scenarios**: 21 executable acceptance scenarios and seven enterprise gates. The core profile executes 20 scenarios and leaves the container scenario blocked; the deployment profile includes the container check. The suite includes negative tests, concurrency and recovery fixtures, exact-commit delivery guards, tenant denial, and evaluation-regression checks.

[Layer matrix and adoption guide](../docs/ENTERPRISE_EVALUATION.md) defines enterprise ownership, required artifacts and rollout phases. [Product readiness](../docs/READINESS.md) identifies implementation boundaries.

## Recorded deployment-profile result

[Enterprise results](../docs/ENTERPRISE_RESULTS.md) records the validated source and layer totals. Raw logs and report JSON are available in CI artifacts or a local report directory.
