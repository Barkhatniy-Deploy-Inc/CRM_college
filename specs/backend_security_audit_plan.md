# Backend security and reliability audit

## Scope

Review the FastAPI auth, schedule and techcard services and the shared `crm_auth` package. Focus this implementation pass on confirmed auth/session and gateway rate-limit defects; report other findings with evidence rather than broad unmeasured rewrites.

## Requirements

- When an administrator changes a user's password or deactivates the account, the system shall revoke all refresh sessions for that user.
- When requests pass through the trusted Nginx gateway, the auth rate limiter shall key limits by the client address forwarded by that gateway, rather than charging all clients to the proxy container address.
- Rate-limit bookkeeping shall be bounded and stale entries shall be reclaimed.
- Tests shall prove the revocation and rate-limit keying behavior without using production services.

## Security design

- Authorization remains server-side: admin-only account mutation endpoints retain `require_role(ADMIN)`.
- Refresh-session revocation uses the existing database helper and parameterized ORM updates.
- Proxy IP headers are trusted only because backend services are private on the Compose network behind the Nginx gateway. Direct exposure of backend ports would require a trusted-proxy policy before relying on these headers.
- No password hashes are added to API responses; the existing auth JSON token response is intentionally unchanged for backwards compatibility.

## Implementation plan

- [x] Map service layout, dependencies, auth contract, session lifecycle and existing tests.
- [x] Revoke sessions on admin reset/deactivation and role changes; add regression tests.
- [x] Correct rate-limit client identity and bound in-memory state; add focused tests.
- [x] Require expiration on shared access and refresh JWTs; reject malformed non-Bearer auth headers.
- [x] Run service tests, Ruff, compile checks and dependency audit in an isolated Python 3.11 environment.
- [x] Report residual access-token revocation and infrastructure/test limitations.

## Residual findings

- Revoking refresh tokens does not invalidate already-issued access JWTs; they remain accepted until their short expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`). Immediate revocation requires a shared token-version/denylist or an auth-service verification call.
- In-memory rate limiting is process-local. For multiple auth replicas, use shared storage and configure trusted proxies explicitly.
- Current auth responses still include JWT values in JSON for compatibility with existing clients/tests. Removing JSON token fields requires a versioned API migration.
- Several async handlers use synchronous SQLAlchemy operations; broader conversion is a separate, measured performance refactor.
