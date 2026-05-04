#!/usr/bin/env python3
"""Minimal policy validation for required keys and check names."""

from __future__ import annotations

from pathlib import Path
import sys

REQUIRED_TOP_LEVEL = [
    "policy_version:",
    "compliance:",
    "families:",
    "required_checks:",
    "security_baseline:",
    "required_log_fields:",
    "feature_flag_required_fields:",
]

REQUIRED_CHECKS = {
    "policy-sync",
    "contracts-sync",
    "semver-governance",
    "family-platform-parity",
    "feature-flag-governance",
    "project-lifecycle-governance",
    "security-baseline",
    "telemetry-compliance",
    "build-reproducibility",
    "release-readiness",
}

REQUIRED_SECURITY_BASELINE_TOKENS = [
    "existing_repo_grace_ends_at: \"2026-05-18\"",
    "new_repos_require_from_day_one: true",
    "exemption_file: security/baseline-exemption.json",
    "rollout_owner: dev-force-lead",
    "rollout_requires_legacy_exception_order: true",
]


def main() -> int:
    path = Path("policy/policy.yaml")
    if not path.exists():
        print("Missing policy/policy.yaml", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    for token in REQUIRED_TOP_LEVEL:
        if token not in text:
            print(f"Missing required policy section: {token}", file=sys.stderr)
            return 1

    for check in REQUIRED_CHECKS:
        if check not in text:
            print(f"Missing required check: {check}", file=sys.stderr)
            return 1

    for token in REQUIRED_SECURITY_BASELINE_TOKENS:
        if token not in text:
            print(f"Missing security baseline policy token: {token}", file=sys.stderr)
            return 1

    print("Policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
