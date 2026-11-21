# Ont continuous improvement

## Implemented loop

`python scripts/improve_loop.py /path/to/inbox /path/to/reports --baseline current --candidate proposed`

The process watches for JSON evaluation datasets, evaluates each content hash once, writes reports atomically, and responds to SIGTERM/SIGINT. `--once` processes one scan and exits, suitable for CI. The default scan interval is 60 seconds. This is a continuous evaluation loop over newly recorded evidence; it does not invent task outcomes, call models, change source code, or promote policies by itself.

Each dataset is a JSON array of records with `task`, `seed`, `split`, `policy`, `quality`, `cost`, `latency`, and `safe`. Quality must be in [0,1], safety a boolean, and cost/latency finite and nonnegative. Only `holdout` records enter promotion evaluation. Each task/seed requires both policy results; duplicates and unpaired data are rejected.

The evaluator computes quality minus bounded cost and latency penalties, compares paired results, aggregates repeated seeds per task, and calculates a deterministic one-sided 95% bootstrap lower bound across independent tasks. Eligibility requires at least 20 tasks, no candidate safety failure, no per-pair quality regression, and lower-bound reward improvement of at least 0.02. These defaults are a starting policy, not statistical proof of universal improvement. Bootstrap uncertainty depends on representative independent tasks; repeated tuning on one holdout invalidates the estimate.

Reports retain the dataset SHA-256 and always set `promoted=false`. A qualified candidate becomes a review proposal. No endpoint automatically changes the factory from evaluation output.

## Learning primitive

`ont.improvement.Bandit` implements UCB action selection with finite bounded rewards. It is a tabular reinforcement-learning primitive for choosing evaluated configurations. It is not neural model training, RLHF, or a persistent online production learner. The tests establish that selection favors the higher-reward arm in a controlled synthetic environment; they do not establish improvements on real software tasks.

## Recursive improvement contract

1. Record immutable task inputs, factory/model/harness versions, tool events, patches, receipts, and real billed usage.
2. Label success with acceptance tests and independent review; add delayed signals for reverts and incidents.
3. Diagnose failures and propose one versioned change: prompt, skill, routing rule, retrieval policy, or stage graph.
4. Train/select on training data. Freeze the candidate and evaluate on a fresh sealed holdout, with matched budgets and tools.
5. Generate a signed proposal linking dataset, baseline/candidate hashes, safety checks, uncertainty, and estimated blast radius.
6. Require operator approval; canary a small task cohort under a fixed spend ceiling.
7. Observe delayed outcomes. Roll back on policy violations, quality loss, or cost regressions.
8. Feed the new observations into the next generation. Keep the evaluator, reward specification, and promotion permissions outside candidate write access.

Actual candidate generation, persistent bandit state, signed datasets, online canaries, delayed rewards, rollback automation, and neural fine-tuning are future integrations. They require explicit data permissions, compute budgets, and independent validation. An improvement process must never train on secrets or treat self-reported success as a reward without verification.

## Recommended experiment controls

Use task-family stratification, independent task IDs, disjoint training/evaluation corpora, leakage checks, versioned reward definitions, minimum sample planning, maximum experiment counts, and a fresh confirmation set after selection. Report failures and total cost, including retries and rejected candidates. Maintain an immutable baseline so a bad reward or evaluator change cannot erase regression evidence.
