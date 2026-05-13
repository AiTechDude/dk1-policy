# DK1 Auth Standard — retroactive rollout plan

References [`auth-workos.md`](./auth-workos.md). Owned by Dan Kim.
Reviewed quarterly. Last edit: 2026-05-12.

The Manifest cutover is the reference implementation; every other
service mirrors that pattern (sealed cookie, `(authed)` layout cookie
check, `/v1/auth/workos/{login,callback,logout}` endpoints).

| # | Service | Today | Effort | Target | Notes |
|---|---|---|---|---|---|
| 1 | **Manifest** (`dk1-ghtransna-orders`) | bcrypt + bearer | already in flight (ADR 0009) | 2026-05 | Reference implementation. Cutover sequencing in the ADR. |
| 2 | **DK1 Custom Build portal** (`dk1-ai`) | Cloudflare-Worker session token | M | 2026-Q3 | Public-internet, Cloudflare-fronted. Highest-priority retrofit after Manifest because of public exposure. |
| 3 | **Brand Presence** | none yet (planned) | S | first deploy | Wire WorkOS at first ship; never have a bcrypt path. |
| 4 | **Account Strategy Copilot** | bcrypt + session (FastAPI + React) | S | 2026-Q3 | Same shape as Manifest; cleanest copy/paste of the cutover. |
| 5 | **First Leads Inbox** | API-key only today, no human UI | XS | when human UI ships | Not customer-facing today; defer until an operator console is added. |
| 6 | **dk1-command-center** | `CC_API_KEY` only, no human UI | M | when operator UI promoted | Service-to-service `X-DK1-TOKEN` stays. WorkOS only when /chat or any operator console is exposed beyond local. |
| 7 | **dk1-jarvis** | `X-DK1-TOKEN` between services + Mac client | L | when web operator surface ships | Service tokens stay forever. Mac client uses Tailscale identity. WorkOS only on a future browser console. |
| 8 | **dk1-control-tower** | local-only, `127.0.0.1:8500` | XS | exempt | OS-user check sufficient. Declare `auth_status: exempt`. |
| 9 | **dk1-backbone** | `Authorization: Bearer <DK1_BACKBONE_TOKEN>` | M | when operator dashboard ships | Service-to-service stays. WorkOS only on the planned operator dashboard. |
| 10 | **dk1-infrawatch / dk1-toolwatch / dk1-sentinel-qc / dk1-doc-sentinel** | service tokens only | n/a | exempt | Pure machine APIs; declare `auth_status: exempt`. |
| 11 | **dk1-ai marketing site** (public) | none | n/a | exempt | Public marketing site; declare `auth_status: exempt`. |

## Rollout policy

- Each migration is a separate milestone scoped to one service. No
  cross-service "big bang."
- A service must run with WorkOS enabled in parallel with its legacy
  auth path for **at least one operator-week** before the legacy path
  is removed.
- If a migration introduces an operator-visible incident, the legacy
  path is the rollback target — do not roll back to "no auth."
- Sentinel-QC blocks promotion to `release_track: stable` for any
  service whose `auth_status` is `grace` past `auth_grace_until` or
  missing the `auth_standard` block entirely.

## Telemetry

Each migrated service emits a daily count of:

```
workos:success
workos:failed_callback
bearer:success            # legacy fallback path; trends to zero post-cutover
```

into `dk1-command-center` via the existing `audit_events` rollup. The
"bearer:success" trend is the primary signal that we can retire the
legacy path.
