#!/usr/bin/env bash
# Deploy the arena to the private HF Space. Bundles the config, prompts and the current run's responses.
# The Space needs an HF_TOKEN secret with write access to $RATINGS_REPO (set once, see docs/method.md).
set -euo pipefail
SPACE=danielrosehill/Dan-Eval-Arena
cd "$(dirname "$0")/.."
RUN_ID=$(python3 -c "import json; print(json.load(open('config.json'))['run_id'])")
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/daneval" "$STAGE/data" "$STAGE/runs/$RUN_ID"
cp space/Dockerfile space/README.md config.json "$STAGE/"
cp daneval/common.py daneval/arena.py daneval/arena.html "$STAGE/daneval/"
cp data/*.json data/*.jsonl "$STAGE/data/"
cp "runs/$RUN_ID/responses.jsonl" "$STAGE/runs/$RUN_ID/"
hf upload "$SPACE" "$STAGE" . --repo-type space --commit-message "Deploy run $RUN_ID"
