# DK1 Graphify Adoption Standard

**Owner:** DK1 Capital / DK1.AI
**Status:** Active (Phase 1 shipped 2026-05-15)
**Supersedes:** `~/Downloads/dk1_graphify_install_usage_handoff.md` (2026-05-15 draft)
**Scope:** how Graphify is installed, what gets graphed, how graphs stay fresh, and how Claude Code + Codex must consult graphs before broad search.

---

## 1. Executive Decision

Use **Obsidian** (`~/dk1-brain-vault/`) as the DK1 human knowledge system.
Use **Graphify** only as an agent-facing project graph for active software, workflow, and product folders.

Do **not** run Graphify across the entire DK1 portfolio. Run it per project repo or per curated input folder.

Priority repos (Phase 1, shipped 2026-05-15):

1. `~/Projects/dk1-ghtransna-orders` — operational freight workflow (the "manifest" analogue)
2. `~/Projects/dk1-skills/_internal/dk1-core-sales-six` — Sales Team 6 agents/skills/guardrails (nested in `dk1-skills`)
3. `~/Projects/dk1-control-tower` — local operator surface (`localhost:8500`)
4. `~/Projects/dk1-command-center` — operator API + rollups on dk1-core

Secondary tier (Phase 2 — backfill when needed):

- `dk1-jarvis`, `dk1-backbone`, `dk1-ai`
- `first-leads-inbox`
- `houses-of-finance` (client-sensitive — curated-input mode only)
- `md-juvenile-case-law` (client-sensitive — curated-input mode only)
- `6cubed`

**Never graph:**
- `~/dk1-brain-vault/` itself
- `~/Projects/dk1-policy/` (governance source of truth)
- `~/Projects/dk1-ai/_archive/`
- Any MinIO mount or `~/Projects/*/data/`

---

## 2. What Graphify Is For

Graphify is **not** another Obsidian. For DK1, treat it as an **agent context compiler** per repo.

It builds a graph from code (Tree-sitter), docs, SQL, diagrams, and PDFs. Outputs:

```text
graphify-out/
├── GRAPH_REPORT.md     # the file agents read first
├── graph.json          # queryable machine graph
├── graph.html          # optional visual browser
└── cache/              # incremental cache (excluded from rebuilds)
```

The highest-value use case is **agent orientation** — making Claude Code, Codex, or another coding agent read the graph before grepping random files, cutting token burn and improving first-pass accuracy.

The visual graph (`graph.html`) is secondary; the `--no-viz` flag is used in CI and most automated rebuilds.

---

## 3. DK1 Usage Rules

### Rule 1 — Obsidian remains canonical
The vault at `~/dk1-brain-vault/` is the human-readable system of record:
- Strategy notes, client notes, product decisions
- Meeting notes, maps of content, operating principles
- DK1 Council notes, decision history

Graphify only holds: code relationships, workflow relationships, schema/document relationships, agent-readable structure, generated graph summaries.

### Rule 2 — Per-project, not global
Graphify runs at the **repo** level (or a curated sub-folder), never against `~/Projects/` or `~/dk1-brain-vault/`.

### Rule 3 — Client-sensitive files are excluded by default
Every Graphified repo carries a `.graphifyignore` excluding (at minimum):

- `.env`, `.env.*`, `secrets/`, `credentials/`, `private/`, `*.pem`, `*.key`
- `data/`, `*.db`, `*.sqlite`, `*.sqlite3`, `logs/`
- `from client/`, `clients/*/private/`, `customer-data/`, `raw-emails/`, `email-attachments/`, `invoices/`, `pii/`
- `node_modules/`, `.venv/`, `dist/`, `build/`, `.next/`, `coverage/`, `__pycache__/`, `*.pyc`, `*.log`
- `_inbox-from-downloads/` (operator review queues)
- `minio/`, `object-storage/`, `objects/`

Client-sensitive repos (`houses-of-finance`, `md-juvenile-case-law`, any future regulated client) MUST use curated-input mode (§9.2 below), not direct graphing.

### Rule 4 — Graphs are never committed
`graphify-out/` is in `.gitignore` for every DK1 repo. Always. Rebuild locally.

