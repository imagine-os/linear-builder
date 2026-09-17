---
key: "spec-builder/data-section/example"
title: "Data section: `customer-invoices` end to end with live sync, second-context and offline tests"
project: "spec-builder"
parent: "PAP-119"
phase: "P1"
type: "Build"
priority: null
size: "M"
surfaces: ["Developer"]
milestone: null
intendedState: "Backlog"
blockedBy: ["spec-builder/data-section/schema", "spec-builder/data-section/generator"]
blocks: []
source: "round2/agent2/new_spec.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b"
status: "pending"
---

# Data section: `customer-invoices` end to end with live sync, second-context and offline tests

**Goal**

Prove the data section on a real page: the `customer-invoices` example uses generated hooks against seeded Postgres in `live` mode, a mutation in one browser shows in another within a second, and an offline mutation queues and applies on reconnect, all captured by Playwright at phone and desktop widths.

**Scope**

* In: the example's `data` section finalised, generated hooks committed, a minimal page wiring (or PAP-120 scaffold when available), Playwright suite `apps/web/e2e/data-section.spec.ts`, seeds via PAP-240, `docs/spec/data.md` usage section.
* Out: the generator and schema (sibling children), the full example documentation (PAP-125).

**Spec**

* Spec: query `invoices` (`live`, filter open or overdue, sort `dueAt`, fields including `customer.name`, page 50) and mutation `markPaid` (`update`, optimistic, audit).
* Page renders the list with `dataStates` mapping to loading, empty and error components (PAP-234, PAP-71) and a `Mark paid` button per row bound to `useMarkPaid`.
* Tests: two browser contexts logged in as `customer.any` via PAP-240 `login-as`; context A marks paid; context B sees the status within 1 s; `context.setOffline(true)` in A, mark another, badge shows pending, `setOffline(false)`, applied and audit row written with `reason`.
* Screenshots at 375 and 1280 px in light and dark for success, empty and error states.

**Interface contract**

* Provides: the canonical `customer-invoices` data section reused by PAP-125, PAP-120 and PAP-122; the e2e suite as a template for other pages; seed `invoices-basic` in PAP-240.
* Consumers: PAP-125 docs embed these screenshots; PAP-120 example child renders the same page; PAP-82 includes the page in the matrix.
* Requires: sibling children, PAP-36 Electric shape for `invoice`, PAP-240 seeds and login, PAP-38 audit, PAP-234 and PAP-71 components.

**Definition of done**

* Playwright suite green in CI on both forges with the timing assertions.
* Screenshots attached; audit row visible in the PAP-38 log for the mutation.
* Docs usage section; changelog; Linear comment with screenshots and the recording of the second-context update.

**Test plan**

* e2e (Playwright): the two-context and offline scenarios at 375 and 1280 px.
* Integration: hooks against the real seeded API in the test-mode stack.
* Visual: three states, two widths, two themes through gate 3.

**Demo**

Open the example in two windows side by side, click `Mark paid` in one and watch the other update; toggle offline in DevTools, mark another, reconnect, and see it sync with the audit entry. Two minutes.

**Edge cases**

* Electric not deployed in CI: suite falls back to `server` mode with a `test.skip` reason for the second-context timing.
* Slow CI: timing threshold 1 s local, 3 s CI with the value reported.
* Seed drift: fixed dates and ids from PAP-240.
* Mutation rejected by RLS: rollback and error toast asserted.
* Audit `reason` empty: mutation refused client-side with a message.

**Dependencies**

Blocked by `spec-builder/data-section/schema`, `spec-builder/data-section/generator`. Uses PAP-36, PAP-240, PAP-38, PAP-234.

**Agent**

Built by Nova with Forge; reviewed by Sentinel (Edge Case Hunter).

**Size**

M
