#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cargo fmt --all -- --check
cargo clippy --locked --offline --all-targets -- -D warnings
cargo test --locked --offline
cargo test --locked --offline --release
cargo run --locked --offline --release -- --benchmark
