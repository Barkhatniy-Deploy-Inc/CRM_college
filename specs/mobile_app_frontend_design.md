# Mobile-first CRM frontend / app-like web experience

## Requirements

- While a user opens the CRM on a phone or tablet, the interface shall adapt navigation, spacing, and forms to touch input and viewport safe areas.
- When a supported browser offers installation, the interface shall expose a user-controlled install action; it shall never prompt automatically.
- When the network is unavailable, the app shell may show an offline screen, but authenticated API responses and tokens shall not be cached by a service worker.
- On desktop, current navigation and workflows shall remain available without regressions.

## Design

- Vue 3 application remains the sole frontend framework; no parallel React/Quasar stack is introduced.
- Add responsive bottom navigation for small viewports, compact sticky header, safe-area padding, and mobile-first input sizing.
- Add a web manifest, install prompt, and a small network-only/offline-aware service worker strategy for static shell resources only; never cache `/api`, `/ws`, or authenticated responses.
- Keep role-filtered navigation, Vue interpolation, HttpOnly cookie authentication, and existing route guards intact.

## Plan

- [x] Inspect current Vue shell, routes, existing page layouts and project constraints.
- [ ] Add responsive mobile navigation/shell and verify route/role behavior.
- [ ] Add installable web-app metadata and a safe offline fallback.
- [ ] Add tests for install-prompt state and service-worker registration constraints.
- [ ] Run lint, formatting, unit tests, production build, and inspect generated output.
