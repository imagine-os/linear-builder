---
identifier: "PAP-898"
title: "Build session replay: rrweb capture with PII masking driven by schema annotations, consent and sampling, storage budget, replay viewer linked to errors and support conversations, decision ADR"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Product analytics, experiments and abuse controls"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-37", "PAP-296", "PAP-355", "PAP-368", "PAP-412", "PAP-561", "PAP-897"]
blocks: []
key: "r4/platform-ops/session-replay"
url: "https://linear.app/paperos/issue/PAP-898/build-session-replay-rrweb-capture-with-pii-masking-driven-by-schema"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:16.200Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-898: Build session replay: rrweb capture with PII masking driven by schema annotations, consent and sampling, storage budget, replay viewer linked to errors and support conversations, decision ADR

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

See what the user saw when something went wrong, without seeing what they typed: rrweb capture in web and Tauri with masking of every input and of elements bound to `pii`-annotated fields (PAP-355), consent and sampling (100 percent on error, 5 percent otherwise, tenant-configurable), a storage budget on MinIO (PAP-37), a replay viewer in `/admin` and the tenant console linked from error reports (PAP-368) and support conversations (PAP-412), recorded as an ADR against the PAP-296 self-hosting budget.

**Scope**

In: `packages/analytics/src/replay/`: rrweb 2.x recorder with `maskAllInputs`, `maskTextSelector` generated from the PAP-355 `pii` annotations (components bound to a `pii` field render `data-pii`), block list for payment and signature routes (PAP-359, e-sign), canvas and media excluded; chunked upload to MinIO under `replays/<tenant>/<session>/` with a 30-day lifecycle. Sampling and consent: capture starts only with analytics consent; always-on buffer of 60 s flushed on `reportError` (PAP-368) so errors have context; otherwise 5 percent of sessions; tenant setting to disable entirely; platform staff sessions never captured on `/admin`. Viewer: `<ReplayPlayer/>` (rrweb-player) with the console log, network summary (no bodies) and the error timeline; links from PAP-368 error reports, PAP-412 conversations (when the customer consented) and PAP-40 traces via `session_id`. ADR `docs/adr/NNNN-session-replay.md`: rrweb self-hosted versus PostHog or OpenReplay against the PAP-296 6 GB budget and privacy posture; storage estimate per 1,000 sessions.

Out: Heatmaps. Replay of portal customers for tenants beyond consented support cases.

**Spec**

* Masking is fail-closed: an element without a resolvable binding inside a form is masked; the PAP-85 edge-case hunter fuzzes the DOM for leaks
* Replays are keyed to the actor hash, not the principal; support access to a customer replay requires the customer's consent flag on the conversation and is audited
* Storage budget per tenant from PAP-178 (`replayGb`); exceeding drops sampling to error-only
* Recorder overhead under 5 percent CPU and 2 MB memory on a mid-range phone (measured in PAP-87 runs)

**Interface contract**

Provides: `ReplayPort` default adapter, recorder integration, masking rules generator, `<ReplayPlayer/>`, links from errors and conversations, the ADR. Consumes: analytics consent and pipeline, PII annotations (PAP-355), error reporting (PAP-368), object storage (PAP-37), resource budget (PAP-296), support inbox (PAP-412), traces (PAP-40), entitlements (PAP-178). Consumed by: quality (visual gate cross-reference), growth support, assistant ("what happened?" summaries of a replay in v0.3).

**Definition of done**

* Replay of a seeded error on staging shows the last 60 s masked correctly; DOM fuzz finds zero unmasked `pii` text across 200 pages; storage lifecycle and budget proven; ADR merged
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: masking selector generation; sampling decisions; budget downgrade.
* Integration: error → buffer flush → viewer link; consent revoked → capture stops and pending chunks dropped.
* Adversarial: PAP-85 fixtures render PII in unusual elements (tooltips, aria-labels, title attributes) and must be masked.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Trigger a seeded error in the demo tenant's invoice page, open the error report in `/admin`, play the replay and show masked amounts and names with the console log beside it.

**Edge cases**

* Tauri window with a detached panel (PAP-262): each window records its own session linked by the window bus id
* Replay chunk upload fails offline: chunks are dropped, never stored locally beyond memory
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-897 (hard), PAP-355, PAP-368, PAP-37 (hard), PAP-296 (hard: budget), PAP-412, PAP-40, PAP-178 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/platform-ops/product-analytics` = PAP-897.
