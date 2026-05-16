# DK1 Lean Agent Memory Standard

**Owner:** DK1 Capital / DK1.AI
**Status:** Active (Phase 3 shipped 2026-05-16)
**Companion:** `graphify-adoption.md` (sibling in this directory)
**Source:** `~/Downloads/dk1_lean_agent_memory_graphify_handoff.md` (DK1-flavored adaptation)

---

## 1. Executive Decision

Three layers — no more:

```text
Obsidian (~/dk1-brain-vault/)
= Dan's human source-of-truth knowledge base

Repo-level agent memory (docs/agent-memory/ + AGENTS.md)
= durable project instructions, decisions, current state, handoff trail for agents

Graphify (graphify-out/)
= machine-readable project/code graph for active software repos
```

No separate Obsidian Mind vault. No vector DB. No new memory service. No auto-scraping of vault content into repos.

---

## 2. The 6-File Canon

Every active DK1 repo gets this package under `docs/agent-memory/`:

```text
docs/agent-memory/
├── PROJECT_STATE.md      # current snapshot, open work, risks
├── DECISIONS.md          # locked decisions agents must not reverse
├── RUNBOOK.md            # build / test / deploy / rollback / monitoring
├── HANDOFF_LOG.md        # durable trail of agent work, newest-first
├── GRAPHIFY_NOTES.md     # last graph run + key structural findings
└── SECURITY_NOTES.md     # agent-readable security summary
```

Plus a restructured `AGENTS.md` at the repo root that points agents at the canon.

---

## 3. Path Policy

**Honor existing locations.** New files land in `docs/agent-memory/`. Don't move files that already work.

| File | Where it goes |
|---|---|
| PROJECT_STATE.md | If existing at root → keep at root. If existing under `docs/` → keep there. Otherwise create new at `docs/agent-memory/PROJECT_STATE.md`. |
| SECURITY.md | If existing at root → stays canonical. Create thin `docs/agent-memory/SECURITY_NOTES.md` pointer. Otherwise create full `SECURITY_NOTES.md` template. |
| DECISIONS / RUNBOOK / HANDOFF_LOG / GRAPHIFY_NOTES | Always `docs/agent-memory/`. |

AGENTS.md's Mandatory Read Order is rendered per-repo to point at the **actual** PROJECT_STATE.md path that exists.

---

## 4. AGENTS.md Merge Order

AGENTS.md is the entrypoint. Sections in this order, top to bottom:

1. Project intro (one paragraph)
2. **Mandatory Read Order** (6 references, paths resolved per the path policy above)
3. **Change Rules**
4. **After Meaningful Work** (which files to update post-task)
5. **Handoff Output Standard**
6. Any pre-existing project-specific sections
7. **## graphify** (the Graphify orientation rule from Phase 1+2 — preserved at bottom)

The bootstrap script `~/bin/dk1-agent-memory-bootstrap.sh` prepends sections 1–5 above any existing content; never deletes the `## graphify` section.

---

## 5. Core Operating Rule

```text
Before MEANINGFUL work (architecture, schemas, auth, routes, workflows):
  1. Read PROJECT_STATE.md
  2. Read DECISIONS.md
  3. Read RUNBOOK.md
  4. Scan latest HANDOFF_LOG.md entries
  5. Read SECURITY_NOTES.md
  6. Review GRAPHIFY_NOTES.md if Graphify has been run

For TRIVIAL work (typo, single-line fix): read order is advisory.

After meaningful work:
  1. ALWAYS update HANDOFF_LOG.md (new dated entry)
  2. Update PROJECT_STATE.md if open work changed
  3. Update DECISIONS.md if a decision was made/reversed
  4. Update RUNBOOK.md if commands/tests/deploys/monitoring/rollback changed
  5. Update SECURITY_NOTES.md if auth/permissions/secrets/data exposure changed
  6. Update GRAPHIFY_NOTES.md after rerunning Graphify
```

This rule is **documented, not enforced via hook** (Phase 3 choice). If agents ignore it, escalate to a PreToolUse / Stop hook in Phase 4.

---

## 6. Bootstrap Helper

`~/bin/dk1-agent-memory-bootstrap.sh <repo_path> [project_display_name]`

Single global helper (DK1 convention: helpers live in `~/bin/`). Idempotent. Does:

