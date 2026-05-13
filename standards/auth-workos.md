# DK1 Auth Standard — WorkOS AuthKit (`auth_standard: workos@v1`)

Owner: Dan Kim
Status: Enforced for new services; existing services migrate per
[`auth-workos-rollout.md`](./auth-workos-rollout.md).
Reference implementation:
[`dk1-ghtransna-orders` (Manifest) ADR 0009](https://github.com/dk1-capital/dk1-ghtransna-orders/blob/main/docs/adr/0009-workos-auth-standard.md).

## What this standard says

Every customer-facing or operator-facing DK1 surface — web app,
operator console, portal — authenticates humans via **WorkOS AuthKit
sealed-cookie sessions**. Service-to-service auth (worker→worker,
script→API, scheduled job→API) stays on existing tokens (`X-DK1-TOKEN`,
`CC_API_KEY`, signed-webhook HMAC) and is **out of scope** here.

## Required env vars (per service)

```
WORKOS_API_KEY              # sk_live_... or sk_test_...
WORKOS_CLIENT_ID            # client_01...
WORKOS_COOKIE_PASSWORD      # 32+ random bytes, distinct per service
WORKOS_REDIRECT_URI         # absolute URL of the service's callback endpoint
WORKOS_LOGOUT_REDIRECT_URI  # optional, defaults to "/login" relative to the service
```

Provisioned via WorkOS dashboard; stored in
`/home/dan/dk1/configs/.env.<service>` on dk1-core (or the equivalent
secrets injector for the deploy target). Never checked in.

## Required behaviors

1. Service exposes `GET /v1/auth/workos/login` (302 to AuthKit),
   `GET /v1/auth/workos/callback` (exchange + seal + redirect),
   `POST /v1/auth/workos/logout` (clear cookie + WorkOS session end).
2. Auth dependency / middleware accepts the sealed cookie and resolves
   it to a local `users` row keyed by email. Auto-provision on first
   sight of a valid identity; admin elevation is an out-of-band write,
   never inferred from claims unless explicitly mapped via WorkOS
   organization roles.
3. Service-to-service tokens are rejected on user endpoints; user
   sessions are rejected on machine-only endpoints. The two namespaces
   never bleed.
4. Frontend stores **no auth tokens in `localStorage`**. The session
   travels in an httpOnly sealed cookie; client fetches use
   `credentials: "include"`.
5. On 401 from any user-scoped endpoint, the frontend redirects to
   `/login?next=<current-url>` and `/login` honors the `next` param
   (rejecting any value that doesn't start with a single `/`).
6. Every login outcome (success and failure) writes one row to the
   service's audit trail with `actor=<email>`, `action` ∈
   `{workos:success, workos:failed_callback, bearer:success}`.

## Family-manifest declaration

Each service declares conformance in its `family.manifest.yaml`:

```yaml
auth_standard: workos@v1
auth_status: enforced            # enforced | grace | exempt
auth_grace_until: null           # ISO date if status=grace
auth_exemption_reason: null      # required if status=exempt
```

DK1 Sentinel-QC enforces the presence + validity of this block on
every nightly portfolio sweep. New repos missing the block fail
promotion to `release_track: stable`.

## Exemptions

A service may declare `auth_status: exempt` with a documented reason in
`auth_exemption_reason`. Acceptable reasons (non-exhaustive):

- **Local-only operator tools** binding `127.0.0.1` (e.g.
  `dk1-control-tower`). The OS-user check is sufficient.
- **Public marketing sites** with no authenticated surface
  (e.g. `dk1-ai`).
- **Pure machine APIs** with no human UI (service-to-service only).

Every exemption is reviewed quarterly.

## Migration grace window

Existing services in active development may declare
`auth_status: grace` with `auth_grace_until` set to a date no further
out than the rollout-doc-listed migration target. After the grace date
expires, Sentinel-QC blocks the service's CI deploys until the
migration lands.
