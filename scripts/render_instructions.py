#!/usr/bin/env python3
"""Render AGENTS.md and CLAUDE.md from canonical templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def render(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy-repo", required=True)
    parser.add_argument("--policy-sha", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--policy-lock", required=True)
    parser.add_argument("--contracts-lock", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    policy_repo = Path(args.policy_repo)
    out_dir = Path(args.out_dir)

    manifest = parse_simple_yaml(Path(args.manifest))
    policy_lock = json.loads(Path(args.policy_lock).read_text(encoding="utf-8"))
    contracts_lock = json.loads(Path(args.contracts_lock).read_text(encoding="utf-8"))

    values = {
        "policy_sha": args.policy_sha,
        "family": manifest.get("family", "unknown"),
        "platform": manifest.get("platform", "unknown"),
        "app_id": manifest.get("app_id", "unknown"),
        "policy_version": policy_lock.get("policy_version", "unknown"),
        "contracts_version": contracts_lock.get("contracts_version", "unknown"),
    }

    agents_tmpl = (policy_repo / "templates" / "AGENTS.md.tmpl").read_text(encoding="utf-8")
    claude_tmpl = (policy_repo / "templates" / "CLAUDE.md.tmpl").read_text(encoding="utf-8")

    (out_dir / "AGENTS.md").write_text(render(agents_tmpl, values), encoding="utf-8")
    (out_dir / "CLAUDE.md").write_text(render(claude_tmpl, values), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
