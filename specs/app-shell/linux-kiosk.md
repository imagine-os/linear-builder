---
identifier: "PAP-23"
title: "Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-145", "PAP-21", "PAP-263"]
blocks: []
key: "app-shell/linux-kiosk"
url: "https://linear.app/paperos/issue/PAP-23/support-linux-kiosk-and-parallel-browser-mode-launching-synced-windows"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-23: Support Linux kiosk and parallel-browser mode launching synced windows across displays from one CLI flag

**Goal**

From one CLI flag, launch a PaperOS desktop build in kiosk mode on Linux that opens one full-screen, synced window per connected display (or several browser windows in "parallel-browser" mode), so a shop, clinic or warehouse can run staff dashboards and signage from a single cheap box.

**Scope**

In:
- Tauri launch flags parsed in Rust: `--kiosk`, `--displays all|1,2`, `--routes /board,/queue` (one per display, cycled), `--parallel-browser` (spawn Chromium/Firefox windows instead of Tauri webviews for setups that need browser extensions), `--reload-hours 24`, `--watchdog`.
- `ops/kiosk/`: systemd user service template, `paperos-kiosk.service`, a `cage`/`sway` minimal compositor recipe, udev-less display detection via `available_monitors()`, `unclutter` cursor hiding, auto-login instructions for Debian/Ubuntu and Fedora.
- Kiosk window options: fullscreen, `always_on_top`, `decorations false`, `closable false`, disabled context menu and devtools, keyboard shortcut `Ctrl+Alt+Shift+Q` to exit (configurable, can be disabled).
- Health: watchdog restarts a crashed window; heartbeat endpoint `/_kiosk/health` for `data-layer/observability`; nightly reload.
- Remote config: `~/.config/paperos/kiosk.json` schema (Zod on TS side, serde on Rust side) editable from the staff console later.

Out: Windows/macOS kiosk, digital-signage content management, hardware provisioning, custom compositor.

**Spec**

- Startup sequence: parse flags -> enumerate displays -> for each selected display create `WebviewWindow` labelled `kiosk-<n>` with bounds = display bounds, `fullscreen(true)`, load route `${routes[n % routes.length]}?kiosk=1&display=n`.
- Routes receive `kiosk=1` search param; `AppShell` (`app-shell/router-layouts`) hides nav/command bar and enlarges type via a `data-kiosk` attribute (10-foot rules from `app-shell/device-matrix-research`).
- Cross-window coherence via `realtime/multi-window-sync` (selection, filters follow the primary display when `--follow-primary`).
- Parallel-browser mode: spawn `chromium --kiosk --app=<url> --window-position=<x>,<y> --user-data-dir=<tmp/n>` per display using `tauri-plugin-shell` sidecar; supervise children.
- Watchdog: Rust thread polls each window every 10 s; on missing window or webview crash (`tauri::WindowEvent::Destroyed`) recreate after 2 s backoff, max 10 tries, then exit non-zero for systemd restart.
- Logging to journald via `tracing-journald`.
- `paperos kiosk install` subcommand in `@paperos/cli` writes the systemd unit and config.

**Definition of done**

- On a Linux VM with two virtual displays (Xvfb or a real dual-monitor box): `paperos-desktop --kiosk --displays all --routes /board,/queue` shows both routes fullscreen; recording attached.
- Kill one window: watchdog restores it within 5 s (recording).
- `systemctl --user enable` recipe works from cold boot to app in under 60 s on Ubuntu 24.04.
- Rust unit tests for flag parsing and display-to-route assignment; Vitest for kiosk search-param handling.
- Screenshots at 1920x1080, 3840x2160 and a portrait 1080x1920 display.
- `docs/shell/kiosk.md` with hardware recommendations; CHANGELOG; Linear comment with recordings.

**Edge cases**

- Display hot-plugged after start: listen for monitor changes, open/close windows accordingly.
- Zero displays detected (headless): exit with code 4 and clear message.
- Network down at boot: shell loads from cache (`app-shell/pwa`), shows offline banner, retries.
- Screen blanking/DPMS: disable via config in compositor recipe; document.
- Portrait-rotated display: bounds already rotated by compositor; verify layout.
- Exit shortcut on a public screen: default disabled when `--public` flag set.

**Dependencies**

`app-shell/breakpoints-windows` (window manager, display enumeration), `realtime/multi-window-sync` (coherence). Soft: `app-shell/create-cli` for the install subcommand.

**Agent**

Built by Forge (Tauri Smith, Ops Runner for systemd). Reviewed by Sentinel (Edge Case Hunter for crash/hot-plug, Visual Inspector for 10-foot readability).

**Size**

M: builds on the window manager; Linux-only reduces surface, watchdog and systemd need real-hardware testing.
