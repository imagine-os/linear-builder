---
identifier: "PAP-690"
title: "Desktop smoke via `tauri-driver` on Linux: launch the packaged app, sign in through the deep link, open a record and detach a panel, recorded nightly"
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
blockedBy: ["PAP-240", "PAP-256", "PAP-257"]
blocks: []
key: "r4/quality/desktop-tauri-smoke"
url: "https://linear.app/paperos/issue/PAP-690/desktop-smoke-via-tauri-driver-on-linux-launch-the-packaged-app-sign"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:25.581Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-690: Desktop smoke via `tauri-driver` on Linux: launch the packaged app, sign in through the deep link, open a record and detach a panel, recorded nightly

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Deferred to v0.2 by round 4 (not claimable before 2026-10-01; NJ-14 can reinstate). PAP-86 excludes native Tauri e2e and PAP-156 waits on macOS and Windows runners (PAP-371). A Linux-only WebDriver smoke through `tauri-driver` against the built AppImage still proves the shell boots, the deep-link session flow works and multi-window detach behaves, nightly and on release candidates.

**Scope**

* In: `apps/desktop/e2e/` with `tauri-driver` and WebdriverIO, nightly job step after the PAP-256 Linux build, flows sign-in via `paperos://` deep link (PAP-225), open a record, detach a panel (PAP-262), quit; `xvfb` recording to MP4 through the PAP-83 post-processing; results into `reports/e2e.json` with `target: desktop-linux`.
* Out: macOS and Windows (PAP-371), mobile, visual baselines of the native window chrome.

**Spec**

* Job downloads the AppImage artefact from the PAP-256 build, runs `tauri-driver` with `xvfb-run`, WebdriverIO connects on 4444; test-mode API on the compose stack (PAP-240) provides seed and `login-as`, and the deep-link token is minted through the PAP-225 test hook.
* Flows are 4 steps each, `slowMo` 150, recorded with `ffmpeg -f x11grab`; failures keep the recording and the Tauri log.
* Report rows carry `target: desktop-linux`; PAP-254 certification treats a red desktop smoke as S1 (informational for the first week).
* Runtime under 6 minutes.

**Interface contract**

* Provides: `apps/desktop/e2e/**`, `target` dimension in `e2e.json`, the deep-link test hook contract with PAP-225.
* Consumes: PAP-256 Linux build artefact, PAP-257 deep links, PAP-240 test mode, PAP-262 window manager, PAP-83 ffmpeg step, PAP-50 runner with `xvfb` and WebKitGTK deps.

**Definition of done**

* Three nightly runs green with recordings; a seeded broken deep-link handler fails the sign-in flow with the recording attached (link).
* Docs section; changelog under "Quality".

**Test plan**

* Unit: none beyond the flow definitions; deep-link token minting unit test in PAP-225 scope.
* E2E: nightly desktop smoke; on-demand on `release/*` branches.

**Demo**

Open the nightly recording: the AppImage launches, the deep link signs in, a panel detaches into a second window and the app quits cleanly. Under one minute.

**Edge cases**

* WebKitGTK version drift on the runner: pinned in the runner image; mismatch marks the target `error` with the version.
* Deep link cannot be delivered under `xvfb`: fallback invokes the binary with the URL argument, documented.
* Detach opens the window off-screen: `list_displays` fixture sets a 1920×1080 virtual display.

**Dependencies**

Hard: PAP-256, PAP-257, PAP-240. Soft: PAP-225, PAP-262, PAP-83, PAP-50, PAP-371, PAP-254.

**Agent**

Builder: Forge (Tauri Smith) with Sentinel (Edge Case Hunter). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
