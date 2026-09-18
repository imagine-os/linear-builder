---
identifier: "PAP-23"
title: "Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-21", "PAP-145", "PAP-263"]
blocks: ["PAP-871", "PAP-881"]
key: "app-shell/linux-kiosk"
url: "https://linear.app/paperos/issue/PAP-23/support-linux-kiosk-and-parallel-browser-mode-launching-synced-windows"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:45.428Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-23: Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Deferred label (excluded from Oct-1 scope)

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

From one CLI flag, launch a PaperOS desktop build in kiosk mode on Linux that opens one full-screen synced window per connected display, or several browser windows in parallel-browser mode, so a shop, clinic or warehouse runs staff dashboards and signage from one cheap box.

**Scope**

In:

* Rust flags `--kiosk`, `--displays all|1,2`, `--routes /board,/queue`, `--parallel-browser`, `--reload-hours 24`, `--watchdog`, `--public`.
* `ops/kiosk/`: systemd user unit, `cage`/`sway` recipe, `unclutter`, auto-login notes for Debian, Ubuntu and Fedora.
* Kiosk window options: fullscreen, always on top, no decorations, not closable, no context menu or devtools, exit chord `Ctrl+Alt+Shift+Q` (disabled with `--public`).
* Watchdog, `/_kiosk/health`, journald logging, nightly reload.
* `paperos kiosk install` in `@paperos/cli`.

Out: signage content, remote fleet management.

**Spec**

* Startup: parse flags, enumerate displays via PAP-21 `list_displays`, create `WebviewWindow` `kiosk-<n>` per selected display with display bounds, load `${routes[n % routes.length]}?kiosk=1&display=n`.
* `kiosk=1` makes `AppShell` hide nav and command bar and set `data-kiosk` for 10-foot type scale (PAP-14 rules).
* Parallel-browser: spawn `chromium --kiosk --app=<url> --window-position=<x>,<y> --user-data-dir=<tmp/n>` per display via the shell plugin sidecar; supervise children.
* Watchdog thread polls every 10 s; recreate after 2 s backoff, 10 tries, then exit non-zero for systemd.
* Coherence via PAP-145 (`--follow-primary` mirrors selection and filters).

**Interface contract**

Provides:

* Search params `kiosk=1&display=<n>` and the `data-kiosk` attribute on `<html>` that PAP-16 and PAP-70 style against.
* HTTP `GET /_kiosk/health` on `127.0.0.1:<port>` returning `{ ok, displays, windows, uptimeS }` scraped by PAP-40.
* systemd unit `paperos-kiosk.service` and config `~/.config/paperos/kiosk.toml` (`routes`, `displays`, `reloadHours`, `public`).
* CLI subcommand `paperos kiosk install|status`.

Consumes: `WindowManager.list_displays` (PAP-21), `BroadcastChannel('paperos-windows')` (PAP-145), PWA cache for offline boot (PAP-18).

**Definition of done**

* On a two-display Linux box or Xvfb VM, `paperos-desktop --kiosk --displays all --routes /board,/queue` shows both routes fullscreen (recording).
* Kill one window: restored within 5 s (recording).
* Cold boot to app under 60 s on Ubuntu 24.04 via the systemd recipe.
* Rust tests for flag parsing and display assignment; Vitest for kiosk params.
* Screenshots at 1920x1080, 3840x2160 and portrait 1080x1920; `docs/shell/kiosk.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: Rust flag parser table; route cycling for 1, 2, 3 displays with 2 routes; watchdog backoff.
* Integration: Vitest that `kiosk=1` hides nav and sets `data-kiosk`.
* E2E: Xvfb with two screens in CI, launch, assert two windows via `xdotool`, kill one, assert respawn within 5 s.
* Health: `curl /_kiosk/health` asserts `windows: 2`.
* Visual: three display sizes above, light and dark.

**Demo**

Reviewer runs `paperos-desktop --kiosk --displays all --routes /board,/queue` on a laptop with an external monitor: two fullscreen windows appear, one per screen; `xdotool` kills one and it returns within 5 s; `Ctrl+Alt+Shift+Q` exits. Under 2 minutes.

**Edge cases**

* Hot-plugged display: monitor-change listener opens or closes windows.
* Zero displays: exit code 4.
* Network down at boot: shell loads from cache, shows banner, retries.
* DPMS blanking disabled in compositor recipe.
* Portrait-rotated display: bounds already rotated; verified.

**Dependencies**

PAP-21 (window manager, displays), PAP-145 (coherence). Soft: PAP-22 install subcommand, PAP-18.

**Agent**

Built by Forge (Tauri Smith, Ops Runner for systemd). Reviewed by Sentinel (Edge Case Hunter).

**Size**

M: Rust launcher plus ops recipes.