The vault rsync destination `docs/handoffs/vault-context/` is also in `.gitignore` until the operator explicitly approves a snapshot for sharing.

### Rule 5 — Semantic extraction uses Anthropic
Default backend is `--backend claude` (uses `ANTHROPIC_API_KEY` from each repo's `.env` or the canonical key sourced from `~/Projects/dk1-ghtransna-orders/.env`).

Strict-local fallback for client-sensitive repos: `--backend ollama` via `dk1-local-llm-stack`. Lower extraction quality, acceptable for sensitive data.

Never use Gemini, OpenAI, or Bedrock backends without explicit approval.

---

## 4. Install on macOS (MacBook)

```bash
brew install python@3.12 uv          # if not already installed
uv tool install graphifyy            # note the double 'y'
uv tool install graphifyy --with anthropic --force  # required for --backend claude
graphify --version                   # verify
graphify install                     # registers the skill with local AI assistants
```

The `anthropic` package must be injected into Graphify's uv tool environment — without it, the `claude` backend errors with "Claude direct extraction requires the anthropic package".

---

## 5. Install on dk1-core (Ubuntu)

Phase 2. Same recipe, with SSH via Tailscale (`ssh dk1-core`, not LAN IP). Services live at `/home/dan/dk1/services/` per the dk1-core layout standard.

---

## 6. Install on GitHub Actions CI runner

Phase 2. Per-repo workflow `.github/workflows/graphify-check.yml`:

- Runs on PRs touching code paths (advisory, never fails the build).
- Posts diff of `GRAPH_REPORT.md` as a PR comment.
- Weekly Monday 6 AM ET rebuild against `main` to catch drift between local hydration and CI.

---

## 7. Folder Layout

```text
~/Projects/
├── dk1-ghtransna-orders/            # priority 1
├── dk1-skills/
│   └── _internal/
│       └── dk1-core-sales-six/      # priority 2 (NESTED — not a top-level repo)
├── dk1-control-tower/               # priority 3
├── dk1-command-center/              # priority 4
├── dk1-policy/                      # NEVER graph
├── dk1-ai/
│   └── _archive/                    # NEVER graph
└── ...

~/dk1-brain-vault/                   # NEVER graph the vault itself
└── sources/git/<repo-slug>/         # source of curated vault-context rsync
```

---

## 8. Graph-First Orientation Mode (the DK1 default)

This is the policy-shaped piece: **CC and Codex consult the graph before broad search**. Three enforcement layers.

### Layer 1 — Global Claude Code hook
`~/.claude/hooks/graphify-orientation.py` fires on `Grep|Glob` tool calls. If the project has `graphify-out/GRAPH_REPORT.md`, it emits a one-shot per-session nudge asking the agent to read the report first. Advisory only, never blocks. Wired in `~/.claude/settings.json` under `hooks.PreToolUse`.

### Layer 2 — Graphify's per-repo Bash hook
`graphify claude install` writes a per-repo `.claude/settings.json` PreToolUse hook on `Bash` that catches `grep`/`rg`/`find`/`fd`/`ack`/`ag` shell calls and nudges to read `GRAPH_REPORT.md`. Complements Layer 1.

`graphify codex install` writes the equivalent to `.codex/hooks.json` and an AGENTS.md section.

### Layer 3 — CLAUDE.md / AGENTS.md sections
`graphify claude/codex install` appends a `## graphify` section to both files saying:

> ALWAYS read `graphify-out/GRAPH_REPORT.md` before reading any source files, running grep/glob searches, or answering codebase questions. For cross-module "how does X relate to Y" questions, prefer `graphify query`, `graphify path`, or `graphify explain` over grep. After modifying code, run `graphify update .`.

### Layer 4 (Phase 2, deferred)
Add `graphify: true` flag to `dk1_agent.yaml` so `dk1-backbone` surfaces graph availability in the agent registry. Stale graphs (>14d) appear as warnings in `dk1-control-tower`.

---

## 9. Backfill (one-time comprehensive ingest)

### 9.1 Standard repos (priority tier)

For each priority repo:

1. **`.graphifyignore`** — create per Rule 3 above
2. **`.gitignore`** — ensure `graphify-out/` and `docs/handoffs/vault-context/` are listed
3. **Vault rsync** — pull `.md` files (one-way) from `~/dk1-brain-vault/sources/git/<repo-slug>/` into `docs/handoffs/vault-context/` (manual review before each rsync)
4. **First build:** `graphify extract . --backend claude --max-concurrency 2`
5. **Re-cluster:** `graphify cluster-only .` (labels communities)
6. **Read:** `cat graphify-out/GRAPH_REPORT.md`
7. **Sanity check:** `graphify query "what are the major modules?"`
8. **Install integrations:** `graphify claude install && graphify codex install`

### 9.2 Curated-input mode (client-sensitive repos)

For `houses-of-finance`, `md-juvenile-case-law`, or any regulated client:

```bash
mkdir -p ../graphify-input/<repo>
rsync -av \
  --exclude='.git' --exclude='node_modules' --exclude='.venv' \
  --exclude='.env*' --exclude='secrets' --exclude='credentials' \
  --exclude='customer-data' --exclude='raw-emails' --exclude='invoices' \
  --exclude='pii' \
  ./<repo>/ ../graphify-input/<repo>/

cd ../graphify-input/<repo>
graphify extract . --backend ollama   # local-only LLM for sensitive data
```

Never run `graphify extract` directly against a client repo. The rsync IS the security boundary.

### 9.3 What backfill pulls in

| Source | How |
|---|---|
| Live code (`src/`, `app/`, `lib/`) | `graphify extract` — Tree-sitter (deterministic, local) |
| Repo docs (`docs/`, `README.md`, `CLAUDE.md`, `ARCHITECTURE.md`, ADRs) | Auto via `--backend claude` semantic extraction |
| Schema/migrations (`alembic/`, `*.sql`, `prisma/schema.prisma`) | Tree-sitter parses SQL |
| API contracts (`*.yaml`, `*.json`, `dk1_agent.yaml`, `family.manifest.yaml`) | YAML/JSON parsers |
| PRDs / handoff docs | Copy to `<repo>/docs/handoffs/` first, then graph |
| Obsidian notes referencing the repo | Curated rsync into `docs/handoffs/vault-context/` |
| Archived code (`_archive/`, `legacy/`) | **Excluded by default** |
| Git history | **Excluded** — Graphify doesn't model time; use `git log` |

---

## 10. Hydration (keep graphs fresh)

### Mechanism 1 — launchd daily refresh (macOS)

`com.dk1.graphify-hydrate` runs daily at 4:00 AM ET, executing `~/bin/graphify-hydrate.sh`:

- Iterates all priority repos.
- Calls `graphify update .` (AST-only, no LLM cost).
- If AST graph changed (mtime delta), runs `graphify cluster-only . --no-viz` to refresh communities and report.
- Logs to `~/Library/Logs/graphify-hydrate.log`.

Cadence aligns with `dk1-knowledge-graph` (4:30 AM) and `dk1-infrawatch` scorecards (Monday 6 AM).

### Mechanism 2 — per-repo `post-commit` git hook

Each priority repo has `.git/hooks/post-commit` that:

- Inspects `git diff-tree --no-commit-id --name-only -r HEAD`.
- If any file matches `*.py|*.ts|*.tsx|*.js|*.jsx|*.sql|*.md|*.yaml|*.yml|*.toml|*.swift|*.go|*.rs|*.java|*.rb|*.sh`, kicks off `graphify update .` in **background** (never blocks the commit).
- Logs to the same hydrate log.

For `dk1-skills` (which contains multiple sub-projects including `_internal/dk1-core-sales-six`), the hook is path-aware — only rebuilds graphs whose sub-tree was touched.

These hooks are local-only (not committed). `graphify hook install` (the built-in command) is **not used** — its full-rebuild + branch-switch triggers are too aggressive.

### Mechanism 3 — CI freshness check (Phase 2)
See §6.

### Mechanism 4 — Backbone freshness monitoring (Phase 2)
See §8 Layer 4.

### Stale-graph triage

The orientation hook (Layer 1) reads `GRAPH_REPORT.md` mtime. If >14 days, the nudge includes a "graph last refreshed N days ago" warning. Graphs >30 days stale are not auto-rebuilt — operator must approve, because curated docs may have drifted.

---

## 11. Phase 1 ship summary (2026-05-15)

- Graphify 0.8.1 installed via `uv tool install graphifyy` + `--with anthropic`
- Orientation hook live at `~/.claude/hooks/graphify-orientation.py`, wired into `~/.claude/settings.json`
- 4 priority repos backfilled, total Anthropic cost ~$4.50:
  - `dk1-ghtransna-orders`: 3490 nodes / 7610 edges / 185 communities ($0.39)
  - `dk1-core-sales-six`: 546 nodes / 1185 edges / 18 communities ($2.12)
  - `dk1-control-tower`: 1690 nodes / 2835 edges / 96 communities ($0.54)
  - `dk1-command-center`: 3696 nodes / 7465 edges / 212 communities ($1.45)
- Hydration: `~/bin/graphify-hydrate.sh` + `com.dk1.graphify-hydrate` LaunchAgent scheduled daily 4:00 AM ET
- Post-commit hooks installed in all 4 priority repo `.git/hooks/` (and `dk1-skills` parent repo with path filter for sales-six)
- `graphify claude install` and `graphify codex install` ran in each priority repo

---

## 12. Phase 2 ship summary (2026-05-15)

**Graphify on MacBook upgraded to 0.8.4. Six new repos graphed. CI, dk1-core install, curated-input mode, dk1_agent.yaml flag, weekly staleness alert all live.**

### Secondary tier backfills (Phase 2 additions, ~$8.50 Anthropic)

| Repo | Nodes | Edges | Communities | Cost |
|---|---|---|---|---|
| dk1-jarvis | 3947 | 8292 | 320 | $1.17 |
| dk1-backbone | 2417 | 4784 | 165 | $0.19 |
| dk1-ai (Next.js) | 3658 | 7972 | 193 | $6.90 |
| first-leads-inbox | 662 | 1039 | 30 | $0.29 |

After daily hydration AST refresh, dk1-ai grew to 11685 nodes / 19176 edges / 876 communities (cache warmed; viz disabled per >5K node limit). first-leads-inbox grew to 1030 nodes.

### Curated-input mode (client-sensitive)

Wrote `~/bin/graphify-curate.sh` and used it to graph:

| Repo | Curated source | Nodes | Edges | Communities | Cost |
|---|---|---|---|---|---|
| houses-of-finance | `~/Projects/graphify-input/houses-of-finance/` | 1793 | 3395 | 174 | $1.66 |
| md-juvenile-case-law | `~/Projects/graphify-input/md-juvenile-case-law/` | 1443 | 2566 | 131 | $0.85 |

Each gets a `GRAPHIFY.md` pointer file in its original repo so agents know where the curated graph lives and that **direct extract against the original repo is forbidden** (would send case PDFs / mobile screenshots / customer data to Anthropic).

### CI workflow

Reusable template at `~/Projects/dk1-policy/standards/graphify-check.yml.template`. Deployed to all 6 non-nested Graphified repos at `.github/workflows/graphify-check.yml`:
- dk1-ghtransna-orders, dk1-control-tower, dk1-command-center, dk1-jarvis, dk1-backbone, dk1-ai, first-leads-inbox

Behavior: runs on PRs touching code/docs, builds graph in CI, posts `GRAPH_REPORT.md` diff as PR comment, uploads `graphify-out/` as workflow artifact. Advisory — never fails the build. Requires repo secret `ANTHROPIC_API_KEY`.

### dk1-core (Ubuntu) install

SSH'd via Tailscale (`ssh dan@dk1-core`):
- Installed `uv 0.11.14` via curl installer
- Installed `graphify 0.8.4` + `anthropic` SDK via `uv tool install`
- Persisted `$HOME/.local/bin` on PATH in `~/.bashrc` for cron/launchctl compatibility
- No repos graphed on dk1-core itself (canonical graphs live on MacBook); install is for future remote rebuilds and CI parity

### Backbone integration

`graphify` metadata block appended to existing `dk1_agent.yaml` in:
- dk1-ghtransna-orders, dk1-core-sales-six, dk1-command-center, dk1-jarvis

Block:
```yaml
graphify:
  enabled: true
  graph_path: graphify-out/GRAPH_REPORT.md
  freshness_sla_days: 7
```

`dk1-control-tower`, `dk1-backbone`, `dk1-ai`, `first-leads-inbox` don't have `dk1_agent.yaml` files; they're tracked via the staleness checker directly.

### Weekly ntfy staleness alert

`~/bin/graphify-staleness-check.sh` runs Monday 7:00 AM ET via `com.dk1.graphify-staleness` LaunchAgent. Walks all 10 Graphified locations, compares `GRAPH_REPORT.md` mtime against per-repo `freshness_sla_days` (default 7), and POSTs a summary to `dk1-alerts-graphify` ntfy topic **only if** something is stale. Current dry run: 10 fresh, 0 stale, 0 missing — silent (correct).

### Hydration script expanded

`~/bin/graphify-hydrate.sh` `REPOS=()` array now covers all 8 standard-mode repos. Curated-input repos (hof, juvenile) are NOT in the hydrate loop — they need `graphify-curate.sh` first to refresh the rsync source before `graphify update`, so they're refreshed manually.

---

## 13. Phase 3 backlog

- `graphify-curate.sh` integration into a weekly launchd job for hof + juvenile (refresh rsync + update + cluster)
- dk1-backbone API endpoint surfacing `graphify.enabled` + last-build mtime from each registered agent
- dk1-control-tower dashboard tile for graph freshness across the fleet
- Cross-repo `global-graph.json` merge (Graphify supports `graphify global add`) for portfolio-level queries
- `6cubed` and any new venture repos when active
- Replace per-repo Anthropic spend with a single `--backend ollama` route for sensitive curated inputs once `dk1-local-llm-stack` quality is validated

---

## 13. Operator quickstart

When adding Graphify to a new DK1 repo:

```bash
# 1. cd to repo
cd ~/Projects/<repo>

# 2. Create .graphifyignore (copy from a priority repo as template)
cp ~/Projects/dk1-ghtransna-orders/.graphifyignore .

# 3. Add to .gitignore
grep -qE "^graphify-out/" .gitignore || echo "graphify-out/" >> .gitignore
grep -qE "^docs/handoffs/vault-context/" .gitignore || echo "docs/handoffs/vault-context/" >> .gitignore

# 4. (Optional) Vault rsync if ~/dk1-brain-vault/sources/git/<repo>/ exists
mkdir -p docs/handoffs/vault-context
rsync -av --include='*/' --include='*.md' --exclude='*' \
  ~/dk1-brain-vault/sources/git/<repo>/ ./docs/handoffs/vault-context/

# 5. Source API key + build
source ~/Projects/dk1-ghtransna-orders/.env && export ANTHROPIC_API_KEY
graphify extract . --backend claude --max-concurrency 2
graphify cluster-only .

# 6. Install integrations
graphify claude install
graphify codex install

# 7. Add to hydration script (~/bin/graphify-hydrate.sh REPOS array)

# 8. Install post-commit hook (copy from a priority repo)
cp ~/Projects/dk1-ghtransna-orders/.git/hooks/post-commit .git/hooks/
chmod +x .git/hooks/post-commit
```

---

## 14. Pointers

- Plan file: `~/.claude/plans/users-dankim-downloads-dk1-graphify-ins-generic-unicorn.md`
- Graphify GitHub: https://github.com/safishamsi/graphify
- Graphify site: https://graphify.net/
- Hydrate log: `~/Library/Logs/graphify-hydrate.log`
- LaunchAgent: `~/Library/LaunchAgents/com.dk1.graphify-hydrate.plist`
- Settings hook entry: `~/.claude/settings.json` → `hooks.PreToolUse[matcher="Grep|Glob"]`
