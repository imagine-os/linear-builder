---
identifier: "PAP-687"
title: "Cross-browser functional smoke: run the `@smoke` e2e tag on WebKit and Firefox nightly and on PRs touching input, auth or realtime packages"
project: "quality"
projectName: "Quality Pipeline"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Developer"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-86"]
blocks: []
key: "r4/quality/cross-browser-functional-smoke"
url: "https://linear.app/paperos/issue/PAP-687/cross-browser-functional-smoke-run-the-smoke-e2e-tag-on-webkit-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:27.440Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-687: Cross-browser functional smoke: run the `@smoke` e2e tag on WebKit and Firefox nightly and on PRs touching input, auth or realtime packages

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). Every gate runs on Chromium; Tauri on macOS renders with WebKit and customers use Safari and Firefox. Running the existing `@smoke` functional tag on the other two engines nightly, and on PRs that touch the packages most likely to differ, catches passkey, drag-and-drop and WebSocket differences before a release.

**Scope**

* In: Playwright projects `webkit` and `firefox` in `playwright.functional.config.ts` limited to `@smoke`, nightly job step in PAP-253, PR path filter (`packages/input/**`, `packages/auth/**`, `packages/realtime/**`, `apps/web/src/routes/auth/**`), engine column in `reports/e2e.json`, known-difference allowlist `ops/quality/browser-known-diffs.yaml`, docs section.
* Out: visual baselines on other engines (fonts differ; stays Chromium), mobile Safari devices, Tauri process testing.

**Spec**

* Projects reuse the PAP-86 fixtures; WebAuthn virtual authenticator is Chromium-only so passkey tests run `test.skip` on WebKit and Firefox with reason `webauthn-cdp` and the magic-link path covers sign-in.
* Known differences file: `{ testId, engine, reason, expires }`; expired entries fail; the collector (PAP-90) scores flakes per engine key.
* Nightly: both engines on staging after the Chromium `@full` run; PRs: only when the path filter matches, informational for the first week then blocking.
* Report: `reports/e2e.json` gains `engine`; the sticky comment shows a three-column pass table.

**Interface contract**

* Provides: projects `webkit` and `firefox`, `browser-known-diffs.yaml` schema, engine dimension in `e2e.json` and `flakes-delta.json`.
* Consumes: PAP-86 suite and fixtures, PAP-253 nightly slot, PAP-90 flake keys, Playwright image with all three engines (PAP-246 pin).

**Definition of done**

* `@smoke` passes on both engines for three nights; seeded WebKit-only difference (a `:has()` selector bug) fails only the WebKit column (link).
* PR path filter proven on a PR touching `packages/input`; docs section; changelog under "Quality".

**Test plan**

* Unit: known-diff expiry, path filter, report column writer.
* E2E: nightly three-engine run; a filtered PR.

**Demo**

Open the nightly report: three engine columns for the smoke suite, one expired known-diff failing with its reason. Under one minute.

**Edge cases**

* Engine-specific flake: quarantined per engine key by PAP-90, not for all engines.
* Runner lacks WebKit system deps: the pinned Playwright image includes them; a mismatch prints the environment warning and marks the column `error`.
* Firefox lacks a needed API (View Transitions): `browser-known-diffs` entry with expiry and a progressive-enhancement note.

**Dependencies**

Hard: PAP-86. Soft: PAP-253, PAP-90, PAP-246.

**Agent**

Builder: Sentinel (Edge Case Hunter) with Nova on input differences. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
