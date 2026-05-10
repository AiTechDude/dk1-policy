# Opening this repo as an Obsidian vault

This repo is Obsidian-openable. `.obsidian/` is gitignored (operator-local).

## Open

Obsidian → File → Open Vault → select `~/Projects/dk1-policy/`.

## What lives here

DK1 platform policy (v1.3.0) — security baseline, approval kinds, families/platforms, required checks, confidentiality classes. **Source-of-truth** for these.

## Frontmatter convention

Use the canonical template at [`~/Documents/dk1-vaults/_tools/frontmatter-template.md`](../../Documents/dk1-vaults/_tools/frontmatter-template.md). Files here are `source: code-backed` (runtime-enforced).

## Narrative operator memory

The "why" behind policy thresholds lives in `~/Documents/dk1-vaults/dk1-st6-master-vault/03-Approval-Patterns/`, not here. This repo is the **what**; the vault is the **why**.

## Verification

`cd ~/Documents/dk1-vaults && make verify-vaults` — checks that any vault references to this repo's files still resolve.
