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
blocks: ["PAP-20", "PAP-21", "PAP-246", "PAP-258", "PAP-261", "PAP-82"]
key: "app-shell/device-matrix-research"
url: "https://linear.app/paperos/issue/PAP-14/research-and-document-the-target-device-matrix-phone-tablet-laptop"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-14: Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices

**Goal**

Decide and document the exact set of device classes, viewport widths, DPRs and input modes PaperOS commits to supporting, and publish the 7-width breakpoint matrix that the quality pipeline (`quality/playwright-matrix`, `quality/video-replays`) screenshots against and that `app-shell/breakpoints-windows` implements.

**Scope**

In:
- Research current market share and viewport data for phone, tablet, laptop, desktop, ultra-wide, TV/kiosk and foldable classes (StatCounter, Steam hardware survey, Apple/Android device lists).
- A machine-readable matrix file consumed by CI and the app.
- A test-device recommendation list (real and emulated) with cost.
- Guidance on container queries vs viewport breakpoints, DPR handling, safe areas and hover/pointer capability queries.

Out: implementing the breakpoints in CSS (that is `app-shell/breakpoints-windows`); designing components.

**Spec**

- Deliver `packages/core/src/devices/matrix.ts` exporting `BREAKPOINTS` (7 named widths) and `DEVICE_CLASSES`. Recommended starting point to validate or overturn with data: `xs 320`, `sm 375`, `md 768`, `lg 1024`, `xl 1280`, `2xl 1536`, `3xl 1920`, with `tv 3840` documented as an optional eighth for kiosk work.
- Each entry: `{ name, minWidth, exampleDevices[], dpr[], pointer: 'coarse'|'fine'|'both', hover: boolean, orientation: 'portrait'|'landscape'|'both', safeArea: boolean }`.
- `ops/ci/breakpoints.json` generated from the TS file (single source of truth, generation script `pnpm gen:breakpoints`) so Playwright projects can read it without importing TS.
- Foldables: document posture (`device-posture` API) and the dual-screen span; recommend treating unfolded as `md`.
- TV/kiosk: 10-foot UI notes, focus ring minimums, 4K at DPR 1 and 2.
- Write `docs/research/device-matrix.md` (1,500-2,500 words) with data sources, the decision, rejected alternatives and a review date (2027-01).
- Provide a Playwright `devices` mapping table: for each width, the `playwright.devices` preset or custom viewport + `deviceScaleFactor` + `hasTouch` + `isMobile`.
- Propose the 3 physical devices worth buying under $600 total and the emulator/simulator path for the rest.

**Definition of done**

- `matrix.ts`, generated `breakpoints.json` and the research doc merged; generation script covered by a Vitest snapshot test.
- ADR `docs/adr/0002-device-matrix.md` records the 7 widths and why.
- Screenshots of the placeholder web app rendered at all 7 widths via a throwaway Playwright script, attached to the PR as proof the matrix is executable.
- `quality/playwright-matrix` owner (Sentinel) has commented approval on the PR.
- CHANGELOG Unreleased entry.
- Linear comment linking the doc on the Pages demo (`/docs/research/device-matrix`) once the docs engine exists, or the raw file URL until then.

**Edge cases**

- Browser zoom at 125-200 percent changes effective CSS width; document that layouts must be tested at zoom, not only at viewport.
- Split-screen tablets produce widths between named breakpoints; matrix must define behaviour for any width, not just the seven.
- Virtual keyboard shrinking `100vh` on mobile; recommend `100dvh` and `interactive-widget=resizes-content`.
- Notch/safe-area insets on iOS and Android gesture bars.
- Windows display scaling producing fractional DPR (1.25, 1.5).
- Very old kiosks locked to Chromium 90-ish; state minimum browser versions.

**Dependencies**

None. Consumed by `app-shell/breakpoints-windows`, `quality/playwright-matrix`, `quality/video-replays`, `design-system/layout-components`, `input/touch-gestures`, `input/gamepad`.

**Agent**

Researched by Scout (Library Evaluator sub-agent) with Forge as co-owner for the TS artefact. Reviewed by Sentinel (Visual Inspector) and Iris.

**Size**

S: a day of research and one small package; the value is in the decision being written down once.
