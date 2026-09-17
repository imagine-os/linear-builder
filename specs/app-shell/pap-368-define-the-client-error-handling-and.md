---
identifier: "PAP-368"
title: "Define the client error handling and crash reporting contract: error boundaries, error code catalogue, user-facing copy, browser and Tauri crash reports into observability"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Developer", "Staff"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: []
blocks: []
key: "gap/app-shell/client-errors"
url: "https://linear.app/paperos/issue/PAP-368/define-the-client-error-handling-and-crash-reporting-contract-error"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:01:27.454Z"
---

# PAP-368: Define the client error handling and crash reporting contract: error boundaries, error code catalogue, user-facing copy, browser and Tauri crash reports into observability

**Goal**

One `reportError()` and one `<ErrorBoundary>` used by the shell, codegen and Tauri, with an error code catalogue and user-facing copy, and browser and Rust panic reports flowing into the PAP-40 collector through `/api/otel`. PAP-17 declares `VITE_SENTRY_DSN` and every spec has an error state, but nobody owns client error reporting today.

**Scope**

In:

* `packages/core/src/errors/`: `AppError` with `code`, `message`, `hint`, `requestId`, `cause`; catalogue `errors.yaml` mapping codes to user copy (i18n keys via PAP-27); `reportError(err, ctx)` batching to `/api/otel` with breadcrumbs.
* `<ErrorBoundary>` (route-level and slot-level) with retry, "copy diagnostics" and the short request id; `ui.errorState` component in `@paperos/ui` that PAP-120 codegen targets.
* Tauri: Rust panic hook and `tauri-plugin-log` forwarding to the same endpoint; unhandled promise and `window.onerror` capture; service worker errors.
* Sentry-compatible envelope export optional behind `VITE_SENTRY_DSN` for teams that prefer it.
* Dedupe and rate limit: same fingerprint reported once per minute per client.

Out: server error handling (PAP-35 error mapping), alert rules (PAP-40).

**Spec**

* Fingerprint = code plus top stack frame plus route; PII scrubbed with the PAP-40 denylist before send.
* API errors (`ApiErrorCode`) map one-to-one to catalogue entries; unknown codes render the generic entry and log a catalogue miss.
* Offline: reports queued in IndexedDB, flushed on reconnect, capped at 200.
* Copy rules in `errors.yaml`: what happened, what to do, no blame; reviewed by Quill.

**Interface contract**

Provides: `AppError`, `reportError`, `ErrorBoundary`, `ErrorState` (the `ui.errorState` target), `errors.yaml` catalogue and generated `ErrorCode` union, Tauri panic forwarding. Consumes: `/api/otel` and PII denylist (PAP-40), `ApiErrorCode` (PAP-35), `VITE_SENTRY_DSN` (PAP-17), i18n (PAP-27), routes (PAP-16), Tauri crate (PAP-19). Consumed by PAP-120 codegen, PAP-71, every page.

**Definition of done**

* Throwing in a route loader shows the boundary with retry and request id; the report appears in Tempo or Loki with route and code (screenshot).
* Rust panic in the desktop app produces a report and the app relaunches to the last route (recording).
* Vitest for fingerprinting, dedupe, offline queue and catalogue mapping; every `ApiErrorCode` has copy.
* `ErrorState` screenshots at seven widths light and dark; `docs/shell/errors.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: fingerprint stability across renders; one report per minute per fingerprint; PII scrub on messages containing emails; catalogue completeness test against `ApiErrorCode`.
* Integration: report reaches a local collector in CI compose with expected attributes.
* E2E: Playwright triggers a loader error, asserts boundary copy and copy-diagnostics content; offline queue flushes on reconnect.
* Rust: panic hook unit test with a mocked transport.
* Visual: boundary and inline error state at seven widths.

**Demo**

Reviewer appends `?__throw=1` to the dashboard URL on staging, sees the error boundary with a short id, clicks "copy diagnostics", pastes the id into Grafana Explore and finds the report. Under 90 seconds.

**Edge cases**

* Error inside the boundary's own render: fallback to a static HTML message.
* Collector unreachable: queue, cap, drop oldest.
* Error storms (render loop): circuit breaker stops reporting after 50 in a minute and reports one summary.
* Service worker update mid-report: queue survives.

**Dependencies**

PAP-16, PAP-17 (hard). Soft: PAP-19, PAP-27, PAP-35, PAP-40. Consumed by PAP-120, PAP-71.

**Agent**

Built by Forge with Quill on copy. Reviewed by Sentinel (Code Reviewer).

**Size**

M
