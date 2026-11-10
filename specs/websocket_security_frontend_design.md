# WebSocket, security and frontend audit

## Requirements (EARS)

- While an authenticated user views the schedule, when schedule data changes, the system shall refresh that view from the API after a WebSocket event.
- While a browser opens `/ws`, the system shall validate the request Origin and authenticate it using the existing HttpOnly access cookie.
- When a WebSocket client disconnects or cannot receive an event, the system shall clean up its connection without failing the originating HTTP mutation.
- The frontend shall not persist access or refresh JWTs in browser storage or expose them in WebSocket URLs.

## Architecture

- Frontend: a component-scoped WebSocket lifecycle in `ScheduleView.vue`, same-origin `/ws`, bounded reconnect delay, refresh on valid event, cleanup on unmount.
- Backend: strict normalized Origin validation, existing shared JWT validation via cookie, idempotent connection cleanup and best-effort broadcast.
- Security: no query-string JWT, Origin required and allowlisted, authorization remains server-side for mutations, Vue text interpolation remains escaped.

## Implementation Plan

- [x] Inspect Nginx routing, backend event producers, auth cookies and frontend API/session flow.
- [x] Harden WebSocket handshake and connection manager; add Origin/auth/cleanup tests.
- [x] Connect schedule UI to events with reconnection and cleanup.
- [x] Stop frontend storage/use of JWT response values.
- [x] Run available frontend and backend syntax/config checks; document environment limits and residual findings.

## Security checklist

- Authentication: access JWT cookie validated by the schedule service; no unauthenticated connection.
- Authorization: WebSocket delivers only existing schedule change notifications; state reads/mutations still use their API checks. Broadcast scoping remains a follow-up if events become user-specific.
- Input: the socket only accepts/ignores heartbeat text; no client-supplied event commands are processed.
- Output: frontend renders server data using Vue interpolation, not `v-html`.
- Rate limiting/logging: connection count and security failures are logged; per-IP connection throttling is not currently available and is a residual operational hardening item.
