---
identifier: "PAP-255"
title: "Tauri desktop scaffold, capabilities and plugins (apps/desktop, menu, tray, dev scripts)"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-19"
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-256", "PAP-258"]
key: "child/PAP-19/0"
url: "https://linear.app/paperos/issue/PAP-255/tauri-desktop-scaffold-capabilities-and-plugins-appsdesktop-menu-tray"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-255: Tauri desktop scaffold, capabilities and plugins (apps/desktop, menu, tray, dev scripts)

**Goal**

Create `apps/desktop` as a Tauri 2 project wrapping `apps/web/dist`, with least-privilege capability files, the plugin set the shell needs, a native menu and tray, and dev scripts, so the other PAP-19 children and PAP-20 build on a running desktop app.

**Scope**

In: `src-tauri` crate in the root Cargo workspace; `tauri.conf.json`; capabilities `main.json` (`core:window`, `core:event`, `shell:open` https allowlist, `dialog`, `fs` scoped to app data, `notification`, `os`, `process`); plugins `window-state`, `dialog`, `fs`, `shell`, `os`; menu (File, Edit, View, Window, Help); tray with Show and Quit; commands `app_info`, `open_path`; mount PAP-17 `secret_*`; `pnpm dev:desktop`, `pnpm build:desktop`; `rust-toolchain.toml`; Linux deps documented.

Out: CI installers (child 2), updater, single instance, deep links (child 3), signing.

**Spec**

* `frontendDist: ../../web/dist`, `devUrl: http://localhost:5173`; desktop always builds the web bundle with `BASE_PATH=/`.
* Window 1280x800, min 960x600, native decorations, `titleBarStyle: 'Overlay'` on macOS.
* CSP `default-src 'self'; connect-src https: wss:; img-src 'self' data: blob: https:`.
* TS bridge `packages/core/src/native/desktop.ts`: `isDesktop()`, `getVersion()`, `appInfo()`.
* `<BuildInfo/>` shows `getVersion()` when running in Tauri.
* `cargo clippy -D warnings`, `cargo fmt --check` wired into Gate 1 for `apps/desktop`.

**Interface contract**

Provides: crate `paperos-desktop`, capability file layout, command names `app_info`, `open_path`, the TS bridge above, scripts `dev:desktop` and `build:desktop`. Consumes: web build (PAP-13), `secret_*` commands (PAP-17), `UpdateToast` (PAP-18). Children 2 and 3 and PAP-20 add to this crate without restructuring it.

**Definition of done**

* `pnpm dev:desktop` opens the app on Linux and macOS showing the web bundle and version.
* Capability files pass `tauri` schema validation; no wildcard permissions.
* Menu and tray work (recording); Rust and TS tests green; `docs/shell/desktop.md` dev section written.

**Test plan**

* Rust: `cargo test` for `app_info` and `open_path` (rejects non-https and paths outside app data).
* TS: Vitest for the bridge with mocked `__TAURI_INTERNALS__`.
* Static: capability JSON schema check; clippy and fmt.
* Manual recorded: menu items, tray Show and Quit on Linux and macOS.
* Visual: window at 960x600, 1280x800, 1920x1080.

**Demo**

Reviewer runs `pnpm dev:desktop`, sees the app window with the web bundle and version badge, opens the Help menu and clicks the tray icon to hide and show the window. Under a minute after compile.

**Edge cases**

* GNOME without tray extension: app still runs; tray absence logged.
* Wayland placement limits documented.
* Missing `libwebkit2gtk-4.1`: dev script prints the install command.

**Dependencies**

PAP-13 (hard), PAP-17 (either order). Blocks children 2 and 3.

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor).

**Size**

M
