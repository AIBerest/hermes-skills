#!/usr/bin/env bash
# validate-loop-design.sh — compatibility wrapper around sgctl semantic loop validation.
set -euo pipefail
mode=()
if [[ "${1:-}" == "--instantiated" ]]; then
  mode=("--instantiated")
  shift
fi
if [[ $# -lt 1 ]]; then
  echo "usage: validate-loop-design.sh [--instantiated] <path-to-LOOP_DESIGN.md>" >&2
  exit 2
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
args=()
if [[ ${#mode[@]} -gt 0 ]]; then
  args+=("${mode[@]}")
fi
args+=("$1")
if python3 "$ROOT/scripts/sgctl.py" validate-loop-design "${args[@]}" >/tmp/sg-validate-loop.$$ 2>/tmp/sg-validate-loop-err.$$; then
  lines=$(wc -l < "$1" | tr -d ' ')
  echo "✓ $1: loop design semantic ok ($lines lines)"
  rm -f /tmp/sg-validate-loop.$$ /tmp/sg-validate-loop-err.$$
  exit 0
fi
cat /tmp/sg-validate-loop-err.$$ >&2 || true
rm -f /tmp/sg-validate-loop.$$ /tmp/sg-validate-loop-err.$$
exit 1
