#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required" >&2
  exit 1
fi

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <repo> [branch]" >&2
  echo "Example: $0 AiTechDude/dk1-jarvis main" >&2
  exit 1
fi

REPO="$1"
BRANCH="${2:-main}"

# Branch protection baseline

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input "$(dirname "$0")/../github/branch-protection.baseline.json"

# Required production environment with reviewer gate
# NOTE: adjust reviewer ID to the owner account ID in your org before production use.

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/environments/production" \
  -f wait_timer=0 \
  -f prevent_self_review=true

echo "Applied baseline controls to ${REPO}:${BRANCH}"
