#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
output_dir=$(mktemp -d)
trap 'rm -rf "$output_dir"' EXIT
c++ -std=c++20 -Wall -Wextra -Werror -O2 test.cpp -o "$output_dir/test"
"$output_dir/test"
c++ -std=c++20 -Wall -Wextra -Werror -fsanitize=address,undefined -g test.cpp -o "$output_dir/sanitized"
"$output_dir/sanitized"
c++ -std=c++20 -Wall -Wextra -Werror -O2 main.cpp -o "$output_dir/planner"
"$output_dir/planner" --benchmark
