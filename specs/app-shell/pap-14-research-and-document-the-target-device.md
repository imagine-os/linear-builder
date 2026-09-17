---
identifier: "PAP-14"
title: "Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-20", "PAP-21", "PAP-82", "PAP-246", "PAP-258", "PAP-261"]
key: "app-shell/device-matrix-research"
url: "https://linear.app/paperos/issue/PAP-14/research-and-document-the-target-device-matrix-phone-tablet-laptop"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:33.425Z"
---

# PAP-14: Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices

**Goal**

Decide and publish the device classes, viewport widths, DPRs and input modes PaperOS commits to, as one machine-readable matrix that the quality pipeline screenshots against (PAP-82, PAP-84) and that PAP-21 implements as container queries. The seven widths become the vocabulary every DoD in this plan uses.

**Scope**

In:

* Market and viewport data for phone, tablet, laptop, desktop, ultra-wide, TV/kiosk and foldable (StatCounter, Steam survey, Apple and Android device lists).
* `packages/core/src/devices/matrix.ts` plus generated `ops/ci/breakpoints.json`.
* Test-device recommendations (real and emulated) with cost.
* Guidance on container queries versus viewport breakpoints, DPR, safe areas, hover and pointer queries.

Out: CSS implementation (PAP-21), component design.

**Spec**

* Starting point to confirm or overturn with data: `xs 320`, `sm 375`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536`, `3xl 1920`; `tv 3840` documented as optional eighth.
* Entry shape: `{ name, minWidth, exampleDevices[], dpr[], pointer: 'coarse'|'fine'|'both', hover: boolean, orientation, safeArea: boolean }`.
* `pnpm gen:breakpoints` writes `breakpoints.json` from the TS file; CI fails when stale.
* Playwright mapping table per width: preset or `{ viewport, deviceScaleFactor, hasTouch, isMobile }`.
* Foldables: `device-posture` notes; unfolded treated as `md`. TV: 10-foot rules, focus ring minimums, 4K at DPR 1 and 2.
* `docs/research/device-matrix.md` (1,500-2,500 words) with sources, decision, rejected options, review date 2027-01.
* Three physical devices worth buying, with prices.

**Interface contract**

Provides:

* `BREAKPOINTS: readonly Breakpoint[]` and `DEVICE_CLASSES` from `@paperos/core/devices`; type `BreakpointName = 'xs'|'sm'|'md'|'lg'|'xl'|'2xl'|'3xl'`.
* `ops/ci/breakpoints.json` schema `{ version, breakpoints: [{ name, width, height, deviceScaleFactor, hasTouch, isMobile }] }` read by PAP-82 Playwright projects and PAP-84 video replays without importing TS.
* `PLAYWRIGHT_DEVICES` map for PAP-82.

Consumes: nothing. Changing a width after PAP-82 has baselines requires a baseline regeneration, so the file carries a `version` field.

**Definition of done**

* `matrix.ts`, `breakpoints.json` and the research doc merged; generator snapshot-tested.
* ADR `docs/adr/0002-device-matrix.md` records the seven widths.
* Placeholder app screenshots at all seven widths via a throwaway Playwright script attached to the PR.
* Sentinel (PAP-82 owner) approves on the PR.
* Linear comment linking the doc.

**Test plan**

* Unit: Vitest snapshot of `gen:breakpoints` output; type test that `BreakpointName` is exhaustive.
* Static: `pnpm gen:breakpoints --check` in CI detects a hand-edited JSON.
* Visual: seven screenshots of the placeholder page, one per width, plus 375 at DPR 3 and 1920 at DPR 1.
* Review: every numeric claim in the doc has a source URL; reviewer spot-checks three.

**Demo**

Reviewer opens `docs/research/device-matrix.md`, then runs `pnpm gen:breakpoints && cat ops/ci/breakpoints.json` and `pnpm exec playwright test scripts/matrix-shots.spec.ts` to produce the seven screenshots in `test-results/`. Under 2 minutes.

**Edge cases**

* Browser zoom 125-200 percent changes effective width; layouts must be tested at zoom.
* Split-screen tablets produce widths between breakpoints; behaviour for any width is defined.
* Virtual keyboard shrinking `100vh`; recommend `100dvh` and `interactive-widget=resizes-content`.
* Fractional DPR on Windows (1.25, 1.5).
* Old kiosks on Chromium 90-ish: state minimum browser versions.

**Dependencies**

None. Consumed by PAP-21, PAP-20, PAP-82, PAP-84, PAP-70, PAP-154, PAP-158.

**Agent**

Researched by Scout (Library Evaluator) with Forge confirming feasibility. Reviewed by Sentinel.

**Size**

S: half a day of research plus a small TS file and generator.
