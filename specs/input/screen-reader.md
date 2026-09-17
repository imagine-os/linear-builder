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
blockedBy: ["PAP-152", "PAP-73", "PAP-86"]
blocks: ["PAP-160"]
key: "input/screen-reader"
url: "https://linear.app/paperos/issue/PAP-156/test-and-fix-the-screen-reader-experience-nvda-voiceover-talkback-for"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-156: Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows

**Goal**

Verify with real assistive technology, not only axe, that the core PaperOS flows are usable with NVDA on Windows, VoiceOver on macOS and iOS, and TalkBack on Android, then fix what breaks. The deliverable is a repeatable test protocol, recorded results, and merged fixes across primitives, focus management and the shell, so every later app inherits a working screen-reader experience.

**Scope**

In:
- Test protocol `docs/platform/a11y/screen-reader-protocol.md`: environment setup per AT (NVDA 2025.x with Firefox and Chrome, VoiceOver with Safari on macOS 15 and iOS 18, TalkBack with Chrome on Android 15), the flow scripts, what to record (spoken output transcript, pass/fail, severity per `quality/review-rubrics`).
- Core flows from `quality/e2e-flows`: sign in (passkey and magic link), tenant switch, navigate via skip links and `F6`, create/edit/delete a record in the grid, filter and sort a view, post a comment with a mention, open the command palette and run a command, receive a live update, complete a drag with the keyboard.
- Automated layer: Playwright with `@guidepup/playwright` (VoiceOver and NVDA driver) running the flows on macOS and Windows runners nightly, asserting the spoken phrase snapshots; TalkBack remains manual on a device or emulator with a recorded video.
- Fix pass: every Sev-1/Sev-2 finding fixed in this issue's PR chain (or filed as blocking issues in the owning project with `a11y` label if outside `packages/ui`, `packages/input`, shell).
- Results report `docs/platform/a11y/screen-reader-results-<date>.md` with the matrix (flow × AT × browser) and links to fixes.

Out: eye tracking or switch access, third-party embedded widgets (Stripe elements are tested by Stripe), full WCAG documentation (`input/a11y-statement`).

**Spec**

- Snapshot format for automated runs: JSON `{ flow, at, browser, steps: [{ action, spoken, expected, pass }] }` stored under `apps/web/e2e/a11y/snapshots/`; phrases matched with normalisation (case, punctuation, trailing "button"/"link" role words allowed).
- Conformance targets: every interactive element has an accessible name; roles and states match visual state; live regions announce remote changes at the agreed cadence (`realtime/presence`, `realtime/conflict-ux`); virtualised grids expose `aria-rowcount`/`aria-rowindex`; tables of over 50 columns provide a column picker reachable by keyboard; dialogs announce their title on open; toasts are `role="status"`.
- Windows runner: self-hosted GitHub/Forgejo runner (`forge/actions-runner`) VM with NVDA installed; macOS runner uses the hosted `macos-15` image with VoiceOver enabled via `guidepup` setup.
- Severity: Sev-1 blocks a flow, Sev-2 requires workaround, Sev-3 cosmetic; Sev-1/2 must be fixed before the milestone `Touch, pen, gamepad` closes.
- Each fix includes a regression snapshot so the nightly run guards it.

**Definition of done**

- Protocol document merged and linked from `quality/review-rubrics`.
- Nightly `a11y-sr` job runs NVDA and VoiceOver flows green for three nights; failures post to Linear via `pm-linear/webhooks`.
- TalkBack manual run recorded (video) for all flows on a Pixel emulator or device, results in the report.
- Results report shows zero open Sev-1 and Sev-2 across the matrix; Sev-3 items filed as issues.
- At least the following fixes merged if found: grid row/col semantics, palette `aria-activedescendant`, live-region cadence, dialog titles, drag announcements.
- Changelog entry and Linear comment with the report link and one screenshot of the matrix.

**Edge cases**

- VoiceOver on iOS in a Tauri webview (WKWebView) differs from Safari: run the iOS flows in the Tauri app too, not only Safari.
- NVDA browse vs focus mode switching in the grid: ensure `role="application"` is never used and arrow keys work in focus mode.
- Speech output includes dynamic numbers (row counts, timestamps): snapshot normaliser replaces digits with `#`.
- Flaky AT startup on runners: retry once and quarantine per `quality/flake-quarantine`, never silently pass.
- Non-English locale on a runner: force `en-US` speech for stable snapshots; note localisation as a follow-up.
- Reduced-motion and high-contrast themes (`design-system/theming`): run one flow per theme to catch state-only-by-colour regressions.

**Dependencies**

- `input/focus-management`, `design-system/primitives`, `design-system/a11y-audit` (component-level baseline), `quality/e2e-flows` (flow scripts), `forge/actions-runner` (Windows runner), `quality/flake-quarantine`, `input/drag-drop` (keyboard drag flow). Feeds `input/a11y-statement`.

**Agent**

Builder: Sentinel (Visual Inspector sub-agent runs the protocol; Code Reviewer prepares fixes) with Iris (Component Crafter) fixing `packages/ui`. Reviewer: Nova for `packages/input` fixes; Justin sees only the final matrix in the release digest.

**Size**

M: protocol and automation are bounded; the fix list is the unknown, capped by severity rules.
