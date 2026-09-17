---
identifier: "PAP-234"
title: "Build the state components codegen emits: ErrorState, DeniedState, OfflineBanner, IntegrationUnavailable, LoadingPage as spec-mapped `ui.*` components"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-68", "PAP-71", "PAP-459"]
blocks: ["PAP-120", "PAP-315"]
key: "design-system/state-components"
url: "https://linear.app/paperos/issue/PAP-234/build-the-state-components-codegen-emits-errorstate-deniedstate"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:11.367Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-234: Build the state components codegen emits: ErrorState, DeniedState, OfflineBanner, IntegrationUnavailable, LoadingPage as spec-mapped `ui.*` components

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Give every declared page state a real component so codegen (PAP-120) emits `ui.errorState`, `ui.deniedState`, `ui.offlineBanner`, `ui.integrationUnavailable` and `ui.loadingPage` instead of plain fallbacks, and every generated page shows the same loading, error, denied and offline experience.

**Scope**

* In: `packages/ui/src/states/` with `ErrorState` (error boundary aware, retry, report id), `DeniedState` (403 with explain in dev and a return link), `OfflineBanner` (moved from `packages/core/pwa` shell into the design system, with a thin re-export kept for PAP-18), `IntegrationUnavailable` (connector name, status, reconnect action), `LoadingPage` (skeleton composition per layout slot), `NotFoundState`; `meta.ts` for each; copy in one file for i18n.
* Out: `EmptyState` (PAP-71), error reporting transport (app-shell error handling issue), notifications.

**Spec**

* Common props: `{ title?, body?, illustration?, actions?: { primary?, secondary? }, testId? }` with sensible defaults per state; illustrations from PAP-68 (`error`, `no-permission`, `offline`).
* `ErrorState` accepts `error` and `resetErrorBoundary` (compatible with `react-error-boundary` 4.x); shows `errorId` from `reportError()` when available; in dev shows the stack in a `<details>`.
* `DeniedState` reads `useCan` explain text (PAP-59) in dev; production copy is generic.
* `OfflineBanner` subscribes to `navigator.onLine` plus the sync status from PAP-36 `useSyncStatus()`; renders in the layout `banner` slot; announces via `aria-live="polite"` once.
* `IntegrationUnavailable` takes `{ connector, reason: 'disconnected' | 'rate_limited' | 'error', retryAt? }` from PAP-121 status shape.
* `LoadingPage` composes `Skeleton` variants from PAP-71 by `layout` name (`list`, `detail`, `dashboard`, `form`).

**Interface contract**

* Provides: spec IDs `ui.errorState`, `ui.deniedState`, `ui.offlineBanner`, `ui.integrationUnavailable`, `ui.loadingPage`, `ui.notFoundState`; `StateProps` type; the `states` map `stateComponents: Record<PageState, ComponentType>` consumed by codegen.
* Requires: PAP-71 Skeleton, EmptyState; PAP-68 illustrations; soft PAP-59 `useCan`, PAP-36 `useSyncStatus`, PAP-121 connector status.
* Consumers: PAP-120 codegen states switch, PAP-122 conformance tests (declared states must render these ids), PAP-62 and PAP-63 shells.

**Definition of done**

* Six components with stories in light, dark and high-contrast; `vitest-axe` clean; `play` test for `ErrorState` retry.
* `stateComponents` map exported and consumed by PAP-120's template (PR or comment agreeing the import path).
* `OfflineBanner` toggles within one frame of the `offline` event in a Playwright test using `context.setOffline(true)`.
* Screenshots of the "States gallery" at 320, 375, 768, 1280, 1920.
* Docs section in `docs/design/data-display.md` "States"; changelog under "Design system".

**Test plan**

* Unit: default copy per state, dev-only details hidden in production build.
* Integration: error boundary catches a thrown render and shows `ErrorState`; retry re-renders.
* E2E: offline toggle; denied route renders `DeniedState` for a customer principal.
* Visual: gallery at five widths.

**Demo**

Open Storybook "States/Gallery", flip the theme toolbar through light, dark and hc; then in the example app open DevTools, set Offline, and watch the banner appear and announce. Under two minutes.

**Edge cases**

* Error inside `ErrorState` itself: minimal unstyled fallback text, never a blank screen.
* Offline flaps every second: banner debounced 2 s.
* Denied on the root route: `DeniedState` offers sign-out and tenant switch.
* Very small viewport (320): illustrations hidden, text remains.

**Dependencies**

PAP-71, PAP-68 (hard). Soft: PAP-59, PAP-36, PAP-121, PAP-18 (re-export).

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Visual Inspector) and Quill (codegen contract).

**Size**

S: six small compositions; the contract with codegen is the point.
