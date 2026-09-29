#!/usr/bin/env bash
# Background continuation of the author-approved Phase 2 matrix.
set -euo pipefail
cd "$(dirname "$0")/.."
selection=revision/artifacts/phase2/selection.json
for attempt in $(seq 1 1080); do
    if [ -s "$selection" ]; then
        printf 'Validation selection ready at %s\n' "$(date --iso-8601=seconds)"
        revision/run_phase2_after_validation.sh
        printf 'Phase 2 scheduled stages exited at %s\n' "$(date --iso-8601=seconds)"
        exit 0
    fi
    sleep 20
done
printf 'No validation selection after six hours; inspect validation run logs.\n' >&2
exit 1
