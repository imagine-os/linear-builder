---
key: "spec-builder/layout-codegen/examples"
title: "Layout codegen: generate the three example specs, screenshot seven widths and pass conformance with zero manual edits"
project: "spec-builder"
parent: "PAP-120"
phase: "P1"
type: "Build"
priority: null
size: "S"
surfaces: ["Developer"]
milestone: null
intendedState: "Backlog"
blockedBy: ["spec-builder/layout-codegen/templates", "spec-builder/layout-codegen/wiring"]
blocks: []
source: "round2/agent2/new_spec.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b"
identifier: "PAP-316"
status: "created"
createdAt: "2026-09-17"
---

# Layout codegen: generate the three example specs, screenshot seven widths and pass conformance with zero manual edits

**Goal**

Prove the generator on the three PAP-125 example specs: generate, typecheck, render, screenshot every state at seven widths in both themes, publish the stories and pass the PAP-122 conformance suites without touching a generated file by hand.

**Scope**

* In: generated files for `customer-invoices`, `staff-dashboard`, `agent-console` committed, Playwright capture, Storybook publication (PAP-69), conformance run, `docs/spec/codegen.md` walkthrough.
* Out: template and wiring code (sibling children), documentation prose beyond the walkthrough (PAP-125).

**Spec**

* Run `pnpm spec gen:page --all` for the examples; commit route, view, logic stub and stories; `--check` in gate 1 covers them.
* Playwright: each state of each page at 320, 375, 768, 1024, 1280, 1536 and 1920 px, light and dark, using PAP-240 login and seeds; artifacts named per PAP-82 (`screenshots/<page>/<state>/<width>-<theme>.png`).
* Storybook: stories appear in the PAP-69 deployment under `Generated/<page>`.
* Conformance: `pnpm spec gen:tests --all` then run; expect green with zero edits to generated files (CI asserts `git diff --exit-code` on `generated/`).
* Contact sheet: `pnpm screenshots:sheet` (PAP-82 reporter) assembles one image per page with the seven widths in a row per state, attached to the PR and the Linear comment so a reviewer reads the whole matrix at a glance.
* Walkthrough in `docs/spec/codegen.md`: the exact commands in order, expected output file list and how to fix a red `generated-untouched` assertion (edit the spec or the component, regenerate, never the output).

**Interface contract**

* Provides: committed generated examples as reference output, the screenshot set consumed by PAP-125 docs, the CI assertion pattern `generated-untouched`.
* Consumers: PAP-125, PAP-122, PAP-82 matrix, PAP-105 `page-from-spec` (points at the examples), PAP-29 drill.
* Requires: sibling children, PAP-122 generator, PAP-240, PAP-69, PAP-82 naming.

**Definition of done**

* Three pages generate and typecheck; conformance suites green; `generated-untouched` assertion passes.
* Screenshot matrix attached (three pages, up to six states, seven widths, two themes).
* Stories visible at the Storybook URL; walkthrough section; changelog; Linear comment with links.

**Test plan**

* Integration: full chain in CI (`gen:page`, `gen:data` if available, `gen:tests`, vitest, playwright).
* e2e: Playwright capture suite.
* Visual: the full matrix through gate 3.

**Demo**

Open the Storybook link, browse `Generated/customer-invoices` states, then open the Linear comment's contact sheet and compare the 320 px and 1920 px renders of the dashboard. One minute.

**Edge cases**

* `staff-dashboard` needs PAP-173 blocks: fallback `ui.responsiveGrid` with a callout naming PAP-173.
* `agent-console` needs PAP-129 data: mocked hooks in stories; Playwright uses the seed.
* Flaky screenshot from animation: PAP-72 reduced-motion flag forced.
* 320 px overflow found: fix in the spec or component, never in generated files.
* Theme token missing in dark: report to PAP-66 with the screenshot.

**Dependencies**

Blocked by `spec-builder/layout-codegen/templates`, `spec-builder/layout-codegen/wiring`. Uses PAP-122, PAP-240, PAP-69, PAP-82.

**Agent**

Built by Nova; reviewed by Sentinel (Visual Inspector).

**Size**

S
