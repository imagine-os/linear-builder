---
identifier: "PAP-508"
title: "Tauri WebDriver E2E harness: `tauri-driver` on Linux CI, test helpers for windows, deep links, updater and menu actions, and recorded runs attached to PRs"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-255"]
blocks: ["PAP-257", "PAP-262"]
key: "r4/app-shell/tauri-e2e-harness"
url: "https://linear.app/paperos/issue/PAP-508/tauri-webdriver-e2e-harness-tauri-driver-on-linux-ci-test-helpers-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:59.284Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-508: Tauri WebDriver E2E harness: `tauri-driver` on Linux CI, test helpers for windows, deep links, updater and menu actions, and recorded runs attached to PRs

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra M

**Goal**

PAP-257, PAP-262, PAP-263, PAP-23 and PAP-502 all say "Tauri WebDriver on Linux" in their test plans, but no issue sets it up. A Linux-only Claude session cannot produce the macOS recordings those DoDs also ask for, so an automated Linux harness is the only proof the gates can check. This issue builds it once for everyone.

**Scope**

In:

* `apps/desktop/e2e/` with `tauri-driver` and WebdriverIO (the Tauri-supported stack) running against a debug build under Xvfb on `ubuntu-22.04`; `pnpm e2e:desktop` locally and `ops/ci/desktop-e2e.yml` on PRs touching `apps/desktop` or `packages/core/src/{native,windows}`.
* Helpers in `apps/desktop/e2e/lib/`: `launchApp({ argv, env })`, `windows()` (labels, bounds, focus), `deepLink(url)` (via `xdg-open`), `menu(path)` (via the `__test_menu` dev command), `waitForRoute(path)`, `screenshot(name)` at 960x600, 1280x800, 1920x1080, `recordVideo()` with `ffmpeg` on the Xvfb display.
* Dev-only Tauri commands guarded by `cfg(debug_assertions)`: `__test_menu`, `__test_panic`, `__test_displays(topology)` to fake a two-display layout for PAP-262.
* Baseline suite: launch shows the web bundle and version; single instance (second launch focuses the first); deep link navigates; detach and dock a panel; update toast from a local `latest.json` server.
* Artefacts: screenshots and MP4 uploaded in the PAP-239 `videos.json` shape so Gate 3 tooling lists them.

Out: macOS and Windows automation (PAP-371 runners can run the same suite later; documented as `pending-runner`), mobile Maestro flows (PAP-260), the features under test.

**Spec**

* Runs in under 8 minutes on CI including the debug build with a Rust cache.
* Fake displays: `__test_displays` makes `list_displays` return the given topology so topology-hash tests are deterministic.
* Every helper is typed and documented in `docs/shell/desktop-e2e.md`; a failing test uploads the video and the `tauri-plugin-log` file.
* Wayland is not exercised in CI (Xvfb is X11); the harness records `display: x11` in the artefact.

**Interface contract**

Provides: `pnpm e2e:desktop`, helpers, dev-only test commands, `desktop-e2e.yml`, artefacts in `videos.json`; consumed by PAP-257, PAP-262, PAP-263, PAP-23, PAP-502, PAP-84 (video inspection), PAP-29.

Consumes: the crate and dev scripts (PAP-255), Gate 1 workflow conventions (PAP-78), artefact schema (PAP-239, soft), breakpoints for window sizes (PAP-14).

**Definition of done**

* Baseline suite green on CI with video and screenshots attached to the PR; a seeded failing test uploads its video.
* `__test_displays` two-display fixture drives a detach test that asserts the panel window bounds.
* `docs/shell/desktop-e2e.md`; the four consuming issues comment that their test plans now cite this harness; CHANGELOG; Linear comment.

**Test plan**

* Unit: helper parsing of window lists and deep-link URLs; artefact writer validates against `videos.json`.
* E2E: the baseline suite is the E2E: launch, single instance, deep link, detach and dock, update toast.

**Demo**

Reviewer opens the CI run, downloads `desktop-e2e.mp4` and watches the app launch, receive `paperos://open/settings`, detach the inspector to a fake second display and show the update toast. Under 2 minutes.

**Edge cases**

* `tauri-driver` version drifts from the Tauri crate: pinned together in `rust-toolchain.toml` and `package.json`; Renovate groups them (PAP-217).
* Xvfb without a compositor: window decorations absent; tests assert bounds, not chrome pixels.
* Debug build too slow: the workflow caches `target/` keyed on `Cargo.lock`.
* A test needs network (updater): served from a local static server started by the helper; no internet.

**Dependencies**

Hard: PAP-255. Soft: PAP-78 (the workflow joins Gate 1 when it lands; standalone `desktop-e2e.yml` until then), PAP-239, PAP-14, PAP-217. Unblocks the automated proofs of PAP-257 and PAP-262.

**Agent**

Builder: Forge (Tauri Smith) with Sentinel on artefacts. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/tauri-crash-reporting` = PAP-502.