1. `mkdir -p <repo>/docs/agent-memory`
2. Detects existing PROJECT_STATE.md location → AGENTS.md read order points there; only creates new one in `docs/agent-memory/` if none exists
3. Detects existing root `SECURITY.md` → creates thin `SECURITY_NOTES.md` pointer; otherwise full template
4. Detects existing AGENTS.md state (absent / 11-line graphify stub / substantive) → prepends Mandatory Read Order block accordingly; never clobbers
5. Detects `Makefile` → enumerates targets in RUNBOOK.md
6. Detects `graphify-out/GRAPH_REPORT.md` → auto-populates GRAPHIFY_NOTES.md Last Run section with mtime + node/edge/community counts
7. Creates or appends `agent_memory:` block to `dk1_agent.yaml`
8. Seeds DECISIONS.md with locked cross-portfolio decisions (Obsidian canonical, Graphify orientation, no Mind vault, CLAUDE.md gitignored)
9. Seeds HANDOFF_LOG.md with an initial bootstrap entry

Running twice is a no-op.

---

## 7. Scope (Phase 3 ship — 2026-05-16)

**In scope (8 repos):**

Priority tier:
1. `dk1-ghtransna-orders` (Manifest in handoff lingo)
2. `dk1-skills/_internal/dk1-core-sales-six` (Sales Team Six)
3. `dk1-control-tower` (Control Room)
4. `dk1-command-center`

Secondary tier:
5. `dk1-jarvis`
6. `dk1-backbone`
7. `dk1-ai`
8. `first-leads-inbox`

**Explicitly out of scope (Phase 4+):**
- `houses-of-finance` — client-sensitive
- `md-juvenile-case-law` — client-sensitive
- `6cubed` — not yet active
- `dk1-policy` — governance source; meta-circular
- Anything else without an existing `.graphifyignore` from Phase 1+2

---

## 8. Weekly Review Checklist (operator)

For each active project, once per week:

- Does PROJECT_STATE.md still reflect reality?
- Did anyone reverse a decision in DECISIONS.md without documenting it?
- Are there HANDOFF_LOG.md entries that introduced new architecture without a corresponding DECISIONS.md entry?
- Are RUNBOOK.md commands still correct?
- Did any auth/permission/data change land without SECURITY_NOTES.md update?
- Does Graphify need a rerun? (Check `graphify-staleness-check.sh` log.)
- Are open issues stalled?

8 repos × 7 files × weekly review = a known time tax. If it exceeds 30 minutes total, consolidate or automate.

---

## 9. Things This Standard Does Not Do

- Does not stand up a separate Obsidian Mind vault
- Does not stand up a vector DB or memory service
- Does not auto-sync vault content into repos
- Does not enforce read-6-files via a blocking PreToolUse hook (advisory only)
- Does not enforce HANDOFF_LOG.md updates via a Stop hook (advisory only)
- Does not export agent-memory content to model providers automatically

If any of these become necessary, they go in Phase 4.

---

## 10. Phase 3 ship summary (2026-05-16)

- Bootstrap helper: `~/bin/dk1-agent-memory-bootstrap.sh`
- Policy doc: this file
- 8 repos bootstrapped: ghtransna, sales-six, control-tower, command-center, jarvis, backbone, dk1-ai, first-leads-inbox
- 0 existing files clobbered (per inventory: 6 SECURITY.md, 3 PROJECT_STATE.md, 2 substantive AGENTS.md, 5 CHANGELOG.md all preserved)
- All locked decisions seeded into every DECISIONS.md

---

## 11. Phase 4 backlog

- PreToolUse hook enforcing read order on architectural tools (Edit/Write/MultiEdit, but not Read/Grep)
- Stop hook reminding agent to update HANDOFF_LOG.md before ending a session
- Backbone API surfacing `agent_memory.enabled` + last HANDOFF_LOG.md mtime per repo
- Control-tower dashboard tile for memory freshness across the fleet
- Curated-input mode adaptation for hof / juvenile (curated agent-memory package, not committed in client repo)
- Cross-portfolio decisions registry — auto-sync the "Locked" entries from every repo's DECISIONS.md to a central index
- Weekly review automation — generate a summary of all 8 repos' state into a single rollup
