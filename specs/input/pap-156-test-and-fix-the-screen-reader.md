---
identifier: "PAP-156"
title: "Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Review"
priority: 1
surfaces: ["Customer"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-73", "PAP-86", "PAP-152"]
blocks: ["PAP-160"]
key: "input/screen-reader"
url: "https://linear.app/paperos/issue/PAP-156/test-and-fix-the-screen-reader-experience-nvda-voiceover-talkback-for"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:36.205Z"
---

# PAP-156: Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows

**Goal**

Verify with real assistive technology, not only axe, that core flows work with NVDA on Windows, VoiceOver on macOS and iOS, and TalkBack on Android, then fix what breaks. This issue is the single owner of manual AT testing (PAP-73 covers automated component audits). Deliverables: a repeatable protocol, recorded results, merged fixes, and a nightly job once the runners exist.

**Scope**

In:

* Protocol `docs/platform/a11y/screen-reader-protocol.md`: setup per AT (NVDA 2025.x, VoiceOver macOS 15 and iOS 18, TalkBack Android 15), flow scripts, recording format, severity per PAP-79.
* Flows from PAP-86: sign in (passkey, magic link), tenant switch, skip links and `F6`, create, edit and delete a record, filter and sort, comment with a mention, palette command, receive a live update, keyboard drag (PAP-155).
* Automated layer: `@guidepup/playwright` running VoiceOver and NVDA flows nightly, asserting normalised spoken snapshots under `apps/web/e2e/a11y/snapshots/`; TalkBack manual on a Pixel emulator with video.
* Tier 1 (runs today on Linux): ARIA snapshot (`toMatchAriaSnapshot`) and accessible-name audit for every flow, so most Sev-1 findings surface before any AT runner exists.
* Fix pass: Sev-1 and Sev-2 fixed here or filed with the `a11y` label; results report `docs/platform/a11y/screen-reader-results-<date>.md`.

Out: switch access, third-party widgets, the statement (PAP-160).

**Spec**

* Snapshot JSON `{ flow, at, browser, steps: [{ action, spoken, expected, pass }] }`; normaliser lowercases, strips punctuation and trailing role words, replaces digits with `#`.
* Conformance: every interactive element has a name; roles and states match visuals; live regions announce at the agreed cadence (PAP-141, PAP-144); grids expose `aria-rowcount`/`aria-rowindex`; dialogs announce titles; toasts `role="status"`; `role="application"` never used.
* Runners: the Windows NVDA VM and hosted `macos-15` runner are provisioned by the planned forge non-Linux runners issue; until they exist the nightly job runs Tier 1 only and is marked `partial` in the report, never green.
* Sev-1 and Sev-2 must close before the milestone.

**Interface contract**

Exposes: protocol doc, snapshot format above (consumed by PAP-160's `criteria-map.json` `sr-matrix` source), `a11y-sr` workflow with artifact `sr-results.json` `{ date, tier, matrix: [{ flow, at, browser, status, severity? }] }`, `@guidepup` helper `speakAndAssert(page, action, expected)`, the `a11y` label convention and fix PR trailer `A11y-Fixes: PAP-156`. Consumes: e2e flow scripts and test-mode login (PAP-86, PAP-240), primitives (PAP-67), focus utilities (PAP-152), drag flows (PAP-155), rubric severities (PAP-79), quarantine rules (PAP-90), Linear comment posting (PAP-97), non-Linux runners (forge gap; hard for Tier 2).

**Definition of done**

* Protocol merged and linked from PAP-79.
* Tier 1 job green nightly for three nights; Tier 2 (NVDA, VoiceOver) green for three nights once runners exist, failures posting to Linear.
* TalkBack manual run recorded for all flows; report shows zero open Sev-1 and Sev-2; Sev-3 filed.
* Changelog; Linear comment with the report link and one matrix screenshot.

**Test plan**

* Unit: snapshot normaliser (digits, punctuation, role words, locale forced to `en-US`); matrix builder from result files marks missing cells `not run`, never `pass`.
* Tier 1 Playwright (Linux, every PR on `a11y` label, nightly otherwise): ARIA snapshots per flow step at 375 and 1280; accessible-name audit fails on any unnamed control; dialog title announced via live region assertion.
* Tier 2 nightly: guidepup VoiceOver on `macos-15`, NVDA on the Windows VM (Firefox, Chrome), one flow per theme and one in the Tauri iOS webview; TalkBack videos attached manually.
* Flakes: retry once, then quarantine per PAP-90 with a visible `partial` flag.

**Demo**

Open the latest `screen-reader-results` report and read the matrix; run `pnpm e2e:a11y --tier 1 --flow create-record` locally and watch the ARIA snapshot diff; play the 30-second TalkBack clip of creating a record. Under two minutes.

**Edge cases**

* iOS Tauri webview differs from Safari: run flows in both.
* NVDA browse versus focus mode in grids: arrows must work in focus mode.
* Non-English runner locale: force `en-US`.
* Runner never provisioned before 10-01: report ships as `partial` with Tier 1 results and the risk stated; not silently green.

**Dependencies**

PAP-152, PAP-86, PAP-73 (hard, encoded). Soft: PAP-67, PAP-155, PAP-90, PAP-240, planned forge non-Linux runners issue (Tier 2). Blocks PAP-160.

**Agent**

Builder: Sentinel (Visual Inspector runs the protocol; Code Reviewer prepares fixes) with Iris fixing `packages/ui`. Reviewer: Nova for `packages/input` fixes; Justin sees only the final matrix in the release digest.

**Size**

M: protocol and automation are bounded; the fix list is capped by severity rules.
