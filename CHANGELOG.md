# Changelog

## Unreleased

### Native runtime

- Replaced the native scheduler with Rust, preserving placement, forecasting, and bounded capacity planning.
- Added Cargo lockfile, formatting/lint gates, debug/release tests, CLI tests and an optimized benchmark.

### Project and distribution

- Reorganized the Ont overview, mission, quickstart, capability map, architecture links, and documentation index.
- Added installable Python wheel/source-distribution metadata and an `ont` CLI with `serve`, `demo`, and version commands.
- Bundled browser assets in the wheel and placed default runtime data under the working directory.
- Added isolated wheel-install smoke testing, documentation-link checks, build-tool pins and CI artifact packaging.
- Added configuration, packaging, readiness, roadmap, contribution and security guidance.

### Validated foundations

- Persistent work-order lifecycle, human gates, leases, cancellation, artifacts and configuration snapshots.
- Tenant-role gateway, optional model/delivery/verification/release/memory adapters and offline comparative evaluation.
- Native Rust placement/capacity planner with tests and Clippy checks.
- Demo fixture, frontend regression controls, Docker HTTP/restart checks, and automated CI.

Distribution packages are built from source. Deployment requirements are documented in the operations and integration guides.
