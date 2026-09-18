---
identifier: "PAP-644"
title: "Shared Playwright input fixtures: pressChord, sequence, touch gestures, pen, gamepad mock, drag helpers and input-modality assertions for every e2e and gate"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-150"]
blocks: ["PAP-83", "PAP-155", "PAP-156", "PAP-167", "PAP-341"]
key: "r4/input/playwright-input-fixtures"
url: "https://linear.app/paperos/issue/PAP-644/shared-playwright-input-fixtures-presschord-sequence-touch-gestures"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:35.111Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-23"
cycle: null
---

# PAP-644: Shared Playwright input fixtures: pressChord, sequence, touch gestures, pen, gamepad mock, drag helpers and input-modality assertions for every e2e and gate

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Every input, tables and quality spec writes Playwright tests that press chords, long-press, pinch, drag by keyboard or mock a gamepad, and each will write those helpers again. Ship `@paperos/input/testing` once so tests read like the specs and Gate 3 and PAP-156 reuse the same gestures.

**Scope**

In: `packages/input/src/testing/{chords,touch,pen,gamepad,drag,modality,index}.ts` exported as `@paperos/input/testing`; Playwright fixtures `test.extend({ input })`; CDP helpers for touch and pen; `expectModality(page, 'keyboard')`; `touchTargets(page)` (moved here from PAP-154's plan); docs page.

Out: the input runtime itself, visual baselines (PAP-246), device farms (PAP-371).

**Spec**

* `input.pressChord(page, 'mod+shift+k')` resolves `mod` per the page's `navigator.platform` and uses `keyboard.press`; `input.sequence(page, 'g i', { gapMs })`; `input.holdKey(page, 'Space', ms)`.
* `input.tap|longPress|swipe|pinch|pan(page, locator, opts)` via `page.touchscreen` and CDP `Input.dispatchTouchEvent` with realistic timing and slop; `input.pen(page, locator, strokes, { pressure })` via `Input.dispatchMouseEvent` with `pointerType: 'pen'`; `input.gamepad(page)` installs a `navigator.getGamepads` mock with `press(button)`, `stick(x, y)` and `connect|disconnect`.
* `input.dragKeyboard(page, handle, moves)` runs the PAP-330 grammar; `input.dragPointer(page, from, to, { steps })`; `input.expectAnnouncement(page, /Moved/)` reads the shared `LiveAnnouncer` region; `input.expectModality(page, 'keyboard'|'pointer')` reads `data-input-*` from PAP-150.
* Fixtures are pure Playwright with no app import so quality packages can depend on them without pulling React; typed and documented with one example per helper.
* CI: fixture self-tests run against a static HTML page in the package (no app) so they never block on app builds.

**Interface contract**

Provides: `@paperos/input/testing` package entry, the `input` Playwright fixture, `touchTargets(page)` audit helper (consumed by PAP-82 as planned in PAP-154), `expectAnnouncement`. Consumes: `data-input-*` attributes and thresholds (PAP-150), test-mode hooks (PAP-240), `LiveAnnouncer` DOM contract (PAP-152, soft), keyboard grammar (PAP-330, soft). Consumed by PAP-341, PAP-167, PAP-155 children, PAP-156 Tier 1, PAP-83 video flows, PAP-86, tables view e2e.

**Definition of done**

* Package published in the workspace with self-tests green on Chromium, Firefox and WebKit projects (touch and pen on Chromium only, documented).
* PAP-329 or PAP-341 test rewritten to use the fixture as the reference; `docs/platform/input/testing.md`; changelog; Linear comment on PAP-82, PAP-83, PAP-156.

**Test plan**

* Unit: chord resolution per platform; touch event sequencing timing; gamepad mock state machine.
* Self-test page: each helper produces the expected DOM events (recorded by an inline listener) on three browsers.
* E2E: none beyond self-tests (consumers exercise it).

**Demo**

Reviewer runs `pnpm --filter input test:e2e` and watches the self-test page log a chord, a pinch, a pen stroke with pressure and a gamepad press. Under one minute.

**Edge cases**

* Firefox lacks CDP: touch helpers skip with a clear message, never silently pass.
* `mod` on Linux in a macOS-emulated UA: resolved from the page, not the runner.
* Headless WebKit ignores `pointerType: 'pen'`: documented limitation.
* Announcement region absent: assertion fails with guidance to mount `LiveAnnouncer`.

**Dependencies**

PAP-150 (hard), PAP-240 (soft, test-mode hooks). Soft: PAP-152, PAP-330. Blocks the e2e steps of PAP-341, PAP-167, PAP-155, PAP-156 and PAP-83.

**Agent**

Builder: Nova (Product Systems Engineer) with Sentinel (Visual Inspector). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
