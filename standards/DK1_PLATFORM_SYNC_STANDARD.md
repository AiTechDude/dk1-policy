# DK1 Platform Synchronization Standard v1.0

Owner: Dan Kim
Applies To: All DK1 Web, macOS, iOS, and Backend Systems
Status: Enforced Platform Policy

This repository operationalizes this standard as policy-as-code.

## Canonical Requirements
- Backend/API contracts are canonical and version-governed.
- Clients must consume generated contract clients/models.
- Feature flags must include compatibility metadata.
- Cross-platform release is coordinated and approval-gated.
- Observability fields are required for all production logs.
- Nightly guardian checks detect synchronization drift.
- Operator-facing remediation prompts must be validated against canonical state before display and stored with version history when their validated content changes.
- Project deprecations must publish archived lifecycle metadata in `PROJECT_STATE.md` and changelog entries in affected repos before removal from active portfolios.
- Active portfolio and managed-agent repos must publish explicit lifecycle metadata in `PROJECT_STATE.md`, and active control plans must remain synchronized to that repo-level lifecycle state.
