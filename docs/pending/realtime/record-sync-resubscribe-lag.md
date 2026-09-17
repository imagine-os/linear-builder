---
key: "realtime/record-sync/resubscribe-lag"
title: "Permission-driven resubscribe and lag measurement"
project: "realtime"
parent: "PAP-143"
phase: "P1"
type: "Build"
priority: 1
size: null
surfaces: ["Developer"]
milestone: "Record sync and conflict UX"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
identifier: "PAP-328"
status: "created"
createdAt: "2026-09-17"
---

# Permission-driven resubscribe and lag measurement

**Goal**

Close PAP-143: when a permission change invalidates a shape the client drops and resubscribes, developers can inspect sync state, and the 500 ms p95 lag budget is measured with a real Electric container in CI.

**Scope**

In:

* `409 shape-invalid` handling: drop local rows for the shape, resubscribe, replay pending writes.
* Dev inspector `window.__paperosSync` listing shapes, row counts, `lsn` lag, outbox length and `forceConflict()`.
* Playwright lag test in `ops/compose/test.yml` (Postgres, Electric, API): 50 API writes, DOM polled in a second context, p95 asserted under 500 ms; result JSON committed.
* `docs/platform/realtime/record-sync.md` with data-flow diagram.

Out: hooks and reconciler (siblings).

**Spec**

* Resubscribe within one cycle (under 2 s); rows the user lost access to disappear without a reload.
* Inspector is tree-shaken out of production builds unless `?debug=sync`.

**Interface contract**

Exposes inspector shape `{ shapes[], lagMs, outboxLength }`, compose test stack reused by PAP-147 and PAP-148, docs. Consumes siblings 1 and 2, proxy 409 semantics (PAP-270), `/__test` role change endpoint (PAP-240).

**Definition of done**

* Revoking a role removes rows within one resubscribe cycle; lag test green in CI with p95 under 500 ms; docs merged; Linear comment with the measurement.

**Test plan**

* Vitest: 409 handler drops and resubscribes once, pending writes replayed after resubscribe.
* Integration: role revoked via `/__test` (PAP-240) and rows vanish within 2 s.
* Playwright: lag measurement as described; inspector shows a non-zero shape list.

**Demo**

Open the grid demo with `?debug=sync`, read `__paperosSync.shapes`, revoke your role in another tab and watch rows disappear; run `pnpm test:e2e --grep lag` and read the p95. Under two minutes.

**Edge cases**

* Repeated 409s (flapping role): back off to 30 s and show a toast.
* Electric restart mid-test: subscription resumes from the last offset.

**Dependencies**

Siblings 1 and 2 (hard). PAP-270, PAP-240 (soft).

**Agent**

Built by Nova. Reviewed by Sentinel (Code Reviewer).

**Size**

S: handler, inspector and one measured test.
